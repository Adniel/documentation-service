"""GitCredential model - Encrypted storage for Git remote credentials.

Sprint 13: Git Remote Support
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.organization import Organization
    from src.db.models.user import User


class CredentialType(str, Enum):
    """Types of Git credentials supported."""

    SSH_KEY = "ssh_key"
    HTTPS_TOKEN = "https_token"
    DEPLOY_KEY = "deploy_key"


class GitCredential(Base, UUIDMixin, TimestampMixin):
    """Encrypted Git credentials for remote repository access.

    Credentials are AES-256 encrypted at rest. One credential per organization.
    """

    __tablename__ = "git_credentials"

    # Organization this credential belongs to (one-to-one)
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Credential type
    credential_type: Mapped[CredentialType] = mapped_column(
        SqlEnum(CredentialType, name="credential_type_enum"),
        nullable=False,
    )

    # Encrypted credential value (AES-256)
    encrypted_value: Mapped[str] = mapped_column(Text, nullable=False)

    # Encryption IV (initialization vector) for AES
    encryption_iv: Mapped[str] = mapped_column(String(32), nullable=False)

    # SSH key fingerprint (for display, not secret)
    key_fingerprint: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Optional expiration
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Audit: who created this credential
    created_by_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False
    )

    # Label for display (e.g., "GitHub Deploy Key")
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<GitCredential org={self.organization_id} type={self.credential_type.value}>"

    @property
    def is_expired(self) -> bool:
        """Check if credential has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(self.expires_at.tzinfo) > self.expires_at
