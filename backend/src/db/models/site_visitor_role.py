"""SiteVisitorRole model for per-site access grants to external visitors.

Sprint D: Integrated Access Control

Assigns roles and clearance levels to external visitors for specific published sites.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.published_site import PublishedSite
    from src.db.models.site_visitor import SiteVisitor
    from src.db.models.user import User


class SiteVisitorRole(Base, UUIDMixin, TimestampMixin):
    """Role assignment for external visitors on a specific published site.

    Each visitor can have one role per site. The role determines:
    - clearance_level: What classification level documents they can access (0-3)
    - role_name: Human-readable role name for display
    - allowed_page_ids: Optional explicit page access list (overrides clearance)

    Clearance levels:
    - 0: public only (default for new visitors)
    - 1: public + internal
    - 2: public + internal + confidential
    - 3: all (including restricted)
    """

    __tablename__ = "site_visitor_roles"

    # === VISITOR REFERENCE ===
    visitor_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("site_visitors.id", ondelete="CASCADE"),
        nullable=False,
    )

    # === SITE REFERENCE ===
    site_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("published_sites.id", ondelete="CASCADE"),
        nullable=False,
    )

    # === ROLE AND CLEARANCE ===
    role_name: Mapped[str] = mapped_column(
        String(100), default="visitor", nullable=False
    )
    # Clearance level (0-3): determines what classification level docs they can see
    # 0 = public only (default), 1 = internal, 2 = confidential, 3 = restricted
    clearance_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # === EXPLICIT PAGE ACCESS ===
    # Optional: explicitly allow access to specific pages regardless of clearance
    # JSON array of page IDs
    allowed_page_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # === INVITATION TRACKING ===
    invited_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # === EXPIRATION ===
    # Optional: role expires after this date
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # === RELATIONSHIPS ===
    visitor: Mapped["SiteVisitor"] = relationship(
        "SiteVisitor", back_populates="roles"
    )
    site: Mapped["PublishedSite"] = relationship("PublishedSite")
    invited_by: Mapped["User | None"] = relationship("User")

    __table_args__ = (
        # One role per visitor per site
        UniqueConstraint("visitor_id", "site_id", name="uq_visitor_site_role"),
    )

    def __repr__(self) -> str:
        return f"<SiteVisitorRole visitor={self.visitor_id} site={self.site_id} role={self.role_name}>"

    def is_valid(self) -> bool:
        """Check if role is currently valid (not expired)."""
        if not self.expires_at:
            return True
        return datetime.now(self.expires_at.tzinfo) < self.expires_at

    def has_explicit_access(self, page_id: str) -> bool:
        """Check if visitor has explicit access to a page."""
        if not self.allowed_page_ids:
            return False
        return page_id in self.allowed_page_ids
