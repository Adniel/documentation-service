"""Organization API endpoints.

Sprint B: Added member management endpoints for organization-scoped admin.
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, delete, and_

from src.api.deps import DbSession, CurrentUser
from src.db.models.organization import Organization, organization_members
from src.db.models.user import User
from src.modules.content.schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationMemberCreate,
    OrganizationMemberUpdate,
    OrganizationMemberResponse,
    OrganizationMemberListResponse,
    OrganizationSettingsUpdate,
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


async def _get_member_role(db: DbSession, org_id: str, user_id: str) -> str | None:
    """Get a user's role in an organization."""
    result = await db.execute(
        select(organization_members.c.role).where(
            and_(
                organization_members.c.organization_id == org_id,
                organization_members.c.user_id == user_id,
            )
        )
    )
    row = result.first()
    return row[0] if row else None


async def _require_org_admin(db: DbSession, org_id: str, current_user: CurrentUser) -> None:
    """Check if user is admin/owner of the organization."""
    if current_user.is_superuser:
        return

    org = await get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Owner always has admin access
    if org.owner_id == current_user.id:
        return

    # Check member role
    role = await _get_member_role(db, org_id, current_user.id)
    if role not in ("admin", "owner"):
        raise HTTPException(
            status_code=403,
            detail="Admin or owner role required for this action"
        )


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

    # Check admin permission
    await _require_org_admin(db, org_id, current_user)

    updated = await update_organization(db, org, org_in)
    return OrganizationResponse.model_validate(updated)


# -----------------------------------------------------------------------------
# Member Management Endpoints (Sprint B)
# -----------------------------------------------------------------------------

@router.get("/{org_id}/members", response_model=OrganizationMemberListResponse)
async def list_members(
    org_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> OrganizationMemberListResponse:
    """List all members of an organization.

    Requires admin role or membership in the organization.
    """
    org = await get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if user is member or admin
    role = await _get_member_role(db, org_id, current_user.id)
    is_owner = org.owner_id == current_user.id

    if not role and not is_owner and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not a member of this organization"
        )

    # Query members with user info
    query = (
        select(
            organization_members.c.organization_id,
            organization_members.c.user_id,
            organization_members.c.role,
            User.email.label("user_email"),
            User.full_name.label("user_full_name"),
            User.avatar_url.label("user_avatar_url"),
            User.is_active,
            User.created_at.label("joined_at"),
        )
        .join(User, User.id == organization_members.c.user_id)
        .where(organization_members.c.organization_id == org_id)
        .order_by(User.full_name)
    )

    result = await db.execute(query)
    rows = result.all()

    members = [
        OrganizationMemberResponse(
            organization_id=row.organization_id,
            user_id=row.user_id,
            role=row.role,
            user_email=row.user_email,
            user_full_name=row.user_full_name,
            user_avatar_url=row.user_avatar_url,
            is_active=row.is_active,
            joined_at=row.joined_at,
        )
        for row in rows
    ]

    # Add owner if not in members list
    owner_in_list = any(m.user_id == org.owner_id for m in members)
    if not owner_in_list:
        owner = await db.get(User, org.owner_id)
        if owner:
            members.insert(0, OrganizationMemberResponse(
                organization_id=org_id,
                user_id=owner.id,
                role="owner",
                user_email=owner.email,
                user_full_name=owner.full_name,
                user_avatar_url=owner.avatar_url,
                is_active=owner.is_active,
                joined_at=owner.created_at,
            ))

    return OrganizationMemberListResponse(members=members, total=len(members))


@router.post("/{org_id}/members", response_model=OrganizationMemberResponse, status_code=201)
async def add_member(
    org_id: str,
    member_in: OrganizationMemberCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> OrganizationMemberResponse:
    """Add a member to an organization.

    Requires admin role in the organization.
    """
    await _require_org_admin(db, org_id, current_user)

    # Find user by email
    result = await db.execute(select(User).where(User.email == member_in.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with email {member_in.email} not found"
        )

    # Check if already a member
    existing_role = await _get_member_role(db, org_id, user.id)
    if existing_role:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this organization"
        )

    # Check if user is the owner
    org = await get_organization(db, org_id)
    if org.owner_id == user.id:
        raise HTTPException(
            status_code=400,
            detail="User is the owner of this organization"
        )

    # Add member
    await db.execute(
        organization_members.insert().values(
            organization_id=org_id,
            user_id=user.id,
            role=member_in.role.value,
        )
    )
    await db.commit()

    return OrganizationMemberResponse(
        organization_id=org_id,
        user_id=user.id,
        role=member_in.role.value,
        user_email=user.email,
        user_full_name=user.full_name,
        user_avatar_url=user.avatar_url,
        is_active=user.is_active,
        joined_at=user.created_at,
    )


@router.patch("/{org_id}/members/{user_id}", response_model=OrganizationMemberResponse)
async def update_member_role(
    org_id: str,
    user_id: str,
    member_in: OrganizationMemberUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> OrganizationMemberResponse:
    """Update a member's role in an organization.

    Requires admin role in the organization.
    Cannot change owner's role.
    """
    await _require_org_admin(db, org_id, current_user)

    org = await get_organization(db, org_id)

    # Cannot change owner's role via this endpoint
    if org.owner_id == user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot change owner's role. Transfer ownership instead."
        )

    # Get user
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user is a member
    existing_role = await _get_member_role(db, org_id, user_id)
    if not existing_role:
        raise HTTPException(
            status_code=404,
            detail="User is not a member of this organization"
        )

    # Prevent non-owners from promoting to owner
    if member_in.role.value == "owner" and org.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the owner can promote members to owner"
        )

    # Update role
    await db.execute(
        organization_members.update()
        .where(
            and_(
                organization_members.c.organization_id == org_id,
                organization_members.c.user_id == user_id,
            )
        )
        .values(role=member_in.role.value)
    )
    await db.commit()

    return OrganizationMemberResponse(
        organization_id=org_id,
        user_id=user_id,
        role=member_in.role.value,
        user_email=user.email,
        user_full_name=user.full_name,
        user_avatar_url=user.avatar_url,
        is_active=user.is_active,
        joined_at=user.created_at,
    )


@router.delete("/{org_id}/members/{user_id}", status_code=204)
async def remove_member(
    org_id: str,
    user_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Remove a member from an organization.

    Requires admin role in the organization.
    Cannot remove the owner.
    """
    await _require_org_admin(db, org_id, current_user)

    org = await get_organization(db, org_id)

    # Cannot remove owner
    if org.owner_id == user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove the owner from the organization"
        )

    # Check if user is a member
    existing_role = await _get_member_role(db, org_id, user_id)
    if not existing_role:
        raise HTTPException(
            status_code=404,
            detail="User is not a member of this organization"
        )

    # Remove member
    await db.execute(
        delete(organization_members).where(
            and_(
                organization_members.c.organization_id == org_id,
                organization_members.c.user_id == user_id,
            )
        )
    )
    await db.commit()


@router.patch("/{org_id}/settings", response_model=OrganizationResponse)
async def update_org_settings(
    org_id: str,
    settings_in: OrganizationSettingsUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> OrganizationResponse:
    """Update organization settings.

    Requires admin role in the organization.
    """
    await _require_org_admin(db, org_id, current_user)

    org = await get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Update settings
    update_data = settings_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(org, key, value)

    await db.commit()
    await db.refresh(org)

    return OrganizationResponse.model_validate(org)
