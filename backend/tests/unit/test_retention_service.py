"""Unit tests for Retention Service (Sprint 6).

Tests retention policy management and document disposition.

Compliance: ISO 15489 - Records management retention requirements
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.modules.document_control.retention_service import RetentionService
from src.db.models.retention_policy import (
    RetentionPolicy,
    DispositionMethod,
    ExpirationAction,
)
from src.db.models.page import Page, PageStatus


class TestApplyRetentionPolicy:
    """Tests for applying retention policies to documents."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a retention service instance."""
        return RetentionService(mock_db)

    @pytest.fixture
    def mock_policy(self):
        """Create a mock retention policy."""
        policy = MagicMock(spec=RetentionPolicy)
        policy.id = str(uuid4())
        policy.retention_years = 5
        policy.retention_from = "effective_date"
        policy.disposition_method = DispositionMethod.ARCHIVE.value
        return policy

    @pytest.fixture
    def mock_page(self):
        """Create a mock page."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.retention_policy_id = None
        page.disposition_date = None
        page.effective_date = datetime.now(timezone.utc)
        page.created_at = datetime.now(timezone.utc)
        page.status = PageStatus.EFFECTIVE.value
        return page

    @pytest.mark.asyncio
    async def test_apply_policy_sets_disposition_date(
        self, service, mock_db, mock_page, mock_policy
    ):
        """Should calculate disposition date from effective date."""
        page = await service.apply_retention_policy(
            page=mock_page,
            policy=mock_policy,
        )

        assert page.retention_policy_id == mock_policy.id
        assert page.disposition_date is not None

        # Should be approximately 5 years from effective date
        expected = mock_page.effective_date + timedelta(days=5 * 365)
        diff = abs((page.disposition_date - expected).days)
        assert diff < 5  # Allow for leap years

    @pytest.mark.asyncio
    async def test_apply_policy_without_effective_date(
        self, service, mock_db, mock_page, mock_policy
    ):
        """Should use created_at if no effective date."""
        mock_page.effective_date = None

        page = await service.apply_retention_policy(
            page=mock_page,
            policy=mock_policy,
        )

        assert page.disposition_date is not None

    @pytest.mark.asyncio
    async def test_apply_policy_from_created_date(
        self, service, mock_db, mock_page, mock_policy
    ):
        """Should use created_at if retention_from is not effective_date."""
        mock_policy.retention_from = "created_date"

        page = await service.apply_retention_policy(
            page=mock_page,
            policy=mock_policy,
        )

        assert page.disposition_date is not None


class TestGetDocumentsDueForReview:
    """Tests for finding documents due for periodic review."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a retention service instance."""
        return RetentionService(mock_db)

    @pytest.mark.asyncio
    async def test_find_due_for_review(self, service, mock_db):
        """Should find documents with review date in range."""
        org_id = str(uuid4())

        page1 = MagicMock(spec=Page)
        page1.id = str(uuid4())
        page1.next_review_date = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [page1]
        mock_db.execute.return_value = mock_result

        docs = await service.get_documents_due_for_review(
            organization_id=org_id,
            days_ahead=30,
        )

        assert len(docs) == 1

    @pytest.mark.asyncio
    async def test_find_overdue_reviews(self, service, mock_db):
        """Should find overdue reviews when include_overdue is True."""
        org_id = str(uuid4())

        # Overdue document
        page1 = MagicMock(spec=Page)
        page1.id = str(uuid4())
        page1.next_review_date = datetime.now(timezone.utc) - timedelta(days=30)

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [page1]
        mock_db.execute.return_value = mock_result

        docs = await service.get_documents_due_for_review(
            organization_id=org_id,
            days_ahead=30,
            include_overdue=True,
        )

        assert len(docs) == 1


class TestGetDocumentsDueForDisposition:
    """Tests for finding documents due for disposition."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a retention service instance."""
        return RetentionService(mock_db)

    @pytest.mark.asyncio
    async def test_find_due_for_disposition(self, service, mock_db):
        """Should find documents with disposition date reached."""
        org_id = str(uuid4())

        page1 = MagicMock(spec=Page)
        page1.id = str(uuid4())
        page1.disposition_date = datetime.now(timezone.utc) - timedelta(days=1)

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [page1]
        mock_db.execute.return_value = mock_result

        docs = await service.get_documents_due_for_disposition(
            organization_id=org_id,
        )

        assert len(docs) == 1


class TestCompleteReview:
    """Tests for completing periodic reviews."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a retention service instance."""
        return RetentionService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock page with review schedule."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.review_cycle_months = 12
        page.next_review_date = datetime.now(timezone.utc)
        page.last_reviewed_date = None
        page.last_reviewed_by_id = None
        return page

    @pytest.mark.asyncio
    async def test_complete_review_updates_dates(
        self, service, mock_db, mock_page
    ):
        """Completing review should update dates."""
        reviewer_id = str(uuid4())

        page = await service.complete_review(
            page=mock_page,
            reviewed_by_id=reviewer_id,
        )

        assert page.last_reviewed_by_id == reviewer_id
        assert page.last_reviewed_date is not None
        # Next review should be scheduled
        assert page.next_review_date is not None

    @pytest.mark.asyncio
    async def test_complete_review_schedules_next(
        self, service, mock_db, mock_page
    ):
        """Should schedule next review based on cycle."""
        reviewer_id = str(uuid4())
        old_review_date = mock_page.next_review_date

        page = await service.complete_review(
            page=mock_page,
            reviewed_by_id=reviewer_id,
        )

        # Next review should be in the future
        assert page.next_review_date > old_review_date

    @pytest.mark.asyncio
    async def test_complete_review_custom_cycle(
        self, service, mock_db, mock_page
    ):
        """Should support custom next review cycle."""
        reviewer_id = str(uuid4())

        await service.complete_review(
            page=mock_page,
            reviewed_by_id=reviewer_id,
            next_review_months=6,  # Override default cycle
        )

        mock_db.flush.assert_called()


class TestExecuteDisposition:
    """Tests for executing document disposition."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a retention service instance."""
        return RetentionService(mock_db)

    @pytest.fixture
    def mock_page_with_policy(self):
        """Create a mock page with retention policy."""
        policy = MagicMock(spec=RetentionPolicy)
        policy.disposition_method = DispositionMethod.ARCHIVE.value

        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.status = PageStatus.EFFECTIVE.value
        page.retention_policy = policy
        page.change_reason = None
        return page

    @pytest.mark.asyncio
    async def test_execute_archive_disposition(
        self, service, mock_db, mock_page_with_policy
    ):
        """Archive disposition should mark as obsolete."""
        user_id = str(uuid4())

        page = await service.execute_disposition(
            page=mock_page_with_policy,
            executed_by_id=user_id,
            reason="Retention period expired",
        )

        assert page.status == PageStatus.OBSOLETE.value
        assert "Archived" in page.change_reason

    @pytest.mark.asyncio
    async def test_execute_destroy_disposition(
        self, service, mock_db, mock_page_with_policy
    ):
        """Destroy disposition should mark for destruction."""
        mock_page_with_policy.retention_policy.disposition_method = (
            DispositionMethod.DESTROY.value
        )
        user_id = str(uuid4())

        page = await service.execute_disposition(
            page=mock_page_with_policy,
            executed_by_id=user_id,
            reason="Retention period expired",
        )

        # Should be marked for destruction
        assert "Destroyed" in page.change_reason

    @pytest.mark.asyncio
    async def test_execute_disposition_no_policy(
        self, service, mock_db
    ):
        """Should raise error if no retention policy."""
        page = MagicMock(spec=Page)
        page.retention_policy = None

        with pytest.raises(ValueError, match="no retention policy"):
            await service.execute_disposition(
                page=page,
                executed_by_id=str(uuid4()),
                reason="Test",
            )


class TestCreateRetentionPolicy:
    """Tests for creating retention policies."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a retention service instance."""
        return RetentionService(mock_db)

    @pytest.mark.asyncio
    async def test_create_policy(self, service, mock_db):
        """Should create retention policy."""
        org_id = str(uuid4())

        policy = await service.create_retention_policy(
            organization_id=org_id,
            name="Standard Records",
            retention_years=7,
            disposition_method=DispositionMethod.ARCHIVE,
            description="Standard 7-year retention for records",
        )

        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_policy_with_expiration_action(self, service, mock_db):
        """Should create policy with custom expiration action."""
        org_id = str(uuid4())

        await service.create_retention_policy(
            organization_id=org_id,
            name="Critical Records",
            retention_years=10,
            disposition_method=DispositionMethod.REVIEW,
            retention_expiry_action=ExpirationAction.AUTO_STATE_CHANGE,
        )

        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_policy_with_document_types(self, service, mock_db):
        """Should create policy for specific document types."""
        org_id = str(uuid4())

        await service.create_retention_policy(
            organization_id=org_id,
            name="SOP Retention",
            retention_years=5,
            disposition_method=DispositionMethod.ARCHIVE,
            applicable_document_types=["sop", "procedure"],
        )

        mock_db.add.assert_called_once()


class TestGetRetentionPolicies:
    """Tests for listing retention policies."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a retention service instance."""
        return RetentionService(mock_db)

    @pytest.mark.asyncio
    async def test_list_policies(self, service, mock_db):
        """Should list all active policies."""
        org_id = str(uuid4())

        policy1 = MagicMock(spec=RetentionPolicy)
        policy1.id = str(uuid4())
        policy1.name = "Standard"
        policy1.is_active = True

        policy2 = MagicMock(spec=RetentionPolicy)
        policy2.id = str(uuid4())
        policy2.name = "Extended"
        policy2.is_active = True

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [policy1, policy2]
        mock_db.execute.return_value = mock_result

        policies = await service.get_retention_policies(org_id)

        assert len(policies) == 2

    @pytest.mark.asyncio
    async def test_list_policies_active_only(self, service, mock_db):
        """Should filter to active policies by default."""
        org_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        await service.get_retention_policies(org_id, active_only=True)

        # Verify query filters active
        mock_db.execute.assert_called_once()


class TestGetApplicablePolicy:
    """Tests for finding applicable policy for document type."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a retention service instance."""
        return RetentionService(mock_db)

    @pytest.mark.asyncio
    async def test_find_type_specific_policy(self, service, mock_db):
        """Should find policy specific to document type."""
        org_id = str(uuid4())

        sop_policy = MagicMock(spec=RetentionPolicy)
        sop_policy.applicable_document_types = ["sop", "procedure"]

        service.get_retention_policies = AsyncMock(return_value=[sop_policy])

        policy = await service.get_applicable_policy(
            organization_id=org_id,
            document_type="sop",
        )

        assert policy == sop_policy

    @pytest.mark.asyncio
    async def test_fallback_to_catchall_policy(self, service, mock_db):
        """Should use catch-all policy if no type-specific match."""
        org_id = str(uuid4())

        catchall_policy = MagicMock(spec=RetentionPolicy)
        catchall_policy.applicable_document_types = []  # Catch-all

        service.get_retention_policies = AsyncMock(return_value=[catchall_policy])

        policy = await service.get_applicable_policy(
            organization_id=org_id,
            document_type="guidance",
        )

        assert policy == catchall_policy

    @pytest.mark.asyncio
    async def test_no_policy_returns_none(self, service, mock_db):
        """Should return None if no policy found."""
        org_id = str(uuid4())

        service.get_retention_policies = AsyncMock(return_value=[])

        policy = await service.get_applicable_policy(
            organization_id=org_id,
            document_type="sop",
        )

        assert policy is None


class TestRetentionPolicyModel:
    """Tests for RetentionPolicy model behavior."""

    def test_disposition_method_values(self):
        """Should have expected disposition methods."""
        assert DispositionMethod.ARCHIVE.value == "archive"
        assert DispositionMethod.DESTROY.value == "destroy"
        assert DispositionMethod.TRANSFER.value == "transfer"
        assert DispositionMethod.REVIEW.value == "review"

    def test_expiration_action_values(self):
        """Should have expected expiration actions."""
        assert ExpirationAction.NOTIFY_ONLY.value == "notify_only"
        assert ExpirationAction.AUTO_STATE_CHANGE.value == "auto_state_change"
        assert ExpirationAction.BLOCK_ACCESS.value == "block_access"


class TestOverdueReviewCount:
    """Tests for counting overdue reviews."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a retention service instance."""
        return RetentionService(mock_db)

    @pytest.mark.asyncio
    async def test_get_overdue_count(self, service, mock_db):
        """Should count documents with overdue reviews."""
        org_id = str(uuid4())

        # Mock 3 overdue documents
        pages = [MagicMock(), MagicMock(), MagicMock()]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = pages
        mock_db.execute.return_value = mock_result

        count = await service.get_overdue_review_count(org_id)

        assert count == 3
