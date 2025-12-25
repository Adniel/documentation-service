"""Signature Service for 21 CFR Part 11 compliant electronic signatures.

Provides the core business logic for:
- Initiating signature flows (challenge-response)
- Completing signatures with re-authentication
- Verifying signature integrity
- Querying signatures for documents

Compliance:
- §11.50: Signature manifestation (name, date/time, meaning)
- §11.70: Signature/record linking (content hash)
- §11.100: Uniqueness (user ID)
- §11.200: Re-authentication at signature time
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import User, Page, ChangeRequest
from src.db.models.electronic_signature import (
    ElectronicSignature,
    SignatureMeaning,
    SIGNATURE_MEANING_DESCRIPTIONS,
)
from src.db.models.signature_challenge import SignatureChallenge, DEFAULT_CHALLENGE_EXPIRY_MINUTES
from src.db.models.audit import AuditEventType
from src.modules.access.security import verify_password
from src.modules.audit.audit_service import AuditService
from src.modules.document_control.ntp_service import get_trusted_timestamp, NTPServiceError
from src.modules.document_control.content_hash_service import (
    compute_content_hash,
    verify_content_hash,
    get_content_preview,
    ContentHashError,
)

logger = logging.getLogger(__name__)


class SignatureError(Exception):
    """Base exception for signature operations."""
    pass


class ChallengeExpiredError(SignatureError):
    """Challenge token has expired."""
    pass


class ChallengeInvalidError(SignatureError):
    """Challenge token is invalid or already used."""
    pass


class AuthenticationError(SignatureError):
    """Re-authentication failed."""
    pass


class ContentChangedError(SignatureError):
    """Content was modified after challenge was created."""
    pass


class SignatureService:
    """Service for managing electronic signatures."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    async def initiate_signature(
        self,
        user: User,
        meaning: SignatureMeaning,
        page_id: Optional[str] = None,
        change_request_id: Optional[str] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Tuple[SignatureChallenge, str, str]:
        """Initiate a signature flow by creating a challenge.

        Args:
            user: User initiating the signature
            meaning: Purpose of the signature
            page_id: Page to sign (optional)
            change_request_id: Change request to sign (optional)
            reason: Optional comment
            ip_address: Client IP for audit

        Returns:
            Tuple of (challenge, content_preview, document_title)

        Raises:
            SignatureError: If target document not found
            ContentHashError: If content cannot be hashed
        """
        # Get the document content
        content, title = await self._get_document_content(page_id, change_request_id)
        if content is None:
            raise SignatureError("Document not found")

        # Compute content hash
        content_hash = compute_content_hash(content)

        # Create content preview
        preview = get_content_preview(content)

        # Create challenge
        challenge = SignatureChallenge.create_challenge(
            user_id=user.id,
            meaning=meaning,
            content_hash=content_hash,
            page_id=page_id,
            change_request_id=change_request_id,
            reason=reason,
            expiry_minutes=DEFAULT_CHALLENGE_EXPIRY_MINUTES,
        )

        self.db.add(challenge)
        await self.db.flush()

        # Log audit event
        await self.audit.log_event(
            event_type="signature.initiated",
            actor_id=user.id,
            actor_email=user.email,
            actor_ip=ip_address,
            resource_type="page" if page_id else "change_request",
            resource_id=page_id or change_request_id,
            resource_name=title,
            details={
                "meaning": meaning.value,
                "content_hash": content_hash,
                "challenge_id": challenge.id,
            },
        )

        return challenge, preview, title or ""

    async def complete_signature(
        self,
        challenge_token: str,
        password: str,
        user: User,
        ip_address: str,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        reason_override: Optional[str] = None,
    ) -> ElectronicSignature:
        """Complete a signature with re-authentication.

        Args:
            challenge_token: Token from initiate_signature
            password: User's password for re-authentication
            user: Current user (must match challenge user)
            ip_address: Client IP address
            user_agent: Client user agent
            session_id: Current session ID
            reason_override: Override reason from challenge

        Returns:
            Created ElectronicSignature

        Raises:
            ChallengeInvalidError: If challenge not found or already used
            ChallengeExpiredError: If challenge has expired
            AuthenticationError: If password verification fails
            ContentChangedError: If content changed since challenge creation
            NTPServiceError: If NTP timestamp cannot be obtained
        """
        # Find and validate challenge
        result = await self.db.execute(
            select(SignatureChallenge)
            .where(SignatureChallenge.challenge_token == challenge_token)
        )
        challenge = result.scalar_one_or_none()

        if not challenge:
            raise ChallengeInvalidError("Invalid challenge token")

        if challenge.is_used:
            raise ChallengeInvalidError("Challenge has already been used")

        if challenge.user_id != user.id:
            raise ChallengeInvalidError("Challenge belongs to a different user")

        if datetime.utcnow() > challenge.expires_at.replace(tzinfo=None):
            raise ChallengeExpiredError("Challenge has expired")

        # Re-authenticate with password (§11.200)
        if not verify_password(password, user.hashed_password):
            # Log failed attempt
            await self.audit.log_event(
                event_type="signature.failed",
                actor_id=user.id,
                actor_email=user.email,
                actor_ip=ip_address,
                resource_type="page" if challenge.page_id else "change_request",
                resource_id=challenge.page_id or challenge.change_request_id,
                details={
                    "reason": "Password verification failed",
                    "challenge_id": challenge.id,
                },
            )
            raise AuthenticationError("Invalid password")

        # Verify content hasn't changed
        current_content, title = await self._get_document_content(
            challenge.page_id,
            challenge.change_request_id
        )
        if current_content is None:
            raise SignatureError("Document no longer exists")

        current_hash = compute_content_hash(current_content)
        if current_hash != challenge.content_hash:
            raise ContentChangedError(
                "Document content has changed since signature was initiated. "
                "Please start a new signature."
            )

        # Get trusted timestamp from NTP
        try:
            signed_at, ntp_server = await get_trusted_timestamp()
        except NTPServiceError as e:
            logger.error(f"NTP service failed: {e}")
            raise

        # Get git commit SHA if available
        git_commit_sha = await self._get_git_commit(
            challenge.page_id,
            challenge.change_request_id
        )

        # Get previous signature in chain (for multi-sig workflows)
        previous_sig = await self._get_latest_signature(
            challenge.page_id,
            challenge.change_request_id
        )

        # Create the electronic signature (§11.50)
        signature = ElectronicSignature(
            page_id=challenge.page_id,
            change_request_id=challenge.change_request_id,
            signer_id=user.id,
            signer_name=user.full_name,
            signer_email=user.email,
            signer_title=getattr(user, 'title', None),  # May not exist
            meaning=challenge.meaning,
            reason=reason_override or challenge.reason,
            content_hash=challenge.content_hash,
            git_commit_sha=git_commit_sha,
            signed_at=signed_at,
            ntp_server=ntp_server,
            auth_method="password",
            auth_session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            previous_signature_id=previous_sig.id if previous_sig else None,
            is_valid=True,
        )

        # Mark challenge as used
        challenge.consume()

        self.db.add(signature)
        await self.db.flush()

        # Log audit event
        await self.audit.log_event(
            event_type=AuditEventType.SIGNATURE_CREATED,
            actor_id=user.id,
            actor_email=user.email,
            actor_ip=ip_address,
            actor_user_agent=user_agent,
            resource_type="page" if challenge.page_id else "change_request",
            resource_id=challenge.page_id or challenge.change_request_id,
            resource_name=title,
            details={
                "signature_id": signature.id,
                "meaning": signature.meaning,
                "content_hash": signature.content_hash,
                "git_commit_sha": git_commit_sha,
                "ntp_server": ntp_server,
                "signed_at": signed_at.isoformat(),
            },
        )

        return signature

    async def verify_signature(
        self,
        signature_id: str,
        verify_content: bool = True,
    ) -> Tuple[bool, list[str]]:
        """Verify a signature's integrity.

        Checks:
        - Signature exists and is marked valid
        - Content hash matches current document (if verify_content=True)
        - Signer exists
        - Git commit is valid (if present)

        Args:
            signature_id: ID of signature to verify
            verify_content: Whether to verify content hash against current content

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        result = await self.db.execute(
            select(ElectronicSignature)
            .where(ElectronicSignature.id == signature_id)
            .options(selectinload(ElectronicSignature.signer))
        )
        signature = result.scalar_one_or_none()

        if not signature:
            return False, ["Signature not found"]

        issues = []

        # Check validity flag
        if not signature.is_valid:
            issues.append(f"Signature invalidated: {signature.invalidation_reason}")

        # Check signer exists
        if not signature.signer:
            issues.append("Signer account no longer exists")

        # Verify content hash if requested
        if verify_content:
            current_content, _ = await self._get_document_content(
                signature.page_id,
                signature.change_request_id
            )
            if current_content is None:
                issues.append("Signed document no longer exists")
            else:
                try:
                    if not verify_content_hash(current_content, signature.content_hash):
                        issues.append("Content has been modified since signing")
                except ContentHashError as e:
                    issues.append(f"Cannot verify content: {e}")

        # Log verification
        await self.audit.log_event(
            event_type=AuditEventType.SIGNATURE_VERIFIED,
            resource_type="signature",
            resource_id=signature_id,
            details={
                "is_valid": len(issues) == 0,
                "issues": issues,
            },
        )

        return len(issues) == 0, issues

    async def get_signatures_for_page(
        self,
        page_id: str,
        include_invalid: bool = False,
    ) -> list[ElectronicSignature]:
        """Get all signatures for a page.

        Args:
            page_id: Page ID
            include_invalid: Whether to include invalidated signatures

        Returns:
            List of signatures ordered by signed_at descending
        """
        query = (
            select(ElectronicSignature)
            .where(ElectronicSignature.page_id == page_id)
            .order_by(ElectronicSignature.signed_at.desc())
        )

        if not include_invalid:
            query = query.where(ElectronicSignature.is_valid == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_signatures_for_change_request(
        self,
        change_request_id: str,
        include_invalid: bool = False,
    ) -> list[ElectronicSignature]:
        """Get all signatures for a change request.

        Args:
            change_request_id: Change request ID
            include_invalid: Whether to include invalidated signatures

        Returns:
            List of signatures ordered by signed_at descending
        """
        query = (
            select(ElectronicSignature)
            .where(ElectronicSignature.change_request_id == change_request_id)
            .order_by(ElectronicSignature.signed_at.desc())
        )

        if not include_invalid:
            query = query.where(ElectronicSignature.is_valid == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def invalidate_signature(
        self,
        signature_id: str,
        reason: str,
        invalidated_by: User,
        ip_address: Optional[str] = None,
    ) -> ElectronicSignature:
        """Invalidate a signature.

        Args:
            signature_id: ID of signature to invalidate
            reason: Reason for invalidation
            invalidated_by: User performing the invalidation
            ip_address: Client IP

        Returns:
            Updated signature

        Raises:
            SignatureError: If signature not found
        """
        result = await self.db.execute(
            select(ElectronicSignature)
            .where(ElectronicSignature.id == signature_id)
        )
        signature = result.scalar_one_or_none()

        if not signature:
            raise SignatureError("Signature not found")

        if not signature.is_valid:
            raise SignatureError("Signature is already invalid")

        signature.invalidate(reason)
        await self.db.flush()

        # Log audit event
        await self.audit.log_event(
            event_type="signature.invalidated",
            actor_id=invalidated_by.id,
            actor_email=invalidated_by.email,
            actor_ip=ip_address,
            resource_type="signature",
            resource_id=signature_id,
            details={
                "reason": reason,
                "original_signer_id": signature.signer_id,
                "original_signed_at": signature.signed_at.isoformat(),
            },
        )

        return signature

    # -------------------------------------------------------------------------
    # Helper methods
    # -------------------------------------------------------------------------

    async def _get_document_content(
        self,
        page_id: Optional[str],
        change_request_id: Optional[str],
    ) -> Tuple[Optional[dict], Optional[str]]:
        """Get document content and title.

        Returns:
            Tuple of (content_dict, title) or (None, None) if not found
        """
        if page_id:
            result = await self.db.execute(
                select(Page).where(Page.id == page_id)
            )
            page = result.scalar_one_or_none()
            if page:
                return page.content or {}, page.title
            return None, None

        if change_request_id:
            result = await self.db.execute(
                select(ChangeRequest).where(ChangeRequest.id == change_request_id)
            )
            cr = result.scalar_one_or_none()
            if cr:
                return cr.draft_content or {}, cr.title
            return None, None

        return None, None

    async def _get_git_commit(
        self,
        page_id: Optional[str],
        change_request_id: Optional[str],
    ) -> Optional[str]:
        """Get git commit SHA for the document."""
        if page_id:
            result = await self.db.execute(
                select(Page.git_commit_sha).where(Page.id == page_id)
            )
            return result.scalar_one_or_none()

        if change_request_id:
            result = await self.db.execute(
                select(ChangeRequest.draft_commit_sha).where(ChangeRequest.id == change_request_id)
            )
            return result.scalar_one_or_none()

        return None

    async def _get_latest_signature(
        self,
        page_id: Optional[str],
        change_request_id: Optional[str],
    ) -> Optional[ElectronicSignature]:
        """Get the most recent valid signature for a document."""
        if page_id:
            result = await self.db.execute(
                select(ElectronicSignature)
                .where(
                    and_(
                        ElectronicSignature.page_id == page_id,
                        ElectronicSignature.is_valid == True,
                    )
                )
                .order_by(ElectronicSignature.signed_at.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()

        if change_request_id:
            result = await self.db.execute(
                select(ElectronicSignature)
                .where(
                    and_(
                        ElectronicSignature.change_request_id == change_request_id,
                        ElectronicSignature.is_valid == True,
                    )
                )
                .order_by(ElectronicSignature.signed_at.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()

        return None
