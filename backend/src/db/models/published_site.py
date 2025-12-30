"""PublishedSite model for documentation publishing.

Sprint A: Publishing
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.organization import Organization
    from src.db.models.space import Space
    from src.db.models.theme import Theme
    from src.db.models.user import User


class SiteStatus(str, Enum):
    """Published site status."""

    DRAFT = "draft"  # Not yet published
    PUBLISHED = "published"  # Live and accessible
    MAINTENANCE = "maintenance"  # Temporarily unavailable
    ARCHIVED = "archived"  # No longer active


class SiteVisibility(str, Enum):
    """Site visibility/access control."""

    PUBLIC = "public"  # Anyone can access
    AUTHENTICATED = "authenticated"  # Logged-in users only
    RESTRICTED = "restricted"  # Specific users/domains only


class PublishedSite(Base, UUIDMixin, TimestampMixin):
    """Published documentation site configuration."""

    __tablename__ = "published_sites"

    # Content source
    space_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("spaces.id", ondelete="CASCADE"),
        unique=True,  # One site per space
        nullable=False,
    )
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Site identity
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    custom_domain: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    custom_domain_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Site metadata (SEO)
    site_title: Mapped[str] = mapped_column(String(255), nullable=False)
    site_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    og_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    favicon_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Theme
    theme_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("themes.id", ondelete="SET NULL"), nullable=True
    )
    custom_css: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Visibility and access
    visibility: Mapped[str] = mapped_column(
        String(20), default=SiteVisibility.AUTHENTICATED.value, nullable=False
    )
    allowed_email_domains: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )  # For restricted visibility (JSON list of domain strings)

    # Publishing state
    status: Mapped[str] = mapped_column(
        String(20), default=SiteStatus.DRAFT.value, nullable=False
    )
    last_published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    published_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    published_commit_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Feature flags
    search_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    toc_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version_selector_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    feedback_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Analytics
    analytics_id: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g., GA4 ID

    # Navigation customization (JSON stored as text for flexibility)
    navigation_config: Mapped[str | None] = mapped_column(Text, nullable=True)
    footer_config: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    space: Mapped["Space"] = relationship("Space", foreign_keys=[space_id])
    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[organization_id])
    theme: Mapped["Theme | None"] = relationship("Theme", foreign_keys=[theme_id])
    published_by: Mapped["User | None"] = relationship("User", foreign_keys=[published_by_id])

    def __repr__(self) -> str:
        return f"<PublishedSite {self.slug}>"

    @property
    def is_published(self) -> bool:
        """Check if site is currently published."""
        return self.status == SiteStatus.PUBLISHED.value

    @property
    def public_url(self) -> str:
        """Get the public URL for this site."""
        if self.custom_domain and self.custom_domain_verified:
            return f"https://{self.custom_domain}"
        return f"/s/{self.slug}"

    def can_access(self, user_email: str | None) -> bool:
        """Check if a user can access this site based on visibility settings."""
        if self.visibility == SiteVisibility.PUBLIC.value:
            return True

        if self.visibility == SiteVisibility.AUTHENTICATED.value:
            return user_email is not None

        if self.visibility == SiteVisibility.RESTRICTED.value:
            if not user_email or not self.allowed_email_domains:
                return False
            domain = user_email.split("@")[-1] if "@" in user_email else ""
            return domain in self.allowed_email_domains

        return False
