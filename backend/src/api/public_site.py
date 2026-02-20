"""Public site router for viewing published documentation.

Sprint A: Publishing
Sprint D: Integrated Access Control

Routes for accessing published documentation sites.
Implements layered access model:
1. Site visibility (first gate)
2. Document classification + ACLs (second gate)
"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.db.models import Page, SiteStatus, SiteVisibility
from src.db.models.site_visitor import SiteVisitor
from src.db.models.user import User
from src.modules.publishing import (
    PublishingService,
    ThemeService,
    RenderedPage,
    SiteNavigation,
    PublishedSiteAccessService,
    get_visitor_service,
    get_sso_bridge,
    transform_page_content,
    generate_publish_report,
)
from src.modules.publishing.service import PublishingError

router = APIRouter(tags=["public-site"])


async def get_visitor_from_request(
    request: Request,
    db: AsyncSession,
) -> tuple[Optional[SiteVisitor], Optional[User]]:
    """Extract visitor or internal user from request.

    Checks for:
    1. Internal user via SSO token (Authorization header)
    2. External visitor via session token (X-Visitor-Token header or cookie)
    """
    visitor = None
    internal_user = None

    # Check for internal user (SSO)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # This would integrate with main auth system
        # For now, try to get user from token
        try:
            from src.api.deps import get_current_user_optional
            internal_user = await get_current_user_optional(
                token=auth_header.replace("Bearer ", ""),
                db=db,
            )
        except Exception:
            pass

    # Check for external visitor session
    visitor_token = (
        request.headers.get("X-Visitor-Token") or
        request.cookies.get("visitor_session")
    )
    if visitor_token:
        visitor_service = await get_visitor_service(db)
        visitor = await visitor_service.get_visitor_by_token(visitor_token)

    return visitor, internal_user


async def get_public_site(
    site_slug: str,
    db: AsyncSession,
    request: Request,
):
    """Get a published site by slug, checking access permissions.

    Returns tuple of (site, visitor, internal_user) if:
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

    # Get visitor/user from request
    visitor, internal_user = await get_visitor_from_request(request, db)

    # Check site visibility (first gate)
    access_service = PublishedSiteAccessService(db)
    visibility_result = await access_service.check_site_visibility(
        site, visitor, internal_user
    )

    if not visibility_result.allowed:
        if site.visibility == SiteVisibility.AUTHENTICATED.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif site.visibility == SiteVisibility.RESTRICTED.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=visibility_result.reason,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    return site, visitor, internal_user


async def _filter_navigation_items(
    items: list,
    site,
    visitor: Optional[SiteVisitor],
    internal_user: Optional[User],
    access_service: PublishedSiteAccessService,
    db: AsyncSession,
) -> list:
    """Filter navigation items based on visitor access.

    Handles:
    - Completely hidden pages (no access, no placeholder)
    - Placeholder pages (no access, but show as restricted)
    - Full access pages
    """
    from src.modules.publishing.schemas import NavigationItem

    filtered = []

    for item in items:
        # Get the page to check access
        result = await db.execute(
            select(Page).where(Page.id == item.page_id)
        )
        page = result.scalar_one_or_none()

        if not page:
            continue

        # Check access
        access_result = await access_service.can_access_page(
            site, page, visitor, internal_user
        )

        if access_result.allowed:
            # Full access - include with filtered children
            new_children = await _filter_navigation_items(
                item.children or [],
                site, visitor, internal_user, access_service, db
            )
            filtered.append(NavigationItem(
                page_id=item.page_id,
                title=item.title,
                slug=item.slug,
                path=item.path,
                children=new_children,
                is_restricted=False,
            ))
        elif access_result.show_placeholder:
            # Show as restricted placeholder
            filtered.append(NavigationItem(
                page_id=item.page_id,
                title=item.title,
                slug=item.slug,
                path=item.path,
                children=[],  # Don't show children of restricted pages
                is_restricted=True,
            ))
        # else: completely hidden, don't include

    return filtered


@router.get("/{site_slug}")
async def get_site_home(
    site_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get site homepage.

    Returns site metadata and navigation. The actual homepage content
    is typically the first page in the navigation tree.
    Navigation is filtered to show only pages the visitor can access.
    """
    site, visitor, internal_user = await get_public_site(site_slug, db, request)

    publishing_service = PublishingService(db)
    theme_service = ThemeService(db)
    access_service = PublishedSiteAccessService(db)

    # Get navigation
    try:
        navigation = await publishing_service.get_site_navigation(site.id)
    except PublishingError:
        navigation = SiteNavigation(items=[], current_page_id=None)

    # Filter navigation based on access
    filtered_items = await _filter_navigation_items(
        navigation.items, site, visitor, internal_user, access_service, db
    )
    navigation = SiteNavigation(items=filtered_items, current_page_id=None)

    # Get theme
    theme = None
    if site.theme_id:
        theme = await theme_service.get_theme(site.theme_id)

    # Find homepage (first page in navigation)
    homepage_slug = None
    if navigation.items:
        homepage_slug = navigation.items[0].slug

    # Check if user is authenticated
    is_authenticated = visitor is not None or internal_user is not None

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
        "is_authenticated": is_authenticated,
        "visitor_email": visitor.email if visitor else (internal_user.email if internal_user else None),
    }


@router.get("/{site_slug}/navigation")
async def get_site_nav(
    site_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_page_id: str | None = Query(None, description="Current page for highlighting"),
) -> SiteNavigation:
    """Get navigation for a published site.

    Navigation is filtered to show only pages the visitor can access.
    """
    site, visitor, internal_user = await get_public_site(site_slug, db, request)

    publishing_service = PublishingService(db)
    access_service = PublishedSiteAccessService(db)

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

    # Filter navigation based on access
    filtered_items = await _filter_navigation_items(
        navigation.items, site, visitor, internal_user, access_service, db
    )

    return SiteNavigation(items=filtered_items, current_page_id=current_page_id)


@router.get("/{site_slug}/page/{page_slug:path}")
async def get_site_page(
    site_slug: str,
    page_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get a rendered page from a published site.

    The page_slug can include path segments for nested pages.
    Checks document-level access and transforms content based on viewer's clearance.
    """
    site, visitor, internal_user = await get_public_site(site_slug, db, request)

    publishing_service = PublishingService(db)
    access_service = PublishedSiteAccessService(db)

    # Get the page
    result = await db.execute(
        select(Page).where(
            Page.space_id == site.space_id,
            Page.slug == page_slug,
        )
    )
    db_page = result.scalar_one_or_none()

    if not db_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    # Check page-level access (second gate)
    access_result = await access_service.can_access_page(
        site, db_page, visitor, internal_user
    )

    if not access_result.allowed:
        if access_result.show_placeholder:
            # Return placeholder response
            placeholder_message = (
                site.restricted_placeholder_message or
                "You do not have access to view this content."
            )
            return {
                "id": db_page.id,
                "title": db_page.title,
                "slug": db_page.slug,
                "is_restricted": True,
                "restricted_message": placeholder_message,
                "content_html": None,
                "content_markdown": None,
                "toc": [],
            }
        else:
            # Completely hidden
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found",
            )

    # Render the page
    rendered = await publishing_service.render_page(
        site_id=site.id,
        page_slug=page_slug,
    )

    if not rendered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    # Transform content (handle links/embeds to restricted docs)
    if rendered.content_markdown:
        transform_result = await transform_page_content(
            db=db,
            site=site,
            content=rendered.content_markdown,
            visitor=visitor,
            internal_user=internal_user,
            current_page=db_page,
        )
        # Update rendered content with transformed version
        # The publishing service would need to re-render the transformed markdown
        # For now, we include transformation metadata
        return {
            **rendered.model_dump(),
            "is_restricted": False,
            "transform_applied": transform_result.transform_count > 0,
            "restricted_references": transform_result.restricted_references,
        }

    return {
        **rendered.model_dump(),
        "is_restricted": False,
        "transform_applied": False,
        "restricted_references": [],
    }


@router.get("/{site_slug}/search")
async def search_site(
    site_slug: str,
    q: str = Query(..., min_length=1, description="Search query"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Search within a published site.

    Returns matching pages with snippets.
    Search results are filtered based on visitor's access level.
    """
    site, visitor, internal_user = await get_public_site(site_slug, db, request)

    # Check if search is enabled
    if not site.search_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not enabled for this site",
        )

    access_service = PublishedSiteAccessService(db)

    # Basic search implementation - can be enhanced with full-text search
    from src.db.models import PageStatus

    search_result = await db.execute(
        select(Page).where(
            Page.space_id == site.space_id,
            Page.status.in_([PageStatus.APPROVED.value, PageStatus.EFFECTIVE.value]),
            Page.title.ilike(f"%{q}%"),
        ).limit(50)  # Get more results since we'll filter
    )
    pages = list(search_result.scalars().all())

    # Filter by access
    accessible_results = []
    placeholder_results = []

    for page in pages:
        access_result = await access_service.can_access_page(
            site, page, visitor, internal_user
        )

        if access_result.allowed:
            accessible_results.append({
                "id": page.id,
                "title": page.title,
                "slug": page.slug,
                "path": f"/s/{site_slug}/page/{page.slug}",
                "snippet": page.description or "",
                "is_restricted": False,
            })
        elif access_result.show_placeholder:
            placeholder_results.append({
                "id": page.id,
                "title": page.title,
                "slug": page.slug,
                "path": f"/s/{site_slug}/page/{page.slug}",
                "snippet": "This content requires additional access.",
                "is_restricted": True,
            })
        # else: completely hidden from search

        # Limit total results
        if len(accessible_results) + len(placeholder_results) >= 20:
            break

    # Accessible results first, then placeholders
    results = accessible_results + placeholder_results

    return {
        "query": q,
        "results": results,
        "total": len(results),
        "accessible_count": len(accessible_results),
        "restricted_count": len(placeholder_results),
    }


@router.get("/{site_slug}/sitemap.xml", response_class=HTMLResponse)
async def get_sitemap(
    site_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> str:
    """Generate sitemap.xml for SEO.

    Only includes publicly accessible pages (classification 0).
    """
    site, visitor, internal_user = await get_public_site(site_slug, db, request)

    # Only public sites get sitemaps
    if site.visibility != SiteVisibility.PUBLIC.value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sitemap not available",
        )

    publishing_service = PublishingService(db)
    access_service = PublishedSiteAccessService(db)

    try:
        navigation = await publishing_service.get_site_navigation(site.id)
    except PublishingError:
        navigation = SiteNavigation(items=[], current_page_id=None)

    # Filter to only public pages (anonymous access)
    filtered_items = await _filter_navigation_items(
        navigation.items, site, None, None, access_service, db
    )

    # Build sitemap XML
    base_url = str(request.base_url).rstrip("/")

    urls = []

    def add_nav_items(items, urls):
        for item in items:
            # Only add non-restricted items to sitemap
            if not getattr(item, 'is_restricted', False):
                urls.append(f"{base_url}{item.path}")
                if item.children:
                    add_nav_items(item.children, urls)

    add_nav_items(filtered_items, urls)

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
    site, visitor, internal_user = await get_public_site(site_slug, db, request)

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


# Pre-publish report endpoint (requires admin authentication)

@router.get("/{site_slug}/publish-report")
async def get_publish_report(
    site_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get pre-publish report showing audience breakdown.

    Requires admin access to the site.
    """
    site, visitor, internal_user = await get_public_site(site_slug, db, request)

    # Require internal user with admin access
    if not internal_user or internal_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    report = await generate_publish_report(db, site)

    return report.to_dict()
