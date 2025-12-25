"""Signature Challenge model for re-authentication flow.

Implements short-lived challenge tokens for 21 CFR Part 11 §11.200 compliance.
Users must re-authenticate (enter password) when signing documents.

Challenge tokens:
- Are valid for 5 minutes (configurable)
- Can only be used once
- Store context about what will be signed
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import secrets

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin
from src.db.models.electronic_signature import SignatureMeaning

if TYPE_CHECKING:
    from src.db.models.change_request import ChangeRequest
    from src.db.models.page import Page
    from src.db.models.user import User


# Default challenge expiration in minutes
DEFAULT_CHALLENGE_EXPIRY_MINUTES = 5


class SignatureChallenge(Base, UUIDMixin, TimestampMixin):
    """Short-lived challenge token for signature re-authentication.

    When a user initiates a signature, a challenge is created containing:
    - What will be signed (page or change request)
    - The intended meaning of the signature
    - A secure random token
    - An expiration time

    The user must then re-authenticate (provide password) and submit
    the challenge token to complete the signature. This ensures:
    - The person signing is the account owner (§11.200)
    - The signature intent is captured before authentication
    - Signatures cannot be created without recent verification

    Attributes:
        user_id: User who initiated the challenge
        page_id: Page to be signed (if any)
        change_request_id: Change request to be signed (if any)
        meaning: Intended signature meaning
        reason: Optional comment to include with signature
        challenge_token: Secure random token (64 hex chars)
        expires_at: When this challenge expires
        is_used: Whether the challenge has been consumed
        used_at: When the challenge was used
        content_hash: Pre-computed hash of content at challenge time
    """

    __tablename__ = "signature_challenges"

    # Who is signing
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # What will be signed (one of these must be set)
    page_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=True,
    )

    change_request_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("change_requests.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Signature intent
    meaning: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        String(1000),  # Shorter than full Text for challenges
        nullable=True,
    )

    # Pre-computed content hash (ensures content doesn't change between
    # challenge creation and signature completion)
    content_hash: Mapped[str] = mapped_column(
        String(64),  # SHA-256 hex
        nullable=False,
    )

    # Challenge token (cryptographically random)
    challenge_token: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    # Expiration
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Usage tracking
    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="joined",
    )

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

    __table_args__ = (
        Index("ix_sigchallenge_user_active", "user_id", "is_used", "expires_at"),
    )

    @classmethod
    def create_challenge(
        cls,
        user_id: str,
        meaning: SignatureMeaning,
        content_hash: str,
        page_id: str | None = None,
        change_request_id: str | None = None,
        reason: str | None = None,
        expiry_minutes: int = DEFAULT_CHALLENGE_EXPIRY_MINUTES,
    ) -> "SignatureChallenge":
        """Create a new signature challenge.

        Args:
            user_id: User initiating the signature
            meaning: Purpose of the signature
            content_hash: SHA-256 hash of content being signed
            page_id: Page to sign (optional)
            change_request_id: Change request to sign (optional)
            reason: Optional comment for the signature
            expiry_minutes: How long until challenge expires

        Returns:
            New SignatureChallenge instance

        Raises:
            ValueError: If neither page_id nor change_request_id provided
        """
        if not page_id and not change_request_id:
            raise ValueError("Must provide either page_id or change_request_id")

        now = datetime.utcnow()
        return cls(
            user_id=user_id,
            page_id=page_id,
            change_request_id=change_request_id,
            meaning=meaning.value if isinstance(meaning, SignatureMeaning) else meaning,
            reason=reason,
            content_hash=content_hash,
            challenge_token=secrets.token_hex(32),  # 64 hex chars
            expires_at=now + timedelta(minutes=expiry_minutes),
            is_used=False,
        )

    def is_valid(self) -> bool:
        """Check if this challenge can still be used."""
        if self.is_used:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        return True

    def consume(self) -> None:
        """Mark this challenge as used."""
        self.is_used = True
        self.used_at = datetime.utcnow()

    @property
    def meaning_enum(self) -> SignatureMeaning:
        """Get meaning as enum."""
        return SignatureMeaning(self.meaning)

    @property
    def seconds_remaining(self) -> int:
        """Get seconds until this challenge expires."""
        remaining = self.expires_at - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))

    def __repr__(self) -> str:
        status = "used" if self.is_used else ("expired" if not self.is_valid() else "active")
        return (
            f"<SignatureChallenge "
            f"user={self.user_id[:8]}... "
            f"meaning={self.meaning} "
            f"status={status}>"
        )
