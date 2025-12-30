"""Publishing module API endpoints.

Sprint A: Publishing
Enables creation and management of published documentation sites.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import DbSession, CurrentUser
from src.db.models import SiteStatus
from src.modules.publishing import (
    PublishingService,
    ThemeService,
    ThemeCreate,
    ThemeUpdate,
    ThemeResponse,
    SiteCreate,
    SiteUpdate,
    SiteResponse,
    SitePublishRequest,
    PublishResult,
    RenderedPage,
    SiteNavigation,
)
from src.modules.publishing.service import PublishingError
from src.modules.audit.audit_service import AuditService

router = APIRouter(tags=["publishing"])


# =============================================================================
# THEME ENDPOINTS
# =============================================================================


@router.get("/themes", response_model=List[ThemeResponse])
async def list_themes(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: str | None = Query(None, description="Filter by organization"),
    include_system: bool = Query(True, description="Include system themes"),
) -> List[ThemeResponse]:
    """List available themes.

    Returns system themes and organization-specific themes.
    """
    theme_service = ThemeService(db)
    themes = await theme_service.list_themes(
        organization_id=organization_id,
        include_system=include_system,
    )
    return [ThemeResponse.model_validate(t) for t in themes]


@router.get("/themes/{theme_id}", response_model=ThemeResponse)
async def get_theme(
    theme_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> ThemeResponse:
    """Get a theme by ID."""
    theme_service = ThemeService(db)
    theme = await theme_service.get_theme(theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found",
        )
    return ThemeResponse.model_validate(theme)


@router.post("/organizations/{organization_id}/themes", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED)
async def create_theme(
    organization_id: str,
    theme_in: ThemeCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> ThemeResponse:
    """Create a new theme for an organization.

    Requires Admin role on the organization.
    """
    theme_service = ThemeService(db)
    theme = await theme_service.create_theme(
        organization_id=organization_id,
        data=theme_in,
        created_by_id=str(current_user.id),
    )

    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="publishing.theme_created",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="theme",
        resource_id=theme.id,
        resource_name=theme.name,
        details={"organization_id": organization_id},
    )

    return ThemeResponse.model_validate(theme)


@router.patch("/themes/{theme_id}", response_model=ThemeResponse)
async def update_theme(
    theme_id: str,
    theme_in: ThemeUpdate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> ThemeResponse:
    """Update a theme.

    Requires Admin role on the theme's organization.
    """
    theme_service = ThemeService(db)
    theme = await theme_service.update_theme(theme_id, theme_in)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found",
        )

    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="publishing.theme_updated",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="theme",
        resource_id=theme.id,
        resource_name=theme.name,
        details={"updated_fields": list(theme_in.model_dump(exclude_unset=True).keys())},
    )

    return ThemeResponse.model_validate(theme)


@router.delete("/themes/{theme_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_theme(
    theme_id: str,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a theme.

    Cannot delete system themes. Requires Admin role.
    """
    theme_service = ThemeService(db)

    # Get theme first for audit
    theme = await theme_service.get_theme(theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found",
        )

    try:
        deleted = await theme_service.delete_theme(theme_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Theme not found",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="publishing.theme_deleted",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="theme",
        resource_id=theme_id,
        resource_name=theme.name,
    )


@router.post("/themes/{theme_id}/duplicate", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_theme(
    theme_id: str,
    organization_id: str = Query(..., description="Target organization"),
    new_name: str = Query(..., description="Name for the duplicated theme"),
    db: DbSession = None,
    current_user: CurrentUser = None,
) -> ThemeResponse:
    """Duplicate a theme to an organization."""
    theme_service = ThemeService(db)
    theme = await theme_service.duplicate_theme(
        theme_id=theme_id,
        organization_id=organization_id,
        new_name=new_name,
        created_by_id=str(current_user.id),
    )
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source theme not found",
        )
    return ThemeResponse.model_validate(theme)


# =============================================================================
# SITE ENDPOINTS
# =============================================================================


@router.get("/sites", response_model=List[SiteResponse])
async def list_sites(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: str | None = Query(None, description="Filter by organization"),
    status: SiteStatus | None = Query(None, description="Filter by status"),
) -> List[SiteResponse]:
    """List published sites.

    Returns sites the user has access to.
    """
    publishing_service = PublishingService(db)
    sites = await publishing_service.list_sites(
        organization_id=organization_id,
        status=status,
    )
    return [
        SiteResponse(
            **{
                **s.__dict__,
                "visibility": s.visibility,
                "status": s.status,
                "public_url": s.public_url,
            }
        )
        for s in sites
    ]


@router.get("/sites/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> SiteResponse:
    """Get a site by ID."""
    publishing_service = PublishingService(db)
    site = await publishing_service.get_site(site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )
    return SiteResponse(
        **{
            **site.__dict__,
            "visibility": site.visibility,
            "status": site.status,
            "public_url": site.public_url,
        }
    )


@router.post("/sites", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    site_in: SiteCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> SiteResponse:
    """Create a new published site for a space.

    Each space can only have one published site.
    Requires Admin role on the space's organization.
    """
    publishing_service = PublishingService(db)

    try:
        site = await publishing_service.create_site(
            data=site_in,
            user_id=str(current_user.id),
        )
    except PublishingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return SiteResponse(
        **{
            **site.__dict__,
            "visibility": site.visibility,
            "status": site.status,
            "public_url": site.public_url,
        }
    )


@router.patch("/sites/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: str,
    site_in: SiteUpdate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> SiteResponse:
    """Update a site.

    Requires Admin role on the site's organization.
    """
    publishing_service = PublishingService(db)

    try:
        site = await publishing_service.update_site(
            site_id=site_id,
            data=site_in,
            user_id=str(current_user.id),
        )
    except PublishingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    return SiteResponse(
        **{
            **site.__dict__,
            "visibility": site.visibility,
            "status": site.status,
            "public_url": site.public_url,
        }
    )


@router.delete("/sites/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: str,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a site.

    Requires Admin role on the site's organization.
    """
    publishing_service = PublishingService(db)
    deleted = await publishing_service.delete_site(
        site_id=site_id,
        user_id=str(current_user.id),
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )


@router.post("/sites/{site_id}/publish", response_model=PublishResult)
async def publish_site(
    site_id: str,
    publish_request: SitePublishRequest | None = None,
    request: Request = None,
    db: DbSession = None,
    current_user: CurrentUser = None,
) -> PublishResult:
    """Publish a site (make it live).

    Requires Admin role on the site's organization.
    """
    publishing_service = PublishingService(db)

    try:
        result = await publishing_service.publish_site(
            site_id=site_id,
            user_id=str(current_user.id),
            commit_message=publish_request.commit_message if publish_request else None,
        )
    except PublishingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return result


@router.post("/sites/{site_id}/unpublish", response_model=SiteResponse)
async def unpublish_site(
    site_id: str,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> SiteResponse:
    """Unpublish a site (take offline).

    Requires Admin role on the site's organization.
    """
    publishing_service = PublishingService(db)
    site = await publishing_service.unpublish_site(
        site_id=site_id,
        user_id=str(current_user.id),
    )
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    return SiteResponse(
        **{
            **site.__dict__,
            "visibility": site.visibility,
            "status": site.status,
            "public_url": site.public_url,
        }
    )


# =============================================================================
# SITE CONTENT ENDPOINTS (for preview/internal use)
# =============================================================================


@router.get("/sites/{site_id}/navigation", response_model=SiteNavigation)
async def get_site_navigation(
    site_id: str,
    db: DbSession,
    current_user: CurrentUser,
    current_page_id: str | None = Query(None, description="Current page for highlighting"),
) -> SiteNavigation:
    """Get navigation structure for a site."""
    publishing_service = PublishingService(db)

    try:
        navigation = await publishing_service.get_site_navigation(
            site_id=site_id,
            current_page_id=current_page_id,
        )
    except PublishingError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return navigation


@router.get("/sites/{site_id}/pages/{page_slug}", response_model=RenderedPage)
async def get_site_page(
    site_id: str,
    page_slug: str,
    db: DbSession,
    current_user: CurrentUser,
) -> RenderedPage:
    """Get a rendered page for preview.

    For the public site, use the /s/{slug}/{page} routes instead.
    """
    publishing_service = PublishingService(db)
    page = await publishing_service.render_page(
        site_id=site_id,
        page_slug=page_slug,
    )
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )
    return page
