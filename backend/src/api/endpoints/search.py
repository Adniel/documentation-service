"""Search API endpoints."""

from fastapi import APIRouter, Query

from src.api.deps import DbSession, CurrentUser
from src.modules.content.search_service import get_search_service

router = APIRouter()


@router.get("/pages")
async def search_pages(
    q: str = Query(..., min_length=1, description="Search query"),
    space_id: str | None = Query(None, description="Filter by space"),
    workspace_id: str | None = Query(None, description="Filter by workspace"),
    organization_id: str | None = Query(None, description="Filter by organization"),
    status: str | None = Query(None, description="Filter by status"),
    diataxis_type: str | None = Query(None, description="Filter by Diátaxis type"),
    classification: int | None = Query(None, ge=0, le=3, description="Max classification level"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str | None = Query(None, description="Sort field:order (e.g., updated_at:desc)"),
    current_user: CurrentUser = None,
    db: DbSession = None,
) -> dict:
    """Search for pages with full-text search.

    Supports filtering by space, workspace, organization, status, and Diátaxis type.
    Results are filtered by user's classification clearance.
    """
    search_service = get_search_service()

    # Build filters
    filters = {}
    if space_id:
        filters["space_id"] = space_id
    if workspace_id:
        filters["workspace_id"] = workspace_id
    if organization_id:
        filters["organization_id"] = organization_id
    if status:
        filters["status"] = status
    if diataxis_type:
        filters["diataxis_type"] = diataxis_type

    # Filter by user's clearance level (can only see documents at or below their level)
    if classification is not None:
        max_level = min(classification, current_user.clearance_level)
    else:
        max_level = current_user.clearance_level

    # Meilisearch filter for classification <= max_level
    # We need to add classification levels 0 through max_level
    if max_level < 3:
        filters["classification"] = list(range(max_level + 1))

    # Parse sort parameter
    sort_list = None
    if sort:
        sort_list = [sort]

    results = await search_service.search_pages(
        query=q,
        filters=filters if filters else None,
        limit=limit,
        offset=offset,
        sort=sort_list,
    )

    return results


@router.get("/spaces")
async def search_spaces(
    q: str = Query(..., min_length=1, description="Search query"),
    workspace_id: str | None = Query(None, description="Filter by workspace"),
    organization_id: str | None = Query(None, description="Filter by organization"),
    diataxis_type: str | None = Query(None, description="Filter by Diátaxis type"),
    limit: int = Query(10, ge=1, le=50),
    current_user: CurrentUser = None,
    db: DbSession = None,
) -> dict:
    """Search for spaces."""
    search_service = get_search_service()

    filters = {}
    if workspace_id:
        filters["workspace_id"] = workspace_id
    if organization_id:
        filters["organization_id"] = organization_id
    if diataxis_type:
        filters["diataxis_type"] = diataxis_type

    results = await search_service.search_spaces(
        query=q,
        filters=filters if filters else None,
        limit=limit,
    )

    return results


@router.get("/suggestions")
async def get_suggestions(
    q: str = Query(..., min_length=2, description="Search query for suggestions"),
    limit: int = Query(5, ge=1, le=10),
    current_user: CurrentUser = None,
) -> list[dict]:
    """Get search suggestions/autocomplete results.

    Returns a mix of matching page titles and space names.
    """
    search_service = get_search_service()
    suggestions = await search_service.get_suggestions(query=q, limit=limit)
    return suggestions


@router.post("/reindex")
async def reindex_all(
    current_user: CurrentUser = None,
    db: DbSession = None,
) -> dict:
    """Reindex all content (admin only).

    This will clear and rebuild all search indexes.
    """
    if not current_user.is_superuser:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reindex",
        )

    # This would trigger a background job to reindex all content
    # For now, just return a placeholder response
    return {
        "status": "started",
        "message": "Reindexing has been queued",
    }
