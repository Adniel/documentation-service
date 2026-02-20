"""SiteVisitor model for external users accessing published sites.

Sprint D: Integrated Access Control

External users (not in the main user database) who are invited to access
published sites via email invitation and magic link authentication.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.site_visitor_role import SiteVisitorRole
    from src.db.models.user import User


class SiteVisitor(Base, UUIDMixin, TimestampMixin):
    """External user with access to published sites.

    External visitors authenticate via:
    1. Magic link (passwordless email login)
    2. Password (optional, if they set one)
    3. SSO bridge (if they have an internal user account)

    Visitors get access to specific sites via SiteVisitorRole assignments.
    """

    __tablename__ = "site_visitors"

    # === EMAIL-BASED IDENTITY ===
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # === AUTHENTICATION ===
    # Optional password (can use magic link instead)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Magic link for passwordless login
    magic_link_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    magic_link_expires: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # === PROFILE ===
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # === STATUS ===
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # === SSO BRIDGE ===
    # Link to internal user if this visitor also has an internal account
    # This enables SSO - if an internal user accesses a published site,
    # they can be matched to their visitor profile
    internal_user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # === RELATIONSHIPS ===
    internal_user: Mapped["User | None"] = relationship(
        "User", foreign_keys=[internal_user_id]
    )
    roles: Mapped[list["SiteVisitorRole"]] = relationship(
        "SiteVisitorRole",
        back_populates="visitor",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<SiteVisitor {self.email}>"

    @property
    def display(self) -> str:
        """Get display name or email."""
        return self.display_name or self.email

    def is_magic_link_valid(self) -> bool:
        """Check if magic link token is valid."""
        if not self.magic_link_token or not self.magic_link_expires:
            return False
        return datetime.now(self.magic_link_expires.tzinfo) < self.magic_link_expires
