"""Navigation service for building hierarchical tree structures."""

from typing import Any

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import Organization, Workspace, Space, Page


# Classification levels in order of access (index = clearance level)
CLASSIFICATION_ORDER = ["public", "internal", "confidential", "restricted"]


def get_allowed_classifications(user_clearance: int) -> list[str]:
    """Get list of classification values a user can access based on clearance level.

    Args:
        user_clearance: User's clearance level (0-3)

    Returns:
        List of classification strings the user can access (for pages)
    """
    return CLASSIFICATION_ORDER[:user_clearance + 1]


def get_allowed_classification_ints(user_clearance: int) -> list[int]:
    """Get list of classification integers a user can access based on clearance level.

    Args:
        user_clearance: User's clearance level (0-3)

    Returns:
        List of classification integers the user can access (for spaces)
    """
    return list(range(user_clearance + 1))


async def get_workspace_tree(
    db: AsyncSession,
    workspace_id: str,
    user_clearance: int,
    include_pages: bool = True,
    max_depth: int = 3,
) -> dict[str, Any] | None:
    """Build navigation tree for a workspace.

    Args:
        db: Database session
        workspace_id: Workspace ID
        user_clearance: User's classification clearance level
        include_pages: Whether to include pages in the tree
        max_depth: Maximum depth of nested spaces to include

    Returns:
        Tree structure with spaces and pages
    """
    # Get workspace with organization
    result = await db.execute(
        select(Workspace)
        .where(Workspace.id == workspace_id)
        .options(selectinload(Workspace.organization))
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        return None

    # Get all spaces in workspace (filtered by classification)
    # Spaces use integer classification (0-3)
    allowed_space_classifications = get_allowed_classification_ints(user_clearance)
    spaces_result = await db.execute(
        select(Space)
        .where(
            and_(
                Space.workspace_id == workspace_id,
                Space.is_active == True,  # noqa: E712
                Space.classification.in_(allowed_space_classifications),
            )
        )
        .order_by(Space.sort_order, Space.name)
    )
    spaces = list(spaces_result.scalars().all())

    # Build space tree
    space_tree = _build_space_tree(spaces, parent_id=None, max_depth=max_depth)

    # If including pages, fetch them
    if include_pages:
        # Get all pages in workspace (filtered by classification)
        # Pages use string classification ('public', 'internal', etc.)
        allowed_page_classifications = get_allowed_classifications(user_clearance)
        pages_result = await db.execute(
            select(Page)
            .where(
                and_(
                    Page.space_id.in_([s.id for s in spaces]),
                    Page.is_active == True,  # noqa: E712
                    Page.classification.in_(allowed_page_classifications),
                )
            )
            .order_by(Page.sort_order, Page.title)
        )
        pages = list(pages_result.scalars().all())

        # Add pages to their respective spaces
        _add_pages_to_tree(space_tree, pages)

    return {
        "id": workspace.id,
        "name": workspace.name,
        "slug": workspace.slug,
        "type": "workspace",
        "organization": {
            "id": workspace.organization.id,
            "name": workspace.organization.name,
            "slug": workspace.organization.slug,
        },
        "children": space_tree,
    }


def _build_space_tree(
    spaces: list[Space],
    parent_id: str | None,
    max_depth: int,
    current_depth: int = 0,
) -> list[dict[str, Any]]:
    """Recursively build space tree structure."""
    if current_depth >= max_depth:
        return []

    tree = []
    for space in spaces:
        if space.parent_id == parent_id:
            node = {
                "id": space.id,
                "name": space.name,
                "slug": space.slug,
                "type": "space",
                "diataxis_type": space.diataxis_type,
                "classification": space.classification,
                "children": _build_space_tree(
                    spaces, space.id, max_depth, current_depth + 1
                ),
                "pages": [],  # Will be populated if include_pages=True
            }
            tree.append(node)
    return tree


def _add_pages_to_tree(tree: list[dict], pages: list[Page]) -> None:
    """Add pages to their respective spaces in the tree."""
    # Create a map of space_id to pages
    pages_by_space: dict[str, list[dict]] = {}
    for page in pages:
        if page.space_id not in pages_by_space:
            pages_by_space[page.space_id] = []
        pages_by_space[page.space_id].append({
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "type": "page",
            "status": page.status,
            "version": page.version,
            "document_number": page.document_number,
        })

    # Recursively add pages to tree nodes
    def add_to_node(nodes: list[dict]) -> None:
        for node in nodes:
            if node["type"] == "space":
                node["pages"] = pages_by_space.get(node["id"], [])
                add_to_node(node.get("children", []))

    add_to_node(tree)


async def get_space_tree(
    db: AsyncSession,
    space_id: str,
    user_clearance: int,
    include_children: bool = True,
) -> dict[str, Any] | None:
    """Get a space with its children and pages."""
    result = await db.execute(
        select(Space)
        .where(
            and_(
                Space.id == space_id,
                Space.is_active == True,  # noqa: E712
            )
        )
        .options(selectinload(Space.workspace))
    )
    space = result.scalar_one_or_none()

    # Spaces use integer classification, pages use string classification
    allowed_space_classifications = get_allowed_classification_ints(user_clearance)
    allowed_page_classifications = get_allowed_classifications(user_clearance)

    if not space or space.classification not in allowed_space_classifications:
        return None

    # Get pages in this space
    pages_result = await db.execute(
        select(Page)
        .where(
            and_(
                Page.space_id == space_id,
                Page.is_active == True,  # noqa: E712
                Page.classification.in_(allowed_page_classifications),
            )
        )
        .order_by(Page.sort_order, Page.title)
    )
    pages = list(pages_result.scalars().all())

    tree = {
        "id": space.id,
        "name": space.name,
        "slug": space.slug,
        "description": space.description,
        "type": "space",
        "diataxis_type": space.diataxis_type,
        "classification": space.classification,
        "workspace_id": space.workspace_id,
        "pages": [
            {
                "id": p.id,
                "title": p.title,
                "slug": p.slug,
                "status": p.status,
                "version": p.version,
            }
            for p in pages
        ],
        "children": [],
    }

    if include_children:
        # Get child spaces
        children_result = await db.execute(
            select(Space)
            .where(
                and_(
                    Space.parent_id == space_id,
                    Space.is_active == True,  # noqa: E712
                    Space.classification.in_(allowed_space_classifications),
                )
            )
            .order_by(Space.sort_order, Space.name)
        )
        children = list(children_result.scalars().all())

        tree["children"] = [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "type": "space",
                "diataxis_type": c.diataxis_type,
            }
            for c in children
        ]

    return tree


async def get_breadcrumbs(
    db: AsyncSession,
    page_id: str,
    resource_type: str = "page",
) -> list[dict[str, Any]] | None:
    """Build breadcrumb trail for a page or space.

    Returns:
        List of breadcrumb items from organization to the resource
    """
    breadcrumbs = []

    if resource_type == "page":
        # Get page with space
        result = await db.execute(
            select(Page)
            .where(Page.id == page_id)
            .options(
                selectinload(Page.space).selectinload(Space.workspace).selectinload(
                    Workspace.organization
                )
            )
        )
        page = result.scalar_one_or_none()

        if not page:
            return None

        space = page.space
        workspace = space.workspace
        organization = workspace.organization

        # Build breadcrumbs from top to bottom
        breadcrumbs = [
            {"type": "organization", "id": organization.id, "name": organization.name, "slug": organization.slug},
            {"type": "workspace", "id": workspace.id, "name": workspace.name, "slug": workspace.slug},
            {"type": "space", "id": space.id, "name": space.name, "slug": space.slug},
            {"type": "page", "id": page.id, "name": page.title, "slug": page.slug},
        ]

        # Add parent spaces if nested
        if space.parent_id:
            parent_crumbs = await _get_parent_spaces(db, space.parent_id)
            # Insert parent spaces between workspace and current space
            breadcrumbs = breadcrumbs[:2] + parent_crumbs + breadcrumbs[2:]

    elif resource_type == "space":
        result = await db.execute(
            select(Space)
            .where(Space.id == page_id)
            .options(
                selectinload(Space.workspace).selectinload(Workspace.organization)
            )
        )
        space = result.scalar_one_or_none()

        if not space:
            return None

        workspace = space.workspace
        organization = workspace.organization

        breadcrumbs = [
            {"type": "organization", "id": organization.id, "name": organization.name, "slug": organization.slug},
            {"type": "workspace", "id": workspace.id, "name": workspace.name, "slug": workspace.slug},
            {"type": "space", "id": space.id, "name": space.name, "slug": space.slug},
        ]

        if space.parent_id:
            parent_crumbs = await _get_parent_spaces(db, space.parent_id)
            breadcrumbs = breadcrumbs[:2] + parent_crumbs + breadcrumbs[2:]

    return breadcrumbs


async def _get_parent_spaces(db: AsyncSession, space_id: str) -> list[dict]:
    """Recursively get parent spaces for breadcrumbs."""
    parents = []
    current_id = space_id

    while current_id:
        result = await db.execute(select(Space).where(Space.id == current_id))
        space = result.scalar_one_or_none()
        if not space:
            break

        parents.insert(0, {
            "type": "space",
            "id": space.id,
            "name": space.name,
            "slug": space.slug,
        })
        current_id = space.parent_id

    return parents


async def get_recent_pages(
    db: AsyncSession,
    user_id: str,
    user_clearance: int,
    limit: int = 10,
    workspace_id: str | None = None,
) -> list[dict[str, Any]]:
    """Get recently updated pages accessible to the user."""
    allowed_classifications = get_allowed_classifications(user_clearance)
    query = (
        select(Page)
        .where(
            and_(
                Page.is_active == True,  # noqa: E712
                Page.classification.in_(allowed_classifications),
            )
        )
        .order_by(Page.updated_at.desc())
        .limit(limit)
    )

    if workspace_id:
        # Filter by workspace through space relationship
        query = query.options(selectinload(Page.space)).where(
            Page.space.has(Space.workspace_id == workspace_id)
        )

    result = await db.execute(query)
    pages = list(result.scalars().all())

    return [
        {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "status": p.status,
            "version": p.version,
            "space_id": p.space_id,
            "updated_at": p.updated_at.isoformat(),
        }
        for p in pages
    ]
