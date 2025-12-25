"""Lifecycle service for document status transitions.

Manages document lifecycle states and validates transitions.

Compliance: ISO 9001 §7.5.2 - Documents must be approved before release
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.page import Page, PageStatus
from src.db.models.document_lifecycle import (
    DocumentStatus,
    LifecycleConfig,
    DEFAULT_TRANSITIONS,
    TRANSITION_PERMISSIONS,
)
from src.db.models.permission import Role
from src.db.models.user import User


class LifecycleService:
    """Service for managing document lifecycle transitions.

    Provides:
    - Transition validation (allowed transitions, permissions)
    - Custom lifecycle configuration per organization
    - Status change tracking
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_lifecycle_config(
        self,
        organization_id: str,
    ) -> LifecycleConfig | None:
        """Get lifecycle configuration for an organization.

        Args:
            organization_id: Organization UUID

        Returns:
            LifecycleConfig if exists, None otherwise
        """
        result = await self.db.execute(
            select(LifecycleConfig).where(
                LifecycleConfig.organization_id == organization_id
            )
        )
        return result.scalar_one_or_none()

    def get_allowed_transitions(
        self,
        from_status: DocumentStatus,
        config: LifecycleConfig | None = None,
    ) -> list[DocumentStatus]:
        """Get allowed transitions from a status.

        Args:
            from_status: Current status
            config: Optional lifecycle config (uses defaults if None)

        Returns:
            List of allowed target statuses
        """
        if config and not config.use_defaults and config.custom_transitions:
            return config.get_allowed_transitions(from_status)
        return DEFAULT_TRANSITIONS.get(from_status, [])

    def get_required_role(
        self,
        from_status: DocumentStatus,
        to_status: DocumentStatus,
        config: LifecycleConfig | None = None,
    ) -> Role | None:
        """Get required role for a transition.

        Args:
            from_status: Current status
            to_status: Target status
            config: Optional lifecycle config

        Returns:
            Required Role, or None if transition not allowed
        """
        if config and not config.use_defaults and config.custom_transitions:
            return config.get_transition_role(from_status, to_status)
        return TRANSITION_PERMISSIONS.get((from_status, to_status))

    def is_transition_allowed(
        self,
        from_status: DocumentStatus,
        to_status: DocumentStatus,
        config: LifecycleConfig | None = None,
    ) -> bool:
        """Check if a transition is allowed.

        Args:
            from_status: Current status
            to_status: Target status
            config: Optional lifecycle config

        Returns:
            True if transition is allowed
        """
        allowed = self.get_allowed_transitions(from_status, config)
        return to_status in allowed

    async def can_transition(
        self,
        page: Page,
        to_status: DocumentStatus,
        user: User,
        user_role: Role,
    ) -> tuple[bool, str | None]:
        """Check if a user can perform a status transition.

        Args:
            page: Page to transition
            to_status: Target status
            user: User performing transition
            user_role: User's effective role on the page

        Returns:
            Tuple of (can_transition, reason_if_not)
        """
        from_status = DocumentStatus(page.status)

        # Get org config if available
        config = None
        if hasattr(page, 'space') and page.space:
            if hasattr(page.space, 'workspace') and page.space.workspace:
                config = await self.get_lifecycle_config(
                    page.space.workspace.organization_id
                )

        # Check if transition is allowed
        if not self.is_transition_allowed(from_status, to_status, config):
            return (
                False,
                f"Transition from {from_status.value} to {to_status.value} is not allowed",
            )

        # Check permission
        required_role = self.get_required_role(from_status, to_status, config)
        if required_role and not user_role.can_perform(required_role):
            return (
                False,
                f"Role '{required_role.name}' required for this transition",
            )

        # Superusers can always transition
        if user.is_superuser:
            return (True, None)

        return (True, None)

    async def transition(
        self,
        page: Page,
        to_status: DocumentStatus,
        transitioned_by_id: str,
        reason: str | None = None,
    ) -> Page:
        """Perform a status transition.

        Note: This method does NOT validate permissions. Use can_transition()
        first to verify the transition is allowed.

        Args:
            page: Page to transition
            to_status: Target status
            transitioned_by_id: User performing transition
            reason: Optional reason for transition

        Returns:
            Updated page
        """
        old_status = page.status
        page.status = to_status.value

        # Store transition reason in change_reason if significant
        if reason and to_status in (DocumentStatus.OBSOLETE, DocumentStatus.APPROVED):
            page.change_reason = reason

        await self.db.flush()
        return page

    async def create_lifecycle_config(
        self,
        organization_id: str,
        custom_states: list[dict] | None = None,
        custom_transitions: list[dict] | None = None,
        use_defaults: bool = True,
    ) -> LifecycleConfig:
        """Create or update lifecycle configuration for an organization.

        Args:
            organization_id: Organization UUID
            custom_states: Optional custom state definitions
            custom_transitions: Optional custom transition rules
            use_defaults: Whether to use default states/transitions

        Returns:
            Created or updated config
        """
        existing = await self.get_lifecycle_config(organization_id)

        if existing:
            existing.custom_states = custom_states
            existing.custom_transitions = custom_transitions
            existing.use_defaults = use_defaults
            await self.db.flush()
            return existing

        config = LifecycleConfig(
            organization_id=organization_id,
            custom_states=custom_states,
            custom_transitions=custom_transitions,
            use_defaults=use_defaults,
        )
        self.db.add(config)
        await self.db.flush()
        return config

    def get_status_info(self, status: DocumentStatus) -> dict:
        """Get information about a status.

        Args:
            status: Document status

        Returns:
            Dictionary with status details
        """
        status_info = {
            DocumentStatus.DRAFT: {
                "name": "draft",
                "label": "Draft",
                "editable": True,
                "visible_to_viewers": False,
                "description": "Work in progress, not yet submitted for review",
            },
            DocumentStatus.IN_REVIEW: {
                "name": "in_review",
                "label": "In Review",
                "editable": False,
                "visible_to_viewers": False,
                "description": "Submitted for approval, awaiting review",
            },
            DocumentStatus.APPROVED: {
                "name": "approved",
                "label": "Approved",
                "editable": False,
                "visible_to_viewers": True,
                "description": "Approved, awaiting effective date",
            },
            DocumentStatus.EFFECTIVE: {
                "name": "effective",
                "label": "Effective",
                "editable": False,
                "visible_to_viewers": True,
                "description": "Current active version",
            },
            DocumentStatus.OBSOLETE: {
                "name": "obsolete",
                "label": "Obsolete",
                "editable": False,
                "visible_to_viewers": True,
                "description": "Superseded or retired document",
            },
        }
        return status_info.get(status, {"name": status.value, "label": status.value})

    def get_all_statuses(self) -> list[dict]:
        """Get information about all statuses.

        Returns:
            List of status information dictionaries
        """
        return [self.get_status_info(s) for s in DocumentStatus]
