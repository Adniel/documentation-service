"""Electronic Signature model for 21 CFR Part 11 compliance.

Implements legally-binding electronic signatures with:
- §11.50: Signature manifestation (name, date/time, meaning)
- §11.70: Signature/record linking (content hash + git commit)
- §11.100: Uniqueness (user ID + non-reusable tokens)
- §11.200: Re-authentication evidence
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.change_request import ChangeRequest
    from src.db.models.page import Page
    from src.db.models.session import Session
    from src.db.models.user import User


class SignatureMeaning(str, Enum):
    """Meaning of the electronic signature per 21 CFR §11.50.

    Each signature must capture the meaning or intent of the signer.
    """

    AUTHORED = "authored"           # Created or wrote this content
    REVIEWED = "reviewed"           # Reviewed for accuracy/completeness
    APPROVED = "approved"           # Approved for release/use
    WITNESSED = "witnessed"         # Witnessed another signature
    ACKNOWLEDGED = "acknowledged"   # Read and understood the content


# Human-readable descriptions for each meaning
SIGNATURE_MEANING_DESCRIPTIONS = {
    SignatureMeaning.AUTHORED: "I authored this document and certify its accuracy.",
    SignatureMeaning.REVIEWED: "I have reviewed this document for accuracy and completeness.",
    SignatureMeaning.APPROVED: "I approve this document for release and use.",
    SignatureMeaning.WITNESSED: "I witnessed the signing of this document.",
    SignatureMeaning.ACKNOWLEDGED: "I have read and understood this document.",
}


class ElectronicSignature(Base, UUIDMixin, TimestampMixin):
    """21 CFR Part 11 compliant electronic signature.

    Captures all required elements for legal validity:
    - Signer identity (frozen at signature time)
    - Signature meaning/intent
    - Trusted timestamp from NTP source
    - Content hash for integrity verification
    - Re-authentication evidence
    - Linkage to source document and git commit

    Attributes:
        page_id: Page being signed (if signing a page directly)
        change_request_id: Change request being signed (if signing a CR)
        signer_id: User who created the signature
        signer_name: Frozen copy of signer's name at signature time
        signer_email: Frozen copy of signer's email at signature time
        signer_title: Frozen copy of signer's job title at signature time
        meaning: Purpose/intent of the signature
        reason: Optional comment explaining the signature
        content_hash: SHA-256 hash of signed content for integrity
        git_commit_sha: Git commit this signature is linked to
        signed_at: NTP-sourced timestamp when signature was created
        ntp_server: Which NTP server provided the timestamp
        auth_method: How re-authentication was performed
        auth_session_id: Session used for re-authentication
        ip_address: IP address of signer
        user_agent: Browser/client user agent
        previous_signature_id: Link to prior signature in chain
        is_valid: Whether signature is still valid
        invalidated_at: When signature was invalidated
        invalidation_reason: Why signature was invalidated
    """

    __tablename__ = "electronic_signatures"

    # What was signed (one of these must be set)
    page_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("pages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    change_request_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("change_requests.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Who signed - FROZEN at signature time (§11.50)
    # These fields capture the signer's identity at the moment of signing,
    # even if their account details change later
    signer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )

    signer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    signer_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    signer_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Signature meaning (§11.50)
    meaning: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Content integrity (§11.70)
    content_hash: Mapped[str] = mapped_column(
        String(64),  # SHA-256 hex = 64 chars
        nullable=False,
    )

    git_commit_sha: Mapped[str | None] = mapped_column(
        String(40),  # Git SHA = 40 chars
        nullable=True,
    )

    # Trusted timestamp (§11.50)
    signed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ntp_server: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Re-authentication evidence (§11.200)
    auth_method: Mapped[str] = mapped_column(
        String(50),  # "password", "mfa", "biometric"
        nullable=False,
    )

    auth_session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True,
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),  # IPv6 max length
        nullable=False,
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )

    # Signature chain for multi-signature workflows
    previous_signature_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("electronic_signatures.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Validity tracking
    is_valid: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    invalidated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    invalidation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    page: Mapped["Page | None"] = relationship(
        "Page",
        foreign_keys=[page_id],
        lazy="joined",
    )

    change_request: Mapped["ChangeRequest | None"] = relationship(
        "ChangeRequest",
        foreign_keys=[change_request_id],
        lazy="joined",
    )

    signer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[signer_id],
        lazy="joined",
    )

    auth_session: Mapped["Session | None"] = relationship(
        "Session",
        foreign_keys=[auth_session_id],
        lazy="joined",
    )

    previous_signature: Mapped["ElectronicSignature | None"] = relationship(
        "ElectronicSignature",
        remote_side="ElectronicSignature.id",
        foreign_keys=[previous_signature_id],
        lazy="select",
    )

    __table_args__ = (
        Index("ix_esig_page_valid", "page_id", "is_valid"),
        Index("ix_esig_cr_valid", "change_request_id", "is_valid"),
        Index("ix_esig_signer_time", "signer_id", "signed_at"),
    )

    @property
    def meaning_enum(self) -> SignatureMeaning:
        """Get meaning as enum."""
        return SignatureMeaning(self.meaning)

    @property
    def meaning_description(self) -> str:
        """Get human-readable meaning description."""
        return SIGNATURE_MEANING_DESCRIPTIONS.get(
            self.meaning_enum,
            f"Unknown meaning: {self.meaning}"
        )

    def invalidate(self, reason: str) -> None:
        """Invalidate this signature with a reason."""
        self.is_valid = False
        self.invalidated_at = datetime.utcnow()
        self.invalidation_reason = reason

    def __repr__(self) -> str:
        return (
            f"<ElectronicSignature "
            f"signer={self.signer_email} "
            f"meaning={self.meaning} "
            f"valid={self.is_valid}>"
        )
