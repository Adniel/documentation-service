"""Public site router for viewing published documentation.

Sprint A: Publishing
Routes for accessing published documentation sites without authentication.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.db.models import SiteStatus, SiteVisibility
from src.modules.publishing import (
    PublishingService,
    ThemeService,
    RenderedPage,
    SiteNavigation,
)
from src.modules.publishing.service import PublishingError

router = APIRouter(tags=["public-site"])


async def get_public_site(
    site_slug: str,
    db: AsyncSession,
    request: Request,
):
    """Get a published site by slug, checking access permissions.

    Returns the site if:
    - Site exists and is published
    - Visibility allows access (public, or authenticated user with correct domain)
    """
    publishing_service = PublishingService(db)
    site = await publishing_service.get_site_by_slug(site_slug)

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    # Check if site is published
    if site.status != SiteStatus.PUBLISHED.value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    # Check visibility
    if site.visibility == SiteVisibility.PUBLIC.value:
        return site

    # For authenticated/restricted visibility, check user
    # For now, we'll implement basic access - this can be enhanced
    # to check JWT tokens from cookies or headers
    if site.visibility == SiteVisibility.RESTRICTED.value:
        # Restricted sites require specific email domains
        # This would need to be checked against authenticated user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted",
        )

    # AUTHENTICATED visibility - would check for valid session
    # For now, allow access (can be enhanced later)
    return site


@router.get("/{site_slug}")
async def get_site_home(
    site_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get site homepage.

    Returns site metadata and navigation. The actual homepage content
    is typically the first page in the navigation tree.
    """
    site = await get_public_site(site_slug, db, request)

    publishing_service = PublishingService(db)
    theme_service = ThemeService(db)

    # Get navigation
    try:
        navigation = await publishing_service.get_site_navigation(site.id)
    except PublishingError:
        navigation = SiteNavigation(items=[], current_page_id=None)

    # Get theme
    theme = None
    if site.theme_id:
        theme = await theme_service.get_theme(site.theme_id)

    # Find homepage (first page in navigation)
    homepage_slug = None
    if navigation.items:
        homepage_slug = navigation.items[0].slug

    return {
        "site": {
            "id": site.id,
            "slug": site.slug,
            "title": site.site_title,
            "description": site.site_description,
            "logo_url": site.logo_url,
            "favicon_url": site.favicon_url,
            "search_enabled": site.search_enabled,
            "toc_enabled": site.toc_enabled,
            "feedback_enabled": site.feedback_enabled,
        },
        "theme": {
            "id": theme.id,
            "name": theme.name,
            "primary_color": theme.primary_color,
            "secondary_color": theme.secondary_color,
            "accent_color": theme.accent_color,
            "background_color": theme.background_color,
            "surface_color": theme.surface_color,
            "text_color": theme.text_color,
            "text_muted_color": theme.text_muted_color,
            "heading_font": theme.heading_font,
            "body_font": theme.body_font,
            "code_font": theme.code_font,
            "sidebar_position": theme.sidebar_position,
            "content_width": theme.content_width,
            "custom_css": theme.custom_css,
        } if theme else None,
        "navigation": navigation.model_dump(),
        "homepage_slug": homepage_slug,
    }


@router.get("/{site_slug}/navigation")
async def get_site_nav(
    site_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_page_id: str | None = Query(None, description="Current page for highlighting"),
) -> SiteNavigation:
    """Get navigation for a published site."""
    site = await get_public_site(site_slug, db, request)

    publishing_service = PublishingService(db)

    try:
        navigation = await publishing_service.get_site_navigation(
            site.id,
            current_page_id=current_page_id,
        )
    except PublishingError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return navigation


@router.get("/{site_slug}/page/{page_slug:path}")
async def get_site_page(
    site_slug: str,
    page_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RenderedPage:
    """Get a rendered page from a published site.

    The page_slug can include path segments for nested pages.
    """
    site = await get_public_site(site_slug, db, request)

    publishing_service = PublishingService(db)

    page = await publishing_service.render_page(
        site_id=site.id,
        page_slug=page_slug,
    )

    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    return page


@router.get("/{site_slug}/search")
async def search_site(
    site_slug: str,
    q: str = Query(..., min_length=1, description="Search query"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Search within a published site.

    Returns matching pages with snippets.
    """
    site = await get_public_site(site_slug, db, request)

    # Check if search is enabled
    if not site.search_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not enabled for this site",
        )

    publishing_service = PublishingService(db)

    # Basic search implementation - can be enhanced with full-text search
    # For now, we'll search page titles
    from sqlalchemy import select
    from src.db.models import Page, PageStatus

    result = await db.execute(
        select(Page).where(
            Page.space_id == site.space_id,
            Page.status.in_([PageStatus.APPROVED.value, PageStatus.EFFECTIVE.value]),
            Page.title.ilike(f"%{q}%"),
        ).limit(20)
    )
    pages = result.scalars().all()

    results = []
    for page in pages:
        results.append({
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "path": f"/s/{site_slug}/page/{page.slug}",
            "snippet": page.description or "",
        })

    return {
        "query": q,
        "results": results,
        "total": len(results),
    }


@router.get("/{site_slug}/sitemap.xml", response_class=HTMLResponse)
async def get_sitemap(
    site_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> str:
    """Generate sitemap.xml for SEO."""
    site = await get_public_site(site_slug, db, request)

    # Only public sites get sitemaps
    if site.visibility != SiteVisibility.PUBLIC.value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sitemap not available",
        )

    publishing_service = PublishingService(db)

    try:
        navigation = await publishing_service.get_site_navigation(site.id)
    except PublishingError:
        navigation = SiteNavigation(items=[], current_page_id=None)

    # Build sitemap XML
    base_url = str(request.base_url).rstrip("/")

    urls = []

    def add_nav_items(items, urls):
        for item in items:
            urls.append(f"{base_url}{item.path}")
            if item.children:
                add_nav_items(item.children, urls)

    add_nav_items(navigation.items, urls)

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in urls:
        sitemap += f"  <url>\n    <loc>{url}</loc>\n  </url>\n"

    sitemap += "</urlset>"

    return HTMLResponse(content=sitemap, media_type="application/xml")


@router.get("/{site_slug}/robots.txt", response_class=HTMLResponse)
async def get_robots_txt(
    site_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> str:
    """Generate robots.txt for SEO."""
    site = await get_public_site(site_slug, db, request)

    base_url = str(request.base_url).rstrip("/")

    if site.visibility == SiteVisibility.PUBLIC.value:
        # Allow indexing for public sites
        robots = f"""User-agent: *
Allow: /

Sitemap: {base_url}/s/{site_slug}/sitemap.xml
"""
    else:
        # Disallow indexing for non-public sites
        robots = """User-agent: *
Disallow: /
"""

    return HTMLResponse(content=robots, media_type="text/plain")
