"""Pydantic schemas for electronic signature operations.

These schemas define the request/response formats for the signature API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.db.models.electronic_signature import SignatureMeaning, SIGNATURE_MEANING_DESCRIPTIONS


# -----------------------------------------------------------------------------
# Request Schemas
# -----------------------------------------------------------------------------

class InitiateSignatureRequest(BaseModel):
    """Request to initiate a signature flow."""

    page_id: Optional[str] = Field(
        None,
        description="ID of page to sign (mutually exclusive with change_request_id)"
    )
    change_request_id: Optional[str] = Field(
        None,
        description="ID of change request to sign (mutually exclusive with page_id)"
    )
    meaning: SignatureMeaning = Field(
        ...,
        description="The meaning/intent of this signature"
    )
    reason: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional reason or comment for the signature"
    )

    def model_post_init(self, __context) -> None:
        """Validate that exactly one target is specified."""
        if not self.page_id and not self.change_request_id:
            raise ValueError("Either page_id or change_request_id must be provided")
        if self.page_id and self.change_request_id:
            raise ValueError("Cannot specify both page_id and change_request_id")


class CompleteSignatureRequest(BaseModel):
    """Request to complete a signature with re-authentication."""

    challenge_token: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="The challenge token from initiate_signature"
    )
    password: str = Field(
        ...,
        min_length=1,
        description="User's password for re-authentication"
    )
    reason: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional additional comment (overrides reason from initiate)"
    )


class InvalidateSignatureRequest(BaseModel):
    """Request to invalidate an existing signature."""

    reason: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Reason for invalidating the signature"
    )


# -----------------------------------------------------------------------------
# Response Schemas
# -----------------------------------------------------------------------------

class InitiateSignatureResponse(BaseModel):
    """Response from initiating a signature flow."""

    challenge_token: str = Field(
        ...,
        description="Token to use when completing the signature"
    )
    expires_at: datetime = Field(
        ...,
        description="When this challenge expires"
    )
    expires_in_seconds: int = Field(
        ...,
        description="Seconds until expiration"
    )
    content_preview: str = Field(
        ...,
        description="Preview of content being signed"
    )
    content_hash: str = Field(
        ...,
        description="SHA-256 hash of content being signed"
    )
    meaning: SignatureMeaning = Field(
        ...,
        description="The signature meaning"
    )
    meaning_description: str = Field(
        ...,
        description="Human-readable meaning description"
    )
    document_title: Optional[str] = Field(
        None,
        description="Title of document being signed"
    )

    class Config:
        from_attributes = True


class ElectronicSignatureResponse(BaseModel):
    """Response containing signature details."""

    id: str
    page_id: Optional[str] = None
    change_request_id: Optional[str] = None

    # Signer info (frozen at signature time)
    signer_id: str
    signer_name: str
    signer_email: str
    signer_title: Optional[str] = None

    # Signature details
    meaning: SignatureMeaning
    meaning_description: str
    reason: Optional[str] = None

    # Integrity
    content_hash: str
    git_commit_sha: Optional[str] = None

    # Timestamp
    signed_at: datetime
    ntp_server: str

    # Validity
    is_valid: bool
    invalidated_at: Optional[datetime] = None
    invalidation_reason: Optional[str] = None

    # Audit
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_db(cls, sig) -> "ElectronicSignatureResponse":
        """Create from database model."""
        return cls(
            id=sig.id,
            page_id=sig.page_id,
            change_request_id=sig.change_request_id,
            signer_id=sig.signer_id,
            signer_name=sig.signer_name,
            signer_email=sig.signer_email,
            signer_title=sig.signer_title,
            meaning=SignatureMeaning(sig.meaning),
            meaning_description=SIGNATURE_MEANING_DESCRIPTIONS.get(
                SignatureMeaning(sig.meaning), sig.meaning
            ),
            reason=sig.reason,
            content_hash=sig.content_hash,
            git_commit_sha=sig.git_commit_sha,
            signed_at=sig.signed_at,
            ntp_server=sig.ntp_server,
            is_valid=sig.is_valid,
            invalidated_at=sig.invalidated_at,
            invalidation_reason=sig.invalidation_reason,
            created_at=sig.created_at,
        )


class SignatureVerificationResponse(BaseModel):
    """Response from signature verification."""

    signature_id: str
    is_valid: bool = Field(
        ...,
        description="Whether the signature is currently valid"
    )

    # Signer info
    signer_name: str
    signer_email: str
    meaning: SignatureMeaning
    meaning_description: str

    # Timestamp
    signed_at: datetime
    ntp_server: str

    # Integrity checks
    content_hash_matches: bool = Field(
        ...,
        description="Whether content hash matches current document"
    )
    git_commit_verified: bool = Field(
        ...,
        description="Whether git commit SHA is valid"
    )

    # Verification metadata
    verification_timestamp: datetime
    issues: list[str] = Field(
        default_factory=list,
        description="List of any issues found during verification"
    )


class SignatureListResponse(BaseModel):
    """Response containing list of signatures."""

    signatures: list[ElectronicSignatureResponse]
    total: int
    has_valid_signatures: bool = Field(
        ...,
        description="Whether there is at least one valid signature"
    )
