"""Navigation API endpoints for hierarchy and tree structures."""

from fastapi import APIRouter, HTTPException, status

from src.api.deps import DbSession, CurrentUser
from src.modules.content.navigation_service import (
    get_workspace_tree,
    get_space_tree,
    get_breadcrumbs,
    get_recent_pages,
)

router = APIRouter()


@router.get("/tree/workspace/{workspace_id}")
async def get_workspace_navigation_tree(
    workspace_id: str,
    db: DbSession,
    current_user: CurrentUser,
    include_pages: bool = True,
    max_depth: int = 3,
) -> dict:
    """Get the navigation tree for a workspace.

    Returns a hierarchical structure of spaces and optionally pages
    that the user has access to.
    """
    tree = await get_workspace_tree(
        db,
        workspace_id=workspace_id,
        user_clearance=current_user.clearance_level,
        include_pages=include_pages,
        max_depth=max_depth,
    )

    if tree is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    return tree


@router.get("/tree/space/{space_id}")
async def get_space_navigation_tree(
    space_id: str,
    db: DbSession,
    current_user: CurrentUser,
    include_children: bool = True,
) -> dict:
    """Get the navigation tree for a specific space.

    Returns the space with its child spaces and pages.
    """
    tree = await get_space_tree(
        db,
        space_id=space_id,
        user_clearance=current_user.clearance_level,
        include_children=include_children,
    )

    if tree is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found",
        )

    return tree


@router.get("/breadcrumbs/page/{page_id}")
async def get_page_breadcrumbs(
    page_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> list[dict]:
    """Get breadcrumb trail for a page.

    Returns the path from organization to the page:
    [Organization, Workspace, Space, ..., Page]
    """
    breadcrumbs = await get_breadcrumbs(db, page_id=page_id, resource_type="page")

    if breadcrumbs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    return breadcrumbs


@router.get("/breadcrumbs/space/{space_id}")
async def get_space_breadcrumbs(
    space_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> list[dict]:
    """Get breadcrumb trail for a space."""
    breadcrumbs = await get_breadcrumbs(db, page_id=space_id, resource_type="space")

    if breadcrumbs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found",
        )

    return breadcrumbs


@router.get("/recent")
async def get_recent_documents(
    db: DbSession,
    current_user: CurrentUser,
    limit: int = 10,
    workspace_id: str | None = None,
) -> list[dict]:
    """Get recently updated pages the user has access to."""
    pages = await get_recent_pages(
        db,
        user_id=current_user.id,
        user_clearance=current_user.clearance_level,
        limit=limit,
        workspace_id=workspace_id,
    )
    return pages


@router.get("/favorites")
async def get_favorite_pages(
    db: DbSession,
    current_user: CurrentUser,
) -> list[dict]:
    """Get user's favorite/bookmarked pages."""
    # TODO: Implement favorites system
    return []
