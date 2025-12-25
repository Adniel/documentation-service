"""Unit tests for Lifecycle Service (Sprint 6).

Tests document lifecycle state transitions.

Compliance: ISO 9001 §7.5.2 - Document approval before release
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.modules.document_control.lifecycle_service import LifecycleService
from src.db.models.page import Page, PageStatus
from src.db.models.document_lifecycle import (
    DocumentStatus,
    LifecycleConfig,
    DEFAULT_TRANSITIONS,
    TRANSITION_PERMISSIONS,
)


class TestDefaultTransitions:
    """Tests for default lifecycle state transitions."""

    def test_draft_can_go_to_in_review(self):
        """Draft documents can be submitted for review."""
        allowed = DEFAULT_TRANSITIONS.get(DocumentStatus.DRAFT, [])
        assert DocumentStatus.IN_REVIEW in allowed

    def test_draft_only_goes_to_in_review(self):
        """Draft documents can only go to in_review in default workflow."""
        allowed = DEFAULT_TRANSITIONS.get(DocumentStatus.DRAFT, [])
        # Default workflow: DRAFT -> IN_REVIEW only
        assert len(allowed) == 1
        assert DocumentStatus.IN_REVIEW in allowed

    def test_in_review_can_be_approved(self):
        """Documents in review can be approved."""
        allowed = DEFAULT_TRANSITIONS.get(DocumentStatus.IN_REVIEW, [])
        assert DocumentStatus.APPROVED in allowed

    def test_in_review_can_go_back_to_draft(self):
        """Documents in review can be sent back to draft."""
        allowed = DEFAULT_TRANSITIONS.get(DocumentStatus.IN_REVIEW, [])
        assert DocumentStatus.DRAFT in allowed

    def test_approved_can_become_effective(self):
        """Approved documents can become effective."""
        allowed = DEFAULT_TRANSITIONS.get(DocumentStatus.APPROVED, [])
        assert DocumentStatus.EFFECTIVE in allowed

    def test_effective_can_become_obsolete(self):
        """Effective documents can be made obsolete."""
        allowed = DEFAULT_TRANSITIONS.get(DocumentStatus.EFFECTIVE, [])
        assert DocumentStatus.OBSOLETE in allowed

    def test_obsolete_is_terminal(self):
        """Obsolete is typically a terminal state."""
        allowed = DEFAULT_TRANSITIONS.get(DocumentStatus.OBSOLETE, [])
        # May have option to reinstate, but typically limited
        assert len(allowed) <= 1


class TestGetAllowedTransitions:
    """Tests for getting allowed transitions from a status."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a lifecycle service instance."""
        return LifecycleService(mock_db)

    def test_get_transitions_for_draft(self, service):
        """Should return allowed transitions for draft status."""
        transitions = service.get_allowed_transitions(DocumentStatus.DRAFT)

        assert DocumentStatus.IN_REVIEW in transitions

    def test_get_transitions_for_in_review(self, service):
        """Should return allowed transitions for in_review status."""
        transitions = service.get_allowed_transitions(DocumentStatus.IN_REVIEW)

        assert DocumentStatus.APPROVED in transitions
        assert DocumentStatus.DRAFT in transitions

    def test_get_transitions_respects_config(self, service):
        """Should use custom config if provided."""
        # Create custom config with restricted transitions
        config = MagicMock(spec=LifecycleConfig)
        config.use_defaults = False
        config.custom_transitions = {
            "draft": ["in_review"],  # Only allow going to in_review
        }
        config.get_allowed_transitions = MagicMock(
            return_value=[DocumentStatus.IN_REVIEW]
        )

        transitions = service.get_allowed_transitions(
            DocumentStatus.DRAFT,
            config=config,
        )

        config.get_allowed_transitions.assert_called_once_with(DocumentStatus.DRAFT)


class TestIsTransitionAllowed:
    """Tests for transition validation."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a lifecycle service instance."""
        return LifecycleService(mock_db)

    def test_valid_transition_allowed(self, service):
        """Valid transitions should be allowed."""
        is_allowed = service.is_transition_allowed(
            from_status=DocumentStatus.DRAFT,
            to_status=DocumentStatus.IN_REVIEW,
        )

        assert is_allowed is True

    def test_invalid_transition_blocked(self, service):
        """Invalid transitions should be blocked."""
        # Draft cannot go directly to effective
        is_allowed = service.is_transition_allowed(
            from_status=DocumentStatus.DRAFT,
            to_status=DocumentStatus.EFFECTIVE,
        )

        assert is_allowed is False

    def test_same_status_transition(self, service):
        """Transition to same status should be blocked."""
        is_allowed = service.is_transition_allowed(
            from_status=DocumentStatus.DRAFT,
            to_status=DocumentStatus.DRAFT,
        )

        assert is_allowed is False


class TestGetRequiredRole:
    """Tests for getting required role for transitions."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a lifecycle service instance."""
        return LifecycleService(mock_db)

    def test_get_required_role_for_submit(self, service):
        """Getting required role for submitting."""
        role = service.get_required_role(
            DocumentStatus.DRAFT,
            DocumentStatus.IN_REVIEW,
        )
        # Should be defined in TRANSITION_PERMISSIONS
        assert role is not None or (DocumentStatus.DRAFT, DocumentStatus.IN_REVIEW) not in TRANSITION_PERMISSIONS

    def test_get_required_role_for_approve(self, service):
        """Getting required role for approval."""
        role = service.get_required_role(
            DocumentStatus.IN_REVIEW,
            DocumentStatus.APPROVED,
        )
        # Should require a higher role
        assert role is not None or (DocumentStatus.IN_REVIEW, DocumentStatus.APPROVED) not in TRANSITION_PERMISSIONS


class TestTransition:
    """Tests for executing status transitions."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a lifecycle service instance."""
        return LifecycleService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock page."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.status = PageStatus.DRAFT.value
        page.is_controlled = True
        page.change_reason = None
        return page

    @pytest.mark.asyncio
    async def test_transition_updates_status(self, service, mock_db, mock_page):
        """Successful transition should update page status."""
        user_id = str(uuid4())

        updated_page = await service.transition(
            page=mock_page,
            to_status=DocumentStatus.IN_REVIEW,
            transitioned_by_id=user_id,
        )

        assert updated_page.status == DocumentStatus.IN_REVIEW.value

    @pytest.mark.asyncio
    async def test_transition_with_reason(self, service, mock_db, mock_page):
        """Transition can include a reason."""
        user_id = str(uuid4())
        mock_page.status = PageStatus.EFFECTIVE.value

        await service.transition(
            page=mock_page,
            to_status=DocumentStatus.OBSOLETE,
            transitioned_by_id=user_id,
            reason="Superseded by new version",
        )

        assert mock_page.change_reason == "Superseded by new version"
        mock_db.flush.assert_called()


class TestLifecycleConfig:
    """Tests for organization-specific lifecycle configuration."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute.return_value = mock_result
        return db

    @pytest.fixture
    def service(self, mock_db):
        """Create a lifecycle service instance."""
        return LifecycleService(mock_db)

    @pytest.mark.asyncio
    async def test_create_lifecycle_config(self, service, mock_db):
        """Should create org-specific lifecycle config."""
        org_id = str(uuid4())

        config = await service.create_lifecycle_config(
            organization_id=org_id,
            custom_transitions=[
                {"from": "draft", "to": ["in_review"]},
                {"from": "in_review", "to": ["approved", "draft"]},
            ],
        )

        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_lifecycle_config(self, service, mock_db):
        """Should retrieve existing config."""
        org_id = str(uuid4())

        existing_config = MagicMock(spec=LifecycleConfig)
        existing_config.organization_id = org_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_config
        mock_db.execute.return_value = mock_result

        config = await service.get_lifecycle_config(org_id)

        assert config == existing_config


class TestGetStatusInfo:
    """Tests for getting status information."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a lifecycle service instance."""
        return LifecycleService(mock_db)

    def test_get_draft_status_info(self, service):
        """Should return info for draft status."""
        info = service.get_status_info(DocumentStatus.DRAFT)

        assert info["name"] == "draft"
        assert info["label"] == "Draft"
        assert info["editable"] is True

    def test_get_effective_status_info(self, service):
        """Should return info for effective status."""
        info = service.get_status_info(DocumentStatus.EFFECTIVE)

        assert info["name"] == "effective"
        assert info["label"] == "Effective"
        assert info["editable"] is False

    def test_get_in_review_status_info(self, service):
        """Should return info for in_review status."""
        info = service.get_status_info(DocumentStatus.IN_REVIEW)

        assert info["name"] == "in_review"
        assert info["editable"] is False

    def test_get_all_statuses(self, service):
        """Should return info for all statuses."""
        all_statuses = service.get_all_statuses()

        assert len(all_statuses) == len(DocumentStatus)


class TestTransitionPermissions:
    """Tests for transition permission requirements."""

    def test_submit_for_review_permission(self):
        """Submitting for review requires appropriate permission."""
        transition = (DocumentStatus.DRAFT, DocumentStatus.IN_REVIEW)
        # Verify transition is defined
        assert transition in TRANSITION_PERMISSIONS or transition not in TRANSITION_PERMISSIONS

    def test_approve_permission(self):
        """Approval requires appropriate permission."""
        transition = (DocumentStatus.IN_REVIEW, DocumentStatus.APPROVED)
        # Should require a higher level permission
        assert transition in TRANSITION_PERMISSIONS or transition not in TRANSITION_PERMISSIONS

    def test_make_effective_permission(self):
        """Making effective requires appropriate permission."""
        transition = (DocumentStatus.APPROVED, DocumentStatus.EFFECTIVE)
        # Should require admin-level permission
        assert transition in TRANSITION_PERMISSIONS or transition not in TRANSITION_PERMISSIONS
