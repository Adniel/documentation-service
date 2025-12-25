"""Electronic Signatures API endpoints for 21 CFR Part 11 compliance.

Provides endpoints for:
- Initiating signature flows (challenge-response)
- Completing signatures with re-authentication
- Verifying signature integrity
- Listing signatures on documents
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status

from src.api.deps import DbSession, CurrentUser
from src.db.models.electronic_signature import SIGNATURE_MEANING_DESCRIPTIONS
from src.modules.document_control.signature_service import (
    SignatureService,
    SignatureError,
    ChallengeExpiredError,
    ChallengeInvalidError,
    AuthenticationError,
    ContentChangedError,
)
from src.modules.document_control.ntp_service import NTPServiceError
from src.modules.document_control.signature_schemas import (
    InitiateSignatureRequest,
    InitiateSignatureResponse,
    CompleteSignatureRequest,
    ElectronicSignatureResponse,
    SignatureVerificationResponse,
    SignatureListResponse,
    InvalidateSignatureRequest,
)

router = APIRouter()


def get_client_ip(request: Request) -> str:
    """Get client IP from request, handling proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post(
    "/signatures/initiate",
    response_model=InitiateSignatureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate signature flow",
    description="""
    Start an electronic signature flow by creating a challenge.

    The returned challenge token must be used within 5 minutes to complete
    the signature with re-authentication.

    21 CFR Part 11: This implements the first step of the signature process.
    """,
)
async def initiate_signature(
    request_body: InitiateSignatureRequest,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> InitiateSignatureResponse:
    """Initiate a signature flow."""
    service = SignatureService(db)
    ip_address = get_client_ip(request)

    try:
        challenge, preview, title = await service.initiate_signature(
            user=current_user,
            meaning=request_body.meaning,
            page_id=request_body.page_id,
            change_request_id=request_body.change_request_id,
            reason=request_body.reason,
            ip_address=ip_address,
        )

        await db.commit()

        return InitiateSignatureResponse(
            challenge_token=challenge.challenge_token,
            expires_at=challenge.expires_at,
            expires_in_seconds=challenge.seconds_remaining,
            content_preview=preview,
            content_hash=challenge.content_hash,
            meaning=challenge.meaning_enum,
            meaning_description=SIGNATURE_MEANING_DESCRIPTIONS.get(
                challenge.meaning_enum, challenge.meaning
            ),
            document_title=title,
        )

    except SignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/signatures/complete",
    response_model=ElectronicSignatureResponse,
    summary="Complete signature with re-authentication",
    description="""
    Complete an electronic signature by providing password for re-authentication.

    21 CFR Part 11 §11.200: This implements re-authentication at signature time.
    The signature captures:
    - Signer identity (frozen at signature time) per §11.50
    - NTP-sourced timestamp per §11.50
    - Content hash for integrity per §11.70
    """,
)
async def complete_signature(
    request_body: CompleteSignatureRequest,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> ElectronicSignatureResponse:
    """Complete a signature with re-authentication."""
    service = SignatureService(db)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")

    try:
        signature = await service.complete_signature(
            challenge_token=request_body.challenge_token,
            password=request_body.password,
            user=current_user,
            ip_address=ip_address,
            user_agent=user_agent,
            reason_override=request_body.reason,
        )

        await db.commit()

        return ElectronicSignatureResponse.from_db(signature)

    except ChallengeExpiredError:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Signature challenge has expired. Please initiate a new signature.",
        )
    except ChallengeInvalidError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password. Re-authentication failed.",
        )
    except ContentChangedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except NTPServiceError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to obtain trusted timestamp. Please try again.",
        )
    except SignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/signatures/{signature_id}",
    response_model=ElectronicSignatureResponse,
    summary="Get signature details",
)
async def get_signature(
    signature_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> ElectronicSignatureResponse:
    """Get details of a specific signature."""
    from sqlalchemy import select
    from src.db.models.electronic_signature import ElectronicSignature

    result = await db.execute(
        select(ElectronicSignature).where(ElectronicSignature.id == signature_id)
    )
    signature = result.scalar_one_or_none()

    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signature not found",
        )

    return ElectronicSignatureResponse.from_db(signature)


@router.get(
    "/signatures/{signature_id}/verify",
    response_model=SignatureVerificationResponse,
    summary="Verify signature integrity",
    description="""
    Verify that a signature is valid and content hasn't been modified.

    Checks:
    - Signature exists and is marked valid
    - Content hash matches current document
    - Signer account exists
    """,
)
async def verify_signature(
    signature_id: str,
    db: DbSession,
    verify_content: bool = True,
) -> SignatureVerificationResponse:
    """Verify signature integrity."""
    from sqlalchemy import select
    from src.db.models.electronic_signature import ElectronicSignature

    # Get signature first
    result = await db.execute(
        select(ElectronicSignature).where(ElectronicSignature.id == signature_id)
    )
    signature = result.scalar_one_or_none()

    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signature not found",
        )

    service = SignatureService(db)
    is_valid, issues = await service.verify_signature(
        signature_id=signature_id,
        verify_content=verify_content,
    )

    return SignatureVerificationResponse(
        signature_id=signature_id,
        is_valid=is_valid and signature.is_valid,
        signer_name=signature.signer_name,
        signer_email=signature.signer_email,
        meaning=signature.meaning_enum,
        meaning_description=SIGNATURE_MEANING_DESCRIPTIONS.get(
            signature.meaning_enum, signature.meaning
        ),
        signed_at=signature.signed_at,
        ntp_server=signature.ntp_server,
        content_hash_matches="Content has been modified since signing" not in issues,
        git_commit_verified=signature.git_commit_sha is not None,
        verification_timestamp=datetime.now(timezone.utc),
        issues=issues,
    )


@router.post(
    "/signatures/{signature_id}/invalidate",
    response_model=ElectronicSignatureResponse,
    summary="Invalidate a signature",
    description="Mark a signature as invalid with a reason. This is an irreversible action.",
)
async def invalidate_signature(
    signature_id: str,
    request_body: InvalidateSignatureRequest,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> ElectronicSignatureResponse:
    """Invalidate an existing signature."""
    service = SignatureService(db)
    ip_address = get_client_ip(request)

    try:
        signature = await service.invalidate_signature(
            signature_id=signature_id,
            reason=request_body.reason,
            invalidated_by=current_user,
            ip_address=ip_address,
        )

        await db.commit()

        return ElectronicSignatureResponse.from_db(signature)

    except SignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/pages/{page_id}/signatures",
    response_model=SignatureListResponse,
    summary="List signatures on a page",
)
async def list_page_signatures(
    page_id: str,
    db: DbSession,
    current_user: CurrentUser,
    include_invalid: bool = False,
) -> SignatureListResponse:
    """Get all signatures for a page."""
    service = SignatureService(db)

    signatures = await service.get_signatures_for_page(
        page_id=page_id,
        include_invalid=include_invalid,
    )

    return SignatureListResponse(
        signatures=[ElectronicSignatureResponse.from_db(s) for s in signatures],
        total=len(signatures),
        has_valid_signatures=any(s.is_valid for s in signatures),
    )


@router.get(
    "/change-requests/{change_request_id}/signatures",
    response_model=SignatureListResponse,
    summary="List signatures on a change request",
)
async def list_change_request_signatures(
    change_request_id: str,
    db: DbSession,
    current_user: CurrentUser,
    include_invalid: bool = False,
) -> SignatureListResponse:
    """Get all signatures for a change request."""
    service = SignatureService(db)

    signatures = await service.get_signatures_for_change_request(
        change_request_id=change_request_id,
        include_invalid=include_invalid,
    )

    return SignatureListResponse(
        signatures=[ElectronicSignatureResponse.from_db(s) for s in signatures],
        total=len(signatures),
        has_valid_signatures=any(s.is_valid for s in signatures),
    )
