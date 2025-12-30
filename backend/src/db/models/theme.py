"""Theme model for published site customization.

Sprint A: Publishing
"""

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.organization import Organization
    from src.db.models.user import User


class SidebarPosition(str, Enum):
    """Sidebar position options."""

    LEFT = "left"
    RIGHT = "right"
    HIDDEN = "hidden"


class ContentWidth(str, Enum):
    """Content width options."""

    PROSE = "prose"  # ~65ch, optimal for reading
    WIDE = "wide"  # ~80ch
    FULL = "full"  # Full width


class Theme(Base, UUIDMixin, TimestampMixin):
    """Theme configuration for published documentation sites."""

    __tablename__ = "themes"

    # Organization (None = system theme available to all)
    organization_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Colors
    primary_color: Mapped[str] = mapped_column(String(20), default="#2563eb", nullable=False)
    secondary_color: Mapped[str] = mapped_column(String(20), default="#64748b", nullable=False)
    accent_color: Mapped[str] = mapped_column(String(20), default="#0ea5e9", nullable=False)
    background_color: Mapped[str] = mapped_column(String(20), default="#ffffff", nullable=False)
    surface_color: Mapped[str] = mapped_column(String(20), default="#f8fafc", nullable=False)
    text_color: Mapped[str] = mapped_column(String(20), default="#1f2937", nullable=False)
    text_muted_color: Mapped[str] = mapped_column(String(20), default="#6b7280", nullable=False)

    # Typography
    heading_font: Mapped[str] = mapped_column(String(100), default="Inter", nullable=False)
    body_font: Mapped[str] = mapped_column(String(100), default="Inter", nullable=False)
    code_font: Mapped[str] = mapped_column(String(100), default="JetBrains Mono", nullable=False)
    base_font_size: Mapped[str] = mapped_column(String(20), default="16px", nullable=False)

    # Layout
    sidebar_position: Mapped[str] = mapped_column(
        String(20), default=SidebarPosition.LEFT.value, nullable=False
    )
    content_width: Mapped[str] = mapped_column(
        String(20), default=ContentWidth.PROSE.value, nullable=False
    )
    toc_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    header_height: Mapped[str] = mapped_column(String(20), default="64px", nullable=False)

    # Branding
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    favicon_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Custom CSS/HTML
    custom_css: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_head_html: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Created by
    created_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    organization: Mapped["Organization | None"] = relationship(
        "Organization", foreign_keys=[organization_id]
    )
    created_by: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self) -> str:
        return f"<Theme {self.name}>"

    def to_css_variables(self) -> str:
        """Generate CSS custom properties from theme settings."""
        return f"""
:root {{
    --color-primary: {self.primary_color};
    --color-secondary: {self.secondary_color};
    --color-accent: {self.accent_color};
    --color-background: {self.background_color};
    --color-surface: {self.surface_color};
    --color-text: {self.text_color};
    --color-text-muted: {self.text_muted_color};
    --font-heading: "{self.heading_font}", system-ui, sans-serif;
    --font-body: "{self.body_font}", system-ui, sans-serif;
    --font-code: "{self.code_font}", ui-monospace, monospace;
    --font-size-base: {self.base_font_size};
    --header-height: {self.header_height};
}}
"""
