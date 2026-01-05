"""ServiceAccount models for MCP integration.

Sprint C: MCP Integration
- ServiceAccount: API access credentials for external integrations
- ServiceAccountUsage: Usage tracking for audit and rate limiting
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.organization import Organization
    from src.db.models.user import User


class ServiceAccount(Base, UUIDMixin, TimestampMixin):
    """Service account for API access.

    Service accounts enable external integrations and AI agents to access
    the documentation platform via API keys. Each account has configurable
    permissions, rate limits, and IP restrictions.
    """

    __tablename__ = "service_accounts"

    # Organization this service account belongs to
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Display name and description
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Authentication - API key is hashed, prefix stored for identification
    api_key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    api_key_prefix: Mapped[str] = mapped_column(String(12), nullable=False, index=True)

    # Permissions
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="viewer")
    allowed_spaces: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    allowed_operations: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    # Security settings
    ip_allowlist: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    rate_limit_per_minute: Mapped[int] = mapped_column(
        Integer, nullable=False, default=60
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Audit: who created this service account
    created_by_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User")
    usage_records: Mapped[list["ServiceAccountUsage"]] = relationship(
        "ServiceAccountUsage",
        back_populates="service_account",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ServiceAccount name={self.name} org={self.organization_id}>"

    @property
    def is_expired(self) -> bool:
        """Check if service account has expired."""
        if self.expires_at is None:
            return False
        from datetime import timezone as tz
        return datetime.now(tz.utc) > self.expires_at


class ServiceAccountUsage(Base, UUIDMixin):
    """Usage tracking for service accounts.

    Records each API request made by a service account for:
    - Audit trail
    - Usage statistics
    - Rate limiting verification
    """

    __tablename__ = "service_account_usage"

    # Service account that made the request
    service_account_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("service_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Request timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Operation performed (e.g., "search_documents", "get_document")
    operation: Mapped[str] = mapped_column(String(100), nullable=False)

    # Resource accessed (optional)
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )

    # Request metadata
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    response_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    service_account: Mapped["ServiceAccount"] = relationship(
        "ServiceAccount",
        back_populates="usage_records",
    )

    def __repr__(self) -> str:
        return f"<ServiceAccountUsage op={self.operation} code={self.response_code}>"
