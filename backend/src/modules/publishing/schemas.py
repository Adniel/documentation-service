"""Pydantic schemas for publishing module.

Sprint A: Publishing
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.db.models import SidebarPosition, ContentWidth, SiteStatus, SiteVisibility


# =============================================================================
# THEME SCHEMAS
# =============================================================================


class ThemeBase(BaseModel):
    """Base theme schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None

    # Colors
    primary_color: str = Field(default="#2563eb", pattern=r"^#[0-9a-fA-F]{6}$")
    secondary_color: str = Field(default="#64748b", pattern=r"^#[0-9a-fA-F]{6}$")
    accent_color: str = Field(default="#0ea5e9", pattern=r"^#[0-9a-fA-F]{6}$")
    background_color: str = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    surface_color: str = Field(default="#f8fafc", pattern=r"^#[0-9a-fA-F]{6}$")
    text_color: str = Field(default="#1f2937", pattern=r"^#[0-9a-fA-F]{6}$")
    text_muted_color: str = Field(default="#6b7280", pattern=r"^#[0-9a-fA-F]{6}$")

    # Typography
    heading_font: str = Field(default="Inter", max_length=100)
    body_font: str = Field(default="Inter", max_length=100)
    code_font: str = Field(default="JetBrains Mono", max_length=100)
    base_font_size: str = Field(default="16px", max_length=20)

    # Layout
    sidebar_position: SidebarPosition = SidebarPosition.LEFT
    content_width: ContentWidth = ContentWidth.PROSE
    toc_enabled: bool = True
    header_height: str = Field(default="64px", max_length=20)

    # Branding
    logo_url: str | None = None
    favicon_url: str | None = None

    # Custom CSS/HTML
    custom_css: str | None = None
    custom_head_html: str | None = None


class ThemeCreate(ThemeBase):
    """Schema for creating a theme."""

    pass


class ThemeUpdate(BaseModel):
    """Schema for updating a theme."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None

    # Colors
    primary_color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    secondary_color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    accent_color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    background_color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    surface_color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    text_color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    text_muted_color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")

    # Typography
    heading_font: str | None = Field(None, max_length=100)
    body_font: str | None = Field(None, max_length=100)
    code_font: str | None = Field(None, max_length=100)
    base_font_size: str | None = Field(None, max_length=20)

    # Layout
    sidebar_position: SidebarPosition | None = None
    content_width: ContentWidth | None = None
    toc_enabled: bool | None = None
    header_height: str | None = Field(None, max_length=20)

    # Branding
    logo_url: str | None = None
    favicon_url: str | None = None

    # Custom CSS/HTML
    custom_css: str | None = None
    custom_head_html: str | None = None


class ThemeResponse(ThemeBase):
    """Theme response schema."""

    id: str
    organization_id: str | None
    is_default: bool
    created_by_id: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# SITE SCHEMAS
# =============================================================================


class SiteBase(BaseModel):
    """Base site schema."""

    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    site_title: str = Field(..., min_length=1, max_length=255)
    site_description: str | None = None

    # Theme
    theme_id: str | None = None
    custom_css: str | None = None
    logo_url: str | None = None

    # SEO
    og_image_url: str | None = None
    favicon_url: str | None = None

    # Visibility
    visibility: SiteVisibility = SiteVisibility.AUTHENTICATED
    allowed_email_domains: list[str] | None = None

    # Features
    search_enabled: bool = True
    toc_enabled: bool = True
    version_selector_enabled: bool = False
    feedback_enabled: bool = False

    # Analytics
    analytics_id: str | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Validate slug format."""
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Slug cannot start or end with a hyphen")
        if "--" in v:
            raise ValueError("Slug cannot contain consecutive hyphens")
        return v.lower()


class SiteCreate(SiteBase):
    """Schema for creating a site."""

    space_id: str


class SiteUpdate(BaseModel):
    """Schema for updating a site."""

    slug: str | None = Field(None, min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    site_title: str | None = Field(None, min_length=1, max_length=255)
    site_description: str | None = None

    # Domain
    custom_domain: str | None = None

    # Theme
    theme_id: str | None = None
    custom_css: str | None = None
    logo_url: str | None = None

    # SEO
    og_image_url: str | None = None
    favicon_url: str | None = None

    # Visibility
    visibility: SiteVisibility | None = None
    allowed_email_domains: list[str] | None = None

    # Features
    search_enabled: bool | None = None
    toc_enabled: bool | None = None
    version_selector_enabled: bool | None = None
    feedback_enabled: bool | None = None

    # Analytics
    analytics_id: str | None = None

    # Navigation
    navigation_config: dict[str, Any] | None = None
    footer_config: dict[str, Any] | None = None


class SiteResponse(SiteBase):
    """Site response schema."""

    id: str
    space_id: str
    organization_id: str
    custom_domain: str | None
    custom_domain_verified: bool
    status: SiteStatus
    last_published_at: datetime | None
    published_by_id: str | None
    published_commit_sha: str | None
    navigation_config: dict[str, Any] | None = None
    footer_config: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    # Computed
    public_url: str

    class Config:
        from_attributes = True


# =============================================================================
# PUBLISH SCHEMAS
# =============================================================================


class SitePublishRequest(BaseModel):
    """Request to publish a site."""

    commit_message: str | None = None


class PublishResult(BaseModel):
    """Result of a publish operation."""

    success: bool
    site_id: str
    published_at: datetime
    commit_sha: str | None
    pages_published: int
    public_url: str
    message: str | None = None


# =============================================================================
# RENDERED CONTENT SCHEMAS
# =============================================================================


class NavigationItem(BaseModel):
    """Navigation tree item."""

    id: str
    title: str
    slug: str
    path: str
    type: str  # "page" or "section"
    children: list["NavigationItem"] = []


class SiteNavigation(BaseModel):
    """Full site navigation."""

    items: list[NavigationItem]
    current_page_id: str | None = None


class RenderedPage(BaseModel):
    """Rendered page content for display."""

    id: str
    title: str
    slug: str
    path: str
    content_html: str
    toc: list[dict[str, Any]]  # Table of contents
    breadcrumbs: list[dict[str, str]]
    last_updated: datetime | None
    author_name: str | None = None

    # SEO
    meta_description: str | None = None
    meta_keywords: list[str] | None = None

    # Navigation context
    prev_page: dict[str, str] | None = None
    next_page: dict[str, str] | None = None
