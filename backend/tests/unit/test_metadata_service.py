"""Unit tests for Document Metadata Service (Sprint 6).

Tests document metadata validation and management.

Compliance: ISO 13485 §4.2.4 - Document control requirements
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.modules.document_control.metadata_service import DocumentMetadataService
from src.db.models.page import Page, PageStatus
from src.db.models.document_lifecycle import DocumentStatus


class TestValidateForTransition:
    """Tests for transition validation."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a metadata service instance."""
        return DocumentMetadataService(mock_db)

    @pytest.fixture
    def mock_controlled_page(self):
        """Create a mock controlled page."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.is_controlled = True
        page.document_number = "SOP-001"
        page.document_type = "sop"
        page.owner_id = str(uuid4())
        page.effective_date = None
        page.approved_date = None
        page.review_cycle_months = None
        page.next_review_date = None
        page.retention_policy_id = None
        return page

    def test_validate_draft_to_review_requires_doc_number(
        self, service, mock_controlled_page
    ):
        """Submitting for review requires document number."""
        mock_controlled_page.document_number = None

        errors = service.validate_for_transition(
            page=mock_controlled_page,
            from_status=DocumentStatus.DRAFT,
            to_status=DocumentStatus.IN_REVIEW,
        )

        assert any("Document number" in e for e in errors)

    def test_validate_draft_to_review_requires_owner(
        self, service, mock_controlled_page
    ):
        """Submitting for review requires document owner."""
        mock_controlled_page.owner_id = None

        errors = service.validate_for_transition(
            page=mock_controlled_page,
            from_status=DocumentStatus.DRAFT,
            to_status=DocumentStatus.IN_REVIEW,
        )

        assert any("owner" in e.lower() for e in errors)

    def test_validate_review_to_approved_requires_doc_type(
        self, service, mock_controlled_page
    ):
        """Approval requires document type."""
        mock_controlled_page.document_type = None

        errors = service.validate_for_transition(
            page=mock_controlled_page,
            from_status=DocumentStatus.IN_REVIEW,
            to_status=DocumentStatus.APPROVED,
        )

        assert any("Document type" in e for e in errors)

    def test_validate_approved_to_effective_allows_no_effective_date(
        self, service, mock_controlled_page
    ):
        """Effective date is set by endpoint, not validated beforehand."""
        mock_controlled_page.effective_date = None
        mock_controlled_page.approved_date = datetime.now(timezone.utc)

        errors = service.validate_for_transition(
            page=mock_controlled_page,
            from_status=DocumentStatus.APPROVED,
            to_status=DocumentStatus.EFFECTIVE,
        )

        # effective_date is set during transition, so no validation error
        assert not any("Effective date must be set" in e for e in errors)

    def test_validate_effective_date_not_before_approved_date(
        self, service, mock_controlled_page
    ):
        """Effective date cannot be before approved date."""
        now = datetime.now(timezone.utc)
        mock_controlled_page.approved_date = now
        mock_controlled_page.effective_date = now - timedelta(days=1)

        errors = service.validate_for_transition(
            page=mock_controlled_page,
            from_status=DocumentStatus.APPROVED,
            to_status=DocumentStatus.EFFECTIVE,
        )

        assert any("before approved date" in e for e in errors)

    def test_validate_review_date_calculated_during_transition(
        self, service, mock_controlled_page
    ):
        """Next review date is calculated by endpoint, not validated beforehand."""
        mock_controlled_page.effective_date = datetime.now(timezone.utc)
        mock_controlled_page.approved_date = datetime.now(timezone.utc)
        mock_controlled_page.review_cycle_months = 12
        mock_controlled_page.next_review_date = None

        errors = service.validate_for_transition(
            page=mock_controlled_page,
            from_status=DocumentStatus.APPROVED,
            to_status=DocumentStatus.EFFECTIVE,
        )

        # next_review_date is calculated during transition, so no validation error
        assert not any("Next review date" in e for e in errors)

    def test_validate_retention_required_for_records(
        self, service, mock_controlled_page
    ):
        """Retention policy required for record type documents."""
        mock_controlled_page.document_type = "record"
        mock_controlled_page.effective_date = datetime.now(timezone.utc)
        mock_controlled_page.approved_date = datetime.now(timezone.utc)
        mock_controlled_page.retention_policy_id = None

        errors = service.validate_for_transition(
            page=mock_controlled_page,
            from_status=DocumentStatus.APPROVED,
            to_status=DocumentStatus.EFFECTIVE,
        )

        assert any("Retention policy" in e for e in errors)

    def test_non_controlled_skips_validation(self, service):
        """Non-controlled documents skip validation."""
        page = MagicMock(spec=Page)
        page.is_controlled = False

        errors = service.validate_for_transition(
            page=page,
            from_status=DocumentStatus.DRAFT,
            to_status=DocumentStatus.EFFECTIVE,
        )

        assert len(errors) == 0


class TestValidateMajorRevision:
    """Tests for major revision validation."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a metadata service instance."""
        return DocumentMetadataService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock page."""
        return MagicMock(spec=Page)

    def test_major_revision_requires_change_reason(self, service, mock_page):
        """Major revision requires change reason."""
        errors = service.validate_major_revision(
            page=mock_page,
            change_reason=None,
        )

        assert any("Change reason is required" in e for e in errors)

    def test_major_revision_requires_min_length(self, service, mock_page):
        """Change reason must be at least 10 characters."""
        errors = service.validate_major_revision(
            page=mock_page,
            change_reason="Short",
        )

        assert any("at least 10 characters" in e for e in errors)

    def test_valid_major_revision(self, service, mock_page):
        """Valid change reason passes validation."""
        errors = service.validate_major_revision(
            page=mock_page,
            change_reason="Updated per regulatory requirement FDA-2024-001",
        )

        assert len(errors) == 0


class TestSetEffective:
    """Tests for making documents effective."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a metadata service instance."""
        return DocumentMetadataService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock page."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.status = PageStatus.APPROVED.value
        page.effective_date = None
        page.next_review_date = None
        page.review_cycle_months = None
        return page

    @pytest.mark.asyncio
    async def test_set_effective_updates_status(self, service, mock_db, mock_page):
        """Setting effective should update page status."""
        effective_date = datetime.now(timezone.utc)
        user_id = str(uuid4())

        page = await service.set_effective(
            page=mock_page,
            effective_date=effective_date,
            set_by_id=user_id,
        )

        assert page.effective_date == effective_date
        assert page.status == PageStatus.EFFECTIVE.value

    @pytest.mark.asyncio
    async def test_set_effective_calculates_review_date(
        self, service, mock_db, mock_page
    ):
        """Should calculate next review date if cycle is set."""
        mock_page.review_cycle_months = 12
        effective_date = datetime.now(timezone.utc)
        user_id = str(uuid4())

        page = await service.set_effective(
            page=mock_page,
            effective_date=effective_date,
            set_by_id=user_id,
        )

        assert page.next_review_date is not None
        # Should be approximately 12 months later
        expected = effective_date + timedelta(days=360)
        assert abs((page.next_review_date - expected).days) < 10


class TestSetApproved:
    """Tests for approving documents."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a metadata service instance."""
        return DocumentMetadataService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock page."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.status = PageStatus.DRAFT.value
        page.approved_date = None
        page.approved_by_id = None
        return page

    @pytest.mark.asyncio
    async def test_set_approved_updates_fields(self, service, mock_db, mock_page):
        """Setting approved should update relevant fields."""
        user_id = str(uuid4())

        page = await service.set_approved(
            page=mock_page,
            approved_by_id=user_id,
        )

        assert page.approved_by_id == user_id
        assert page.approved_date is not None
        assert page.status == PageStatus.APPROVED.value

    @pytest.mark.asyncio
    async def test_set_approved_custom_date(self, service, mock_db, mock_page):
        """Can specify custom approved date."""
        user_id = str(uuid4())
        custom_date = datetime(2024, 1, 15, tzinfo=timezone.utc)

        page = await service.set_approved(
            page=mock_page,
            approved_by_id=user_id,
            approved_date=custom_date,
        )

        assert page.approved_date == custom_date


class TestMarkObsolete:
    """Tests for marking documents obsolete."""

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
        """Create a metadata service instance."""
        return DocumentMetadataService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock page."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.status = PageStatus.EFFECTIVE.value
        page.change_reason = None
        page.superseded_by_id = None
        return page

    @pytest.mark.asyncio
    async def test_mark_obsolete_updates_status(self, service, mock_db, mock_page):
        """Marking obsolete should update status."""
        user_id = str(uuid4())

        page = await service.mark_obsolete(
            page=mock_page,
            superseded_by_id=None,
            reason="No longer applicable",
            marked_by_id=user_id,
        )

        assert page.status == PageStatus.OBSOLETE.value
        assert page.change_reason == "No longer applicable"

    @pytest.mark.asyncio
    async def test_mark_obsolete_with_superseding_doc(
        self, service, mock_db, mock_page
    ):
        """Should link to superseding document."""
        user_id = str(uuid4())
        new_doc_id = str(uuid4())

        # Set up new document
        new_doc = MagicMock(spec=Page)
        new_doc.id = new_doc_id
        new_doc.supersedes_id = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = new_doc
        mock_db.execute.return_value = mock_result

        page = await service.mark_obsolete(
            page=mock_page,
            superseded_by_id=new_doc_id,
            reason="Replaced by new version",
            marked_by_id=user_id,
        )

        assert page.superseded_by_id == new_doc_id
        assert new_doc.supersedes_id == mock_page.id


class TestAssignOwner:
    """Tests for assigning document ownership."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a metadata service instance."""
        return DocumentMetadataService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock page."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.owner_id = None
        page.custodian_id = None
        return page

    @pytest.mark.asyncio
    async def test_assign_owner(self, service, mock_db, mock_page):
        """Should assign owner to document."""
        owner_id = str(uuid4())

        page = await service.assign_owner(
            page=mock_page,
            owner_id=owner_id,
        )

        assert page.owner_id == owner_id

    @pytest.mark.asyncio
    async def test_assign_owner_and_custodian(self, service, mock_db, mock_page):
        """Should assign both owner and custodian."""
        owner_id = str(uuid4())
        custodian_id = str(uuid4())

        page = await service.assign_owner(
            page=mock_page,
            owner_id=owner_id,
            custodian_id=custodian_id,
        )

        assert page.owner_id == owner_id
        assert page.custodian_id == custodian_id


class TestSetReviewSchedule:
    """Tests for setting review schedule."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a metadata service instance."""
        return DocumentMetadataService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock page."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.review_cycle_months = None
        page.next_review_date = None
        page.effective_date = datetime.now(timezone.utc)
        return page

    @pytest.mark.asyncio
    async def test_set_review_cycle(self, service, mock_db, mock_page):
        """Should set review cycle and calculate next review."""
        page = await service.set_review_schedule(
            page=mock_page,
            review_cycle_months=12,
        )

        assert page.review_cycle_months == 12
        assert page.next_review_date is not None

    @pytest.mark.asyncio
    async def test_set_specific_review_date(self, service, mock_db, mock_page):
        """Should allow specific next review date."""
        specific_date = datetime(2025, 6, 15, tzinfo=timezone.utc)

        page = await service.set_review_schedule(
            page=mock_page,
            review_cycle_months=12,
            next_review_date=specific_date,
        )

        assert page.next_review_date == specific_date


class TestSetTrainingRequirement:
    """Tests for setting training requirements."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a metadata service instance."""
        return DocumentMetadataService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock page."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.requires_training = False
        page.training_validity_months = None
        return page

    @pytest.mark.asyncio
    async def test_enable_training_requirement(self, service, mock_db, mock_page):
        """Should enable training requirement."""
        page = await service.set_training_requirement(
            page=mock_page,
            requires_training=True,
            validity_months=24,
        )

        assert page.requires_training is True
        assert page.training_validity_months == 24

    @pytest.mark.asyncio
    async def test_disable_training_clears_validity(self, service, mock_db, mock_page):
        """Disabling training should clear validity."""
        mock_page.requires_training = True
        mock_page.training_validity_months = 24

        page = await service.set_training_requirement(
            page=mock_page,
            requires_training=False,
        )

        assert page.requires_training is False
        assert page.training_validity_months is None


class TestGetMetadataSummary:
    """Tests for metadata summary retrieval."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a metadata service instance."""
        return DocumentMetadataService(mock_db)

    def test_get_complete_summary(self, service):
        """Should return all metadata fields."""
        page = MagicMock(spec=Page)
        page.document_number = "SOP-001"
        page.document_type = "sop"
        page.is_controlled = True
        page.revision = "B"
        page.major_version = 2
        page.minor_version = 1
        page.full_version = "B v2.1"
        page.status = PageStatus.EFFECTIVE.value
        page.classification = "internal"
        page.owner_id = str(uuid4())
        page.custodian_id = str(uuid4())
        page.approved_date = datetime.now(timezone.utc)
        page.effective_date = datetime.now(timezone.utc)
        page.next_review_date = datetime.now(timezone.utc) + timedelta(days=365)
        page.last_reviewed_date = None
        page.review_cycle_months = 12
        page.disposition_date = None
        page.requires_training = True
        page.training_validity_months = 24
        page.change_summary = "Updated procedure"
        page.change_reason = "Regulatory change"
        page.supersedes_id = None
        page.superseded_by_id = None

        summary = service.get_metadata_summary(page)

        assert summary["document_number"] == "SOP-001"
        assert summary["revision"] == "B"
        assert summary["is_controlled"] is True
        assert summary["requires_training"] is True


class TestGetMissingRequiredFields:
    """Tests for missing required fields check."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a metadata service instance."""
        return DocumentMetadataService(mock_db)

    def test_controlled_doc_missing_fields(self, service):
        """Should identify missing required fields for controlled docs."""
        page = MagicMock(spec=Page)
        page.is_controlled = True
        page.document_number = None
        page.document_type = None
        page.owner_id = None
        page.status = PageStatus.DRAFT.value

        missing = service.get_missing_required_fields(page)

        assert "document_number" in missing
        assert "document_type" in missing
        assert "owner_id" in missing

    def test_non_controlled_no_missing(self, service):
        """Non-controlled docs have no required fields."""
        page = MagicMock(spec=Page)
        page.is_controlled = False

        missing = service.get_missing_required_fields(page)

        assert len(missing) == 0

    def test_effective_requires_more_fields(self, service):
        """Effective status requires additional fields."""
        page = MagicMock(spec=Page)
        page.is_controlled = True
        page.document_number = "SOP-001"
        page.document_type = "sop"
        page.owner_id = str(uuid4())
        page.status = PageStatus.EFFECTIVE.value
        page.effective_date = None
        page.review_cycle_months = 12
        page.next_review_date = None

        missing = service.get_missing_required_fields(
            page, target_status=DocumentStatus.EFFECTIVE
        )

        assert "effective_date" in missing
        assert "next_review_date" in missing
