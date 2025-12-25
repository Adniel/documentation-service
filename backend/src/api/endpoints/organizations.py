"""Organization API endpoints."""

from fastapi import APIRouter, HTTPException, status

from src.api.deps import DbSession, CurrentUser
from src.modules.content.schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)
from src.modules.content.service import (
    create_organization,
    get_organization,
    get_organization_by_slug,
    list_user_organizations,
    update_organization,
)
from src.modules.content.git_service import get_git_service

router = APIRouter()


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_org(
    org_in: OrganizationCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> OrganizationResponse:
    """Create a new organization."""
    # Check if slug is taken
    existing = await get_organization_by_slug(db, org_in.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization slug already exists",
        )

    # Create organization
    org = await create_organization(db, org_in, current_user)

    # Initialize Git repository
    git_service = get_git_service()
    git_service.init_repo(org.slug)

    return OrganizationResponse.model_validate(org)


@router.get("/", response_model=list[OrganizationResponse])
async def list_orgs(
    db: DbSession,
    current_user: CurrentUser,
) -> list[OrganizationResponse]:
    """List organizations the current user belongs to."""
    orgs = await list_user_organizations(db, current_user.id)
    return [OrganizationResponse.model_validate(org) for org in orgs]


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_org(
    org_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> OrganizationResponse:
    """Get an organization by ID."""
    org = await get_organization(db, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    return OrganizationResponse.model_validate(org)


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_org(
    org_id: str,
    org_in: OrganizationUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> OrganizationResponse:
    """Update an organization."""
    org = await get_organization(db, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check ownership (in real app, check membership role)
    if org.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this organization",
        )

    updated = await update_organization(db, org, org_in)
    return OrganizationResponse.model_validate(updated)
