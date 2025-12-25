"""Workspace API endpoints."""

from fastapi import APIRouter, HTTPException, status

from src.api.deps import DbSession, CurrentUser
from src.modules.content.schemas import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
)
from src.modules.content.service import (
    create_workspace,
    get_workspace,
    list_organization_workspaces,
    update_workspace,
    get_organization,
)

router = APIRouter()


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_ws(
    ws_in: WorkspaceCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> WorkspaceResponse:
    """Create a new workspace in an organization."""
    # Verify organization exists and user has access
    org = await get_organization(db, ws_in.organization_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    workspace = await create_workspace(db, ws_in)
    return WorkspaceResponse.model_validate(workspace)


@router.get("/org/{org_id}", response_model=list[WorkspaceResponse])
async def list_ws_by_org(
    org_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> list[WorkspaceResponse]:
    """List workspaces in an organization."""
    workspaces = await list_organization_workspaces(db, org_id)
    return [WorkspaceResponse.model_validate(ws) for ws in workspaces]


@router.get("/{ws_id}", response_model=WorkspaceResponse)
async def get_ws(
    ws_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> WorkspaceResponse:
    """Get a workspace by ID."""
    workspace = await get_workspace(db, ws_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return WorkspaceResponse.model_validate(workspace)


@router.patch("/{ws_id}", response_model=WorkspaceResponse)
async def update_ws(
    ws_id: str,
    ws_in: WorkspaceUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> WorkspaceResponse:
    """Update a workspace."""
    workspace = await get_workspace(db, ws_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    updated = await update_workspace(db, workspace, ws_in)
    return WorkspaceResponse.model_validate(updated)
