"""Unit tests for Approval Service (Sprint 6).

Tests multi-step approval workflows.

Compliance: ISO 9001 §7.5.2 - Documents must be approved before release
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.modules.document_control.approval_service import ApprovalService
from src.db.models.approval import ApprovalMatrix, ApprovalRecord, ApprovalDecision
from src.db.models.change_request import ChangeRequest, ChangeRequestStatus
from src.db.models.page import Page


class TestGetApplicableMatrix:
    """Tests for finding applicable approval matrix."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create an approval service instance."""
        return ApprovalService(mock_db)

    @pytest.mark.asyncio
    async def test_find_type_specific_matrix(self, service, mock_db):
        """Should find matrix specific to document type."""
        org_id = str(uuid4())

        # Set up type-specific matrix
        sop_matrix = MagicMock(spec=ApprovalMatrix)
        sop_matrix.applicable_document_types = ["sop", "procedure"]
        sop_matrix.is_active = True

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sop_matrix]
        mock_db.execute.return_value = mock_result

        matrix = await service.get_applicable_matrix(
            organization_id=org_id,
            document_type="sop",
        )

        assert matrix == sop_matrix

    @pytest.mark.asyncio
    async def test_fallback_to_catchall_matrix(self, service, mock_db):
        """Should use catch-all matrix if no type-specific match."""
        org_id = str(uuid4())

        # Set up catch-all matrix
        catchall_matrix = MagicMock(spec=ApprovalMatrix)
        catchall_matrix.applicable_document_types = None  # Catch-all
        catchall_matrix.is_active = True

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [catchall_matrix]
        mock_db.execute.return_value = mock_result

        matrix = await service.get_applicable_matrix(
            organization_id=org_id,
            document_type="guidance",
        )

        assert matrix == catchall_matrix

    @pytest.mark.asyncio
    async def test_no_matrix_returns_none(self, service, mock_db):
        """Should return None if no matrix found."""
        org_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        matrix = await service.get_applicable_matrix(
            organization_id=org_id,
            document_type="sop",
        )

        assert matrix is None


class TestInitiateApproval:
    """Tests for initiating approval workflows."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create an approval service instance."""
        return ApprovalService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock page with organization context."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.document_type = "sop"
        page.space = MagicMock()
        page.space.workspace = MagicMock()
        page.space.workspace.organization_id = str(uuid4())
        return page

    @pytest.fixture
    def mock_change_request(self, mock_page):
        """Create a mock change request."""
        cr = MagicMock(spec=ChangeRequest)
        cr.id = str(uuid4())
        cr.page = mock_page
        cr.status = ChangeRequestStatus.SUBMITTED.value
        cr.approval_matrix_id = None
        cr.current_approval_step = 0
        cr.approval_status = "pending"
        return cr

    @pytest.mark.asyncio
    async def test_initiate_with_matrix(self, service, mock_db, mock_change_request):
        """Should initialize workflow with matrix if found."""
        # Set up matrix
        matrix = MagicMock(spec=ApprovalMatrix)
        matrix.id = str(uuid4())

        # Mock get_applicable_matrix
        service.get_applicable_matrix = AsyncMock(return_value=matrix)

        user_id = str(uuid4())
        cr = await service.initiate_approval(
            change_request=mock_change_request,
            initiated_by_id=user_id,
        )

        assert cr.approval_matrix_id == matrix.id
        assert cr.current_approval_step == 1
        assert cr.approval_status == "in_progress"
        assert cr.status == ChangeRequestStatus.IN_REVIEW.value

    @pytest.mark.asyncio
    async def test_initiate_without_matrix(self, service, mock_db, mock_change_request):
        """Should use simple approval if no matrix found."""
        # No matrix
        service.get_applicable_matrix = AsyncMock(return_value=None)

        user_id = str(uuid4())
        cr = await service.initiate_approval(
            change_request=mock_change_request,
            initiated_by_id=user_id,
        )

        assert cr.approval_matrix_id is None
        assert cr.approval_status == "pending"
        assert cr.status == ChangeRequestStatus.IN_REVIEW.value


class TestRecordApproval:
    """Tests for recording approval decisions."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create an approval service instance."""
        return ApprovalService(mock_db)

    @pytest.fixture
    def mock_matrix(self):
        """Create a mock approval matrix."""
        matrix = MagicMock(spec=ApprovalMatrix)
        matrix.id = str(uuid4())
        matrix.steps = [
            {"order": 1, "name": "Technical Review", "role": "reviewer", "required": True},
            {"order": 2, "name": "Quality Approval", "role": "admin", "required": True},
        ]
        matrix.get_step = lambda n: next(
            (s for s in matrix.steps if s["order"] == n), None
        )
        matrix.get_total_steps = lambda: len(matrix.steps)
        return matrix

    @pytest.fixture
    def mock_cr_with_matrix(self, mock_matrix):
        """Create a CR with approval matrix."""
        cr = MagicMock(spec=ChangeRequest)
        cr.id = str(uuid4())
        cr.approval_matrix = mock_matrix
        cr.approval_matrix_id = mock_matrix.id
        cr.current_approval_step = 1
        cr.approval_status = "in_progress"
        cr.status = ChangeRequestStatus.IN_REVIEW.value
        return cr

    @pytest.mark.asyncio
    async def test_approve_advances_step(
        self, service, mock_db, mock_cr_with_matrix, mock_matrix
    ):
        """Approval should advance to next step."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_cr_with_matrix
        mock_db.execute.return_value = mock_result

        approver_id = str(uuid4())

        cr, is_complete = await service.record_approval(
            change_request_id=str(mock_cr_with_matrix.id),
            approver_id=approver_id,
            decision=ApprovalDecision.APPROVED,
        )

        assert cr.current_approval_step == 2
        assert is_complete is False
        mock_db.add.assert_called()  # Should add approval record

    @pytest.mark.asyncio
    async def test_final_approval_completes_workflow(
        self, service, mock_db, mock_cr_with_matrix, mock_matrix
    ):
        """Final approval should complete the workflow."""
        mock_cr_with_matrix.current_approval_step = 2  # Last step

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_cr_with_matrix
        mock_db.execute.return_value = mock_result

        approver_id = str(uuid4())

        cr, is_complete = await service.record_approval(
            change_request_id=str(mock_cr_with_matrix.id),
            approver_id=approver_id,
            decision=ApprovalDecision.APPROVED,
        )

        assert is_complete is True
        assert cr.approval_status == "approved"
        assert cr.status == ChangeRequestStatus.APPROVED.value

    @pytest.mark.asyncio
    async def test_rejection_completes_workflow(
        self, service, mock_db, mock_cr_with_matrix, mock_matrix
    ):
        """Rejection should complete workflow as rejected."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_cr_with_matrix
        mock_db.execute.return_value = mock_result

        approver_id = str(uuid4())

        cr, is_complete = await service.record_approval(
            change_request_id=str(mock_cr_with_matrix.id),
            approver_id=approver_id,
            decision=ApprovalDecision.REJECTED,
            comment="Does not meet requirements",
        )

        assert is_complete is True
        assert cr.approval_status == "rejected"
        assert cr.status == ChangeRequestStatus.CHANGES_REQUESTED.value

    @pytest.mark.asyncio
    async def test_simple_approval_without_matrix(self, service, mock_db):
        """Simple approval without matrix."""
        cr = MagicMock(spec=ChangeRequest)
        cr.id = str(uuid4())
        cr.approval_matrix = None
        cr.approval_status = "pending"
        cr.status = ChangeRequestStatus.IN_REVIEW.value

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = cr
        mock_db.execute.return_value = mock_result

        approver_id = str(uuid4())

        result_cr, is_complete = await service.record_approval(
            change_request_id=str(cr.id),
            approver_id=approver_id,
            decision=ApprovalDecision.APPROVED,
        )

        assert is_complete is True
        assert result_cr.approval_status == "approved"


class TestSkipOptionalStep:
    """Tests for skipping optional approval steps."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create an approval service instance."""
        return ApprovalService(mock_db)

    @pytest.mark.asyncio
    async def test_skip_optional_step(self, service, mock_db):
        """Should be able to skip optional steps."""
        # Set up matrix with optional step
        matrix = MagicMock(spec=ApprovalMatrix)
        matrix.steps = [
            {"order": 1, "name": "Technical Review", "required": True},
            {"order": 2, "name": "Optional Legal Review", "required": False},
            {"order": 3, "name": "Final Approval", "required": True},
        ]
        matrix.get_step = lambda n: next(
            (s for s in matrix.steps if s["order"] == n), None
        )
        matrix.get_total_steps = lambda: len(matrix.steps)

        cr = MagicMock(spec=ChangeRequest)
        cr.id = str(uuid4())
        cr.approval_matrix = matrix
        cr.current_approval_step = 2  # On optional step
        cr.approval_status = "in_progress"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = cr
        mock_db.execute.return_value = mock_result

        user_id = str(uuid4())

        result_cr, is_complete = await service.skip_optional_step(
            change_request_id=str(cr.id),
            skipped_by_id=user_id,
            reason="Not applicable",
        )

        # Should record a SKIPPED decision
        mock_db.add.assert_called()


class TestGetPendingApprovals:
    """Tests for listing pending approvals."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create an approval service instance."""
        return ApprovalService(mock_db)

    @pytest.mark.asyncio
    async def test_get_pending_approvals(self, service, mock_db):
        """Should return CRs pending approval."""
        user_id = str(uuid4())

        cr1 = MagicMock(spec=ChangeRequest)
        cr1.id = str(uuid4())
        cr1.status = ChangeRequestStatus.IN_REVIEW.value
        cr1.approval_status = "in_progress"

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [cr1]
        mock_db.execute.return_value = mock_result

        pending = await service.get_pending_approvals(user_id)

        assert len(pending) == 1


class TestApprovalHistory:
    """Tests for approval history retrieval."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create an approval service instance."""
        return ApprovalService(mock_db)

    @pytest.mark.asyncio
    async def test_get_approval_history(self, service, mock_db):
        """Should return approval records in order."""
        cr_id = str(uuid4())

        record1 = MagicMock(spec=ApprovalRecord)
        record1.step_order = 1
        record1.decision = ApprovalDecision.APPROVED.value
        record1.decided_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [record1]
        mock_db.execute.return_value = mock_result

        history = await service.get_approval_history(cr_id)

        assert len(history) == 1


class TestCreateApprovalMatrix:
    """Tests for creating approval matrices."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create an approval service instance."""
        return ApprovalService(mock_db)

    @pytest.mark.asyncio
    async def test_create_matrix_with_steps(self, service, mock_db):
        """Should create matrix with approval steps."""
        org_id = str(uuid4())

        steps = [
            {"order": 1, "name": "Author Review", "role": "editor", "required": True},
            {"order": 2, "name": "Technical Review", "role": "reviewer", "required": True},
            {"order": 3, "name": "QA Approval", "role": "admin", "required": True},
        ]

        matrix = await service.create_approval_matrix(
            organization_id=org_id,
            name="Standard SOP Approval",
            steps=steps,
            description="Three-step approval for SOPs",
            applicable_document_types=["sop", "procedure"],
        )

        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()


class TestWorkflowStatus:
    """Tests for getting workflow status."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create an approval service instance."""
        return ApprovalService(mock_db)

    @pytest.mark.asyncio
    async def test_get_workflow_status_with_matrix(self, service, mock_db):
        """Should return detailed workflow status."""
        # Set up matrix
        matrix = MagicMock(spec=ApprovalMatrix)
        matrix.name = "Standard Approval"
        matrix.steps = [
            {"order": 1, "name": "Technical Review", "role": "reviewer", "required": True},
            {"order": 2, "name": "Final Approval", "role": "admin", "required": True},
        ]
        matrix.get_total_steps = lambda: len(matrix.steps)

        cr = MagicMock(spec=ChangeRequest)
        cr.id = str(uuid4())
        cr.approval_matrix = matrix
        cr.current_approval_step = 1
        cr.approval_status = "in_progress"

        # Mock approval history (empty for now)
        service.get_approval_history = AsyncMock(return_value=[])

        status = await service.get_workflow_status(cr)

        assert status["total_steps"] == 2
        assert status["current_step"] == 1
        assert status["matrix_name"] == "Standard Approval"
        assert len(status["steps"]) == 2

    @pytest.mark.asyncio
    async def test_get_workflow_status_simple(self, service, mock_db):
        """Should return simple status without matrix."""
        cr = MagicMock(spec=ChangeRequest)
        cr.id = str(uuid4())
        cr.approval_matrix = None
        cr.current_approval_step = 0
        cr.approval_status = "pending"
        cr.reviewed_at = None
        cr.review_comment = None

        service.get_approval_history = AsyncMock(return_value=[])

        status = await service.get_workflow_status(cr)

        assert status["total_steps"] == 1
        assert status["steps"][0]["name"] == "Review"
