"""Space API endpoints."""

from fastapi import APIRouter, HTTPException, status

from src.api.deps import DbSession, CurrentUser
from src.modules.content.schemas import (
    SpaceCreate,
    SpaceUpdate,
    SpaceResponse,
)
from src.modules.content.service import (
    create_space,
    get_space,
    list_workspace_spaces,
    update_space,
    get_workspace,
)

router = APIRouter()


@router.post("/", response_model=SpaceResponse, status_code=status.HTTP_201_CREATED)
async def create_sp(
    space_in: SpaceCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> SpaceResponse:
    """Create a new space in a workspace."""
    # Verify workspace exists
    workspace = await get_workspace(db, space_in.workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    space = await create_space(db, space_in)
    return SpaceResponse.model_validate(space)


@router.get("/workspace/{ws_id}", response_model=list[SpaceResponse])
async def list_sp_by_workspace(
    ws_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> list[SpaceResponse]:
    """List spaces in a workspace."""
    spaces = await list_workspace_spaces(db, ws_id)
    return [SpaceResponse.model_validate(sp) for sp in spaces]


@router.get("/{space_id}", response_model=SpaceResponse)
async def get_sp(
    space_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> SpaceResponse:
    """Get a space by ID."""
    space = await get_space(db, space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found",
        )
    return SpaceResponse.model_validate(space)


@router.patch("/{space_id}", response_model=SpaceResponse)
async def update_sp(
    space_id: str,
    space_in: SpaceUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> SpaceResponse:
    """Update a space."""
    space = await get_space(db, space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found",
        )

    updated = await update_space(db, space, space_in)
    return SpaceResponse.model_validate(updated)
