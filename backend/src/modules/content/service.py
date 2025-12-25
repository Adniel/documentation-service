"""Content management service layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import Organization, Workspace, Space, Page, User
from src.db.models.organization import organization_members
from src.modules.content.schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    WorkspaceCreate,
    WorkspaceUpdate,
    SpaceCreate,
    SpaceUpdate,
    PageCreate,
    PageUpdate,
)


# Organization operations
async def create_organization(
    db: AsyncSession, org_in: OrganizationCreate, owner: User
) -> Organization:
    """Create a new organization."""
    org = Organization(
        name=org_in.name,
        slug=org_in.slug,
        description=org_in.description,
        owner_id=owner.id,
    )
    db.add(org)
    await db.flush()  # Get the org.id before adding member

    # Add owner as a member of the organization
    await db.execute(
        organization_members.insert().values(
            organization_id=org.id,
            user_id=owner.id,
            role="owner",
        )
    )

    await db.commit()
    await db.refresh(org)
    return org


async def get_organization(db: AsyncSession, org_id: str) -> Organization | None:
    """Get an organization by ID."""
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    return result.scalar_one_or_none()


async def get_organization_by_slug(db: AsyncSession, slug: str) -> Organization | None:
    """Get an organization by slug."""
    result = await db.execute(select(Organization).where(Organization.slug == slug))
    return result.scalar_one_or_none()


async def list_user_organizations(db: AsyncSession, user_id: str) -> list[Organization]:
    """List organizations a user is a member of."""
    result = await db.execute(
        select(Organization)
        .join(organization_members)
        .where(organization_members.c.user_id == user_id)
    )
    return list(result.scalars().all())


async def update_organization(
    db: AsyncSession, org: Organization, org_in: OrganizationUpdate
) -> Organization:
    """Update an organization."""
    update_data = org_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    await db.commit()
    await db.refresh(org)
    return org


# Workspace operations
async def create_workspace(db: AsyncSession, ws_in: WorkspaceCreate) -> Workspace:
    """Create a new workspace."""
    workspace = Workspace(
        name=ws_in.name,
        slug=ws_in.slug,
        description=ws_in.description,
        organization_id=ws_in.organization_id,
        is_public=ws_in.is_public,
    )
    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)
    return workspace


async def get_workspace(db: AsyncSession, ws_id: str) -> Workspace | None:
    """Get a workspace by ID."""
    result = await db.execute(select(Workspace).where(Workspace.id == ws_id))
    return result.scalar_one_or_none()


async def list_organization_workspaces(
    db: AsyncSession, org_id: str
) -> list[Workspace]:
    """List workspaces in an organization."""
    result = await db.execute(
        select(Workspace).where(Workspace.organization_id == org_id)
    )
    return list(result.scalars().all())


async def update_workspace(
    db: AsyncSession, workspace: Workspace, ws_in: WorkspaceUpdate
) -> Workspace:
    """Update a workspace."""
    update_data = ws_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workspace, field, value)
    await db.commit()
    await db.refresh(workspace)
    return workspace


# Space operations
async def create_space(db: AsyncSession, space_in: SpaceCreate) -> Space:
    """Create a new space."""
    space = Space(
        name=space_in.name,
        slug=space_in.slug,
        description=space_in.description,
        workspace_id=space_in.workspace_id,
        parent_id=space_in.parent_id,
        diataxis_type=space_in.diataxis_type.value,
        classification=space_in.classification.value,
    )
    db.add(space)
    await db.commit()
    await db.refresh(space)
    return space


async def get_space(db: AsyncSession, space_id: str) -> Space | None:
    """Get a space by ID."""
    result = await db.execute(select(Space).where(Space.id == space_id))
    return result.scalar_one_or_none()


async def list_workspace_spaces(db: AsyncSession, workspace_id: str) -> list[Space]:
    """List spaces in a workspace."""
    result = await db.execute(
        select(Space)
        .where(Space.workspace_id == workspace_id)
        .order_by(Space.sort_order)
    )
    return list(result.scalars().all())


async def update_space(db: AsyncSession, space: Space, space_in: SpaceUpdate) -> Space:
    """Update a space."""
    update_data = space_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "diataxis_type" and value:
            setattr(space, field, value.value)
        elif field == "classification" and value is not None:
            setattr(space, field, value.value)
        else:
            setattr(space, field, value)
    await db.commit()
    await db.refresh(space)
    return space


# Page operations
async def create_page(db: AsyncSession, page_in: PageCreate, author_id: str) -> Page:
    """Create a new page."""
    page = Page(
        title=page_in.title,
        slug=page_in.slug,
        space_id=page_in.space_id,
        author_id=author_id,
        parent_id=page_in.parent_id,
        content=page_in.content,
        summary=page_in.summary,
        classification=page_in.classification.value,
    )
    db.add(page)
    await db.commit()
    await db.refresh(page)
    return page


async def get_page(db: AsyncSession, page_id: str) -> Page | None:
    """Get a page by ID."""
    result = await db.execute(select(Page).where(Page.id == page_id))
    return result.scalar_one_or_none()


async def get_page_with_space(db: AsyncSession, page_id: str) -> Page | None:
    """Get a page with its space loaded."""
    result = await db.execute(
        select(Page).where(Page.id == page_id).options(selectinload(Page.space))
    )
    return result.scalar_one_or_none()


async def list_space_pages(db: AsyncSession, space_id: str) -> list[Page]:
    """List pages in a space."""
    result = await db.execute(
        select(Page).where(Page.space_id == space_id).order_by(Page.sort_order)
    )
    return list(result.scalars().all())


async def update_page(db: AsyncSession, page: Page, page_in: PageUpdate) -> Page:
    """Update a page."""
    update_data = page_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "classification" and value is not None:
            setattr(page, field, value.value)
        else:
            setattr(page, field, value)
    await db.commit()
    await db.refresh(page)
    return page


async def delete_page(db: AsyncSession, page: Page) -> None:
    """Soft delete a page."""
    page.is_active = False
    await db.commit()
