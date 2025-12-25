"""Session model for Sprint 5 Access Control.

Implements session management with configurable timeout for 21 CFR Part 11 compliance.
Default timeout: 30 minutes of inactivity.

Compliance: 21 CFR §11.10(d) - Limiting system access to authorized individuals
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.db.models.user import User


# Default session timeout in minutes
DEFAULT_SESSION_TIMEOUT_MINUTES = 30


class Session(Base, UUIDMixin, TimestampMixin):
    """User session for tracking activity and enforcing timeout.

    Sessions are created on login and updated on each authenticated request.
    Sessions expire after a configurable period of inactivity.

    Attributes:
        user_id: User who owns the session
        token_jti: JWT token ID (jti claim) for token invalidation
        ip_address: IP address of the client
        user_agent: Browser/client user agent string
        last_activity: Timestamp of last activity (updated on each request)
        expires_at: When the session expires
        is_active: Whether the session is active
        revoked_at: When the session was explicitly revoked (logout)
        revoked_reason: Reason for revocation
    """

    __tablename__ = "sessions"

    # Session ownership
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Token identification
    token_jti: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # Client information
    ip_address: Mapped[str | None] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Activity tracking
    last_activity: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )

    # Session status
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    revoked_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="sessions",
        lazy="joined",
    )

    __table_args__ = (
        Index("ix_session_user_active", "user_id", "is_active"),
        Index("ix_session_expires", "expires_at"),
    )

    @classmethod
    def create_session(
        cls,
        user_id: str,
        token_jti: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        timeout_minutes: int = DEFAULT_SESSION_TIMEOUT_MINUTES,
    ) -> "Session":
        """Create a new session."""
        now = datetime.utcnow()
        return cls(
            user_id=user_id,
            token_jti=token_jti,
            ip_address=ip_address,
            user_agent=user_agent,
            last_activity=now,
            expires_at=now + timedelta(minutes=timeout_minutes),
            is_active=True,
        )

    def is_valid(self) -> bool:
        """Check if session is still valid."""
        if not self.is_active:
            return False
        if self.revoked_at is not None:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        return True

    def refresh(self, timeout_minutes: int = DEFAULT_SESSION_TIMEOUT_MINUTES) -> None:
        """Refresh session expiry on activity."""
        now = datetime.utcnow()
        self.last_activity = now
        self.expires_at = now + timedelta(minutes=timeout_minutes)

    def revoke(self, reason: str = "User logout") -> None:
        """Revoke the session."""
        self.is_active = False
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason

    @property
    def time_remaining_seconds(self) -> int:
        """Get seconds until session expires."""
        remaining = self.expires_at - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))

    def __repr__(self) -> str:
        return (
            f"Session(user_id={self.user_id}, "
            f"active={self.is_active}, "
            f"expires_at={self.expires_at})"
        )
