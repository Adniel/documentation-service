"""Classification inheritance service.

Sprint D: Integrated Access Control

Resolves effective classification for content using the full inheritance chain:
Organization → Workspace → Space → Page

Each level can set a default classification that applies to children,
or children can override with their own classification.
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.organization import Organization
from src.db.models.workspace import Workspace
from src.db.models.space import Space
from src.db.models.page import Page
from src.db.models.permission import ClassificationLevel


# Classification level names for display
CLASSIFICATION_NAMES = {
    0: "public",
    1: "internal",
    2: "confidential",
    3: "restricted",
}

# Reverse mapping from string to int
CLASSIFICATION_VALUES = {v: k for k, v in CLASSIFICATION_NAMES.items()}


@dataclass
class ClassificationChain:
    """The full classification inheritance chain with resolved values."""

    # Effective classification (the final resolved value)
    effective: int

    # Individual levels (None means "inherit from parent")
    organization: int
    workspace: Optional[int]
    space: Optional[int]
    page: Optional[int]

    # Which level determined the effective value
    resolved_from: str  # "organization", "workspace", "space", or "page"

    @property
    def effective_name(self) -> str:
        """Get effective classification as string."""
        return CLASSIFICATION_NAMES.get(self.effective, "unknown")


class ClassificationService:
    """Service for resolving classification inheritance."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_organization(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID with organization loaded."""
        result = await self.db.execute(
            select(Workspace)
            .options(selectinload(Workspace.organization))
            .where(Workspace.id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def get_space(self, space_id: str) -> Optional[Space]:
        """Get space by ID with workspace and organization loaded."""
        result = await self.db.execute(
            select(Space)
            .options(
                selectinload(Space.workspace).selectinload(Workspace.organization)
            )
            .where(Space.id == space_id)
        )
        return result.scalar_one_or_none()

    async def get_page(self, page_id: str) -> Optional[Page]:
        """Get page by ID with full hierarchy loaded."""
        result = await self.db.execute(
            select(Page)
            .options(
                selectinload(Page.space)
                .selectinload(Space.workspace)
                .selectinload(Workspace.organization)
            )
            .where(Page.id == page_id)
        )
        return result.scalar_one_or_none()

    def _parse_page_classification(self, classification: Optional[str]) -> Optional[int]:
        """Convert page classification string to int.

        Pages store classification as string ("public", "internal", etc.)
        while other levels use integers.
        """
        if classification is None:
            return None
        return CLASSIFICATION_VALUES.get(classification.lower())

    async def get_effective_classification(self, page: Page) -> int:
        """Get the effective classification for a page.

        Resolution order (first non-None value wins):
        1. Page's own classification
        2. Space's classification
        3. Workspace's default_classification
        4. Organization's default_classification

        Args:
            page: Page model with space, workspace, org relationships loaded

        Returns:
            Integer classification level (0-3)
        """
        # Ensure relationships are loaded
        if not page.space:
            page = await self.get_page(page.id)
            if not page:
                return ClassificationLevel.PUBLIC

        space = page.space
        workspace = space.workspace if space else None
        org = workspace.organization if workspace else None

        # Check page classification
        page_classification = self._parse_page_classification(page.classification)
        if page_classification is not None:
            return page_classification

        # Check space classification
        if space and space.classification is not None:
            return space.classification

        # Check workspace default_classification
        if workspace and workspace.default_classification is not None:
            return workspace.default_classification

        # Check organization default_classification
        if org and org.default_classification is not None:
            return org.default_classification

        # Default to public
        return ClassificationLevel.PUBLIC

    async def get_classification_chain(self, page_id: str) -> Optional[ClassificationChain]:
        """Get the full classification inheritance chain for a page.

        Useful for debugging and displaying where classification comes from.

        Args:
            page_id: The page ID to get chain for

        Returns:
            ClassificationChain with all levels and resolved values,
            or None if page not found
        """
        page = await self.get_page(page_id)
        if not page:
            return None

        space = page.space
        workspace = space.workspace if space else None
        org = workspace.organization if workspace else None

        # Get individual values
        page_classification = self._parse_page_classification(page.classification)
        space_classification = space.classification if space else None
        workspace_classification = workspace.default_classification if workspace else None
        org_classification = org.default_classification if org else 0

        # Determine effective and source
        effective = org_classification
        resolved_from = "organization"

        if workspace_classification is not None:
            effective = workspace_classification
            resolved_from = "workspace"

        if space_classification is not None:
            effective = space_classification
            resolved_from = "space"

        if page_classification is not None:
            effective = page_classification
            resolved_from = "page"

        return ClassificationChain(
            effective=effective,
            organization=org_classification,
            workspace=workspace_classification,
            space=space_classification,
            page=page_classification,
            resolved_from=resolved_from,
        )

    async def get_space_effective_classification(self, space: Space) -> int:
        """Get effective classification for a space.

        Resolution order:
        1. Space's own classification
        2. Workspace's default_classification
        3. Organization's default_classification
        """
        # Ensure relationships are loaded
        if not space.workspace:
            space = await self.get_space(space.id)
            if not space:
                return ClassificationLevel.PUBLIC

        workspace = space.workspace
        org = workspace.organization if workspace else None

        # Check space classification
        if space.classification is not None:
            return space.classification

        # Check workspace default_classification
        if workspace and workspace.default_classification is not None:
            return workspace.default_classification

        # Check organization default_classification
        if org and org.default_classification is not None:
            return org.default_classification

        return ClassificationLevel.PUBLIC

    async def get_workspace_effective_classification(self, workspace: Workspace) -> int:
        """Get effective classification for a workspace.

        Resolution order:
        1. Workspace's default_classification
        2. Organization's default_classification
        """
        # Ensure relationships are loaded
        if not workspace.organization:
            workspace = await self.get_workspace(workspace.id)
            if not workspace:
                return ClassificationLevel.PUBLIC

        org = workspace.organization

        # Check workspace default_classification
        if workspace.default_classification is not None:
            return workspace.default_classification

        # Check organization default_classification
        if org and org.default_classification is not None:
            return org.default_classification

        return ClassificationLevel.PUBLIC

    def check_clearance(self, user_clearance: int, required_classification: int) -> bool:
        """Check if user clearance meets classification requirement.

        Args:
            user_clearance: User's clearance level (0-3)
            required_classification: Required classification level (0-3)

        Returns:
            True if user_clearance >= required_classification
        """
        return user_clearance >= required_classification

    def get_allowed_classifications(self, user_clearance: int) -> list[str]:
        """Get list of classification names a user can access.

        Args:
            user_clearance: User's clearance level (0-3)

        Returns:
            List of classification names the user can access
        """
        return [
            CLASSIFICATION_NAMES[level]
            for level in range(user_clearance + 1)
            if level in CLASSIFICATION_NAMES
        ]


# Convenience function for dependency injection
async def get_classification_service(db: AsyncSession) -> ClassificationService:
    """Get classification service instance."""
    return ClassificationService(db)
