"""Unit tests for Revision Service (Sprint 6).

Tests revision letter progression and version management.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.modules.document_control.revision_service import RevisionService
from src.db.models.page import Page, PageStatus
from src.db.models.change_request import ChangeRequest, ChangeRequestStatus


class TestRevisionLetterProgression:
    """Tests for revision letter progression logic."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a revision service instance."""
        return RevisionService(mock_db)

    def test_first_revision_is_a(self, service):
        """First revision should be 'A'."""
        result = service._next_revision_letter("")
        assert result == "A"

    def test_revision_a_to_b(self, service):
        """Revision A should progress to B."""
        result = service._next_revision_letter("A")
        assert result == "B"

    def test_revision_progression_through_alphabet(self, service):
        """Test progression through the alphabet."""
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i in range(len(letters) - 1):
            result = service._next_revision_letter(letters[i])
            assert result == letters[i + 1]

    def test_revision_z_to_aa(self, service):
        """Revision Z should progress to AA."""
        result = service._next_revision_letter("Z")
        assert result == "AA"

    def test_revision_aa_to_ab(self, service):
        """Revision AA should progress to AB."""
        result = service._next_revision_letter("AA")
        assert result == "AB"

    def test_revision_az_to_ba(self, service):
        """Revision AZ should progress to BA."""
        result = service._next_revision_letter("AZ")
        assert result == "BA"

    def test_revision_zz_to_aaa(self, service):
        """Revision ZZ should progress to AAA."""
        result = service._next_revision_letter("ZZ")
        assert result == "AAA"


class TestCalculateNextRevision:
    """Tests for revision calculation."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a revision service instance."""
        return RevisionService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock page."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.slug = "test-page"
        page.revision = "A"
        page.major_version = 1
        page.minor_version = 0
        page.status = PageStatus.EFFECTIVE.value
        return page

    def test_major_revision_increments_letter(self, service, mock_page):
        """Major revision should increment revision letter."""
        new_rev, new_major, new_minor = service.calculate_next_revision(
            mock_page, is_major=True
        )

        assert new_rev == "B"
        assert new_major == 1
        assert new_minor == 0

    def test_major_revision_resets_version(self, service, mock_page):
        """Major revision should reset version to 1.0."""
        mock_page.major_version = 3
        mock_page.minor_version = 5

        new_rev, new_major, new_minor = service.calculate_next_revision(
            mock_page, is_major=True
        )

        assert new_rev == "B"
        assert new_major == 1
        assert new_minor == 0

    def test_minor_revision_keeps_letter(self, service, mock_page):
        """Minor revision should keep revision letter."""
        new_rev, new_major, new_minor = service.calculate_next_revision(
            mock_page, is_major=False
        )

        assert new_rev == "A"
        assert new_major == 1
        assert new_minor == 1

    def test_minor_revision_increments_minor(self, service, mock_page):
        """Minor revision should increment minor version."""
        mock_page.minor_version = 5

        new_rev, new_major, new_minor = service.calculate_next_revision(
            mock_page, is_major=False
        )

        assert new_rev == "A"
        assert new_major == 1
        assert new_minor == 6


class TestCreateRevision:
    """Tests for creating revisions."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = AsyncMock()
        # Mock the execute for getting last CR
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute.return_value = mock_result
        return db

    @pytest.fixture
    def service(self, mock_db):
        """Create a revision service instance."""
        return RevisionService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock effective page."""
        page = MagicMock(spec=Page)
        page.id = str(uuid4())
        page.slug = "test-document"
        page.revision = "A"
        page.major_version = 1
        page.minor_version = 0
        page.status = PageStatus.EFFECTIVE.value
        page.git_commit_sha = "abc123"
        return page

    @pytest.mark.asyncio
    async def test_create_revision_requires_effective_status(
        self, service, mock_page
    ):
        """Can only create revisions of effective documents."""
        mock_page.status = PageStatus.DRAFT.value

        with pytest.raises(ValueError, match="Can only create revisions of effective"):
            await service.create_revision(
                page=mock_page,
                is_major=True,
                change_reason="Major update",
                author_id=str(uuid4()),
            )

    @pytest.mark.asyncio
    async def test_major_revision_requires_reason(self, service, mock_page):
        """Major revisions require a change reason."""
        with pytest.raises(ValueError, match="Change reason is required"):
            await service.create_revision(
                page=mock_page,
                is_major=True,
                change_reason="",
                author_id=str(uuid4()),
            )

    @pytest.mark.asyncio
    async def test_create_revision_creates_change_request(
        self, service, mock_db, mock_page
    ):
        """Creating a revision should create a change request."""
        author_id = str(uuid4())

        cr = await service.create_revision(
            page=mock_page,
            is_major=True,
            change_reason="Major update",
            author_id=author_id,
        )

        # Should have added a change request
        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_revision_stores_pending_metadata(
        self, service, mock_db, mock_page
    ):
        """Created CR should store pending revision metadata."""
        author_id = str(uuid4())

        # We need to capture what was added - use a list to track
        added_objects = []

        def capture_add(obj):
            added_objects.append(obj)

        mock_db.add = MagicMock(side_effect=capture_add)

        cr = await service.create_revision(
            page=mock_page,
            is_major=True,
            change_reason="Major update",
            author_id=author_id,
        )

        # The CR is returned directly
        assert cr is not None
        assert cr.revision_metadata["pending_revision"] == "B"
        assert cr.revision_metadata["pending_major_version"] == 1
        assert cr.revision_metadata["pending_minor_version"] == 0


class TestApplyRevision:
    """Tests for applying revision metadata on publish."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a revision service instance."""
        return RevisionService(mock_db)

    @pytest.fixture
    def mock_page(self):
        """Create a mock page."""
        page = MagicMock(spec=Page)
        page.revision = "A"
        page.major_version = 1
        page.minor_version = 0
        page.version = "1.0"
        page.change_summary = None
        page.change_reason = None
        return page

    @pytest.fixture
    def mock_change_request(self, mock_page):
        """Create a mock change request with revision metadata."""
        cr = MagicMock(spec=ChangeRequest)
        cr.page = mock_page
        cr.title = "Major Update"
        cr.change_reason = "Regulatory requirement change"
        cr.revision_metadata = {
            "pending_revision": "B",
            "pending_major_version": 1,
            "pending_minor_version": 0,
        }
        return cr

    @pytest.mark.asyncio
    async def test_apply_revision_updates_page(
        self, service, mock_db, mock_change_request
    ):
        """Apply revision should update page fields."""
        page = await service.apply_revision(mock_change_request)

        assert page.revision == "B"
        assert page.major_version == 1
        assert page.minor_version == 0
        assert page.version == "1.0"
        assert page.change_summary == "Major Update"
        assert page.change_reason == "Regulatory requirement change"

    @pytest.mark.asyncio
    async def test_apply_revision_no_metadata(self, service, mock_db, mock_page):
        """Apply revision with no metadata should not change page."""
        cr = MagicMock(spec=ChangeRequest)
        cr.page = mock_page
        cr.revision_metadata = None

        original_revision = mock_page.revision

        await service.apply_revision(cr)

        assert mock_page.revision == original_revision


class TestRevisionHistory:
    """Tests for revision history retrieval."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a revision service instance."""
        return RevisionService(mock_db)

    @pytest.mark.asyncio
    async def test_get_revision_history_returns_published_crs(self, service, mock_db):
        """Should return only published change requests."""
        page_id = str(uuid4())

        # Mock published CRs
        cr1 = MagicMock()
        cr1.id = str(uuid4())
        cr1.number = 1
        cr1.title = "Initial release"
        cr1.description = "First version"
        cr1.change_reason = "Initial"
        cr1.is_major_revision = True
        cr1.author_id = str(uuid4())
        cr1.published_at = datetime.now(timezone.utc)
        cr1.published_by_id = str(uuid4())
        cr1.revision_metadata = {
            "pending_revision": "A",
            "pending_major_version": 1,
            "pending_minor_version": 0,
        }

        mock_result = MagicMock()
        mock_result.scalars.return_value = [cr1]
        mock_db.execute.return_value = mock_result

        history = await service.get_revision_history(page_id)

        assert len(history) == 1
        assert history[0]["revision"] == "A"
        assert history[0]["version"] == "1.0"
        assert history[0]["is_major"] is True


class TestVersionInfo:
    """Tests for version info retrieval."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a revision service instance."""
        return RevisionService(mock_db)

    @pytest.mark.asyncio
    async def test_get_current_version_info(self, service):
        """Should return all version fields."""
        page = MagicMock(spec=Page)
        page.revision = "B"
        page.major_version = 2
        page.minor_version = 3
        page.full_version = "B v2.3"
        page.version = "2.3"
        page.change_summary = "Bug fixes"
        page.change_reason = "Quality improvement"

        info = await service.get_current_version_info(page)

        assert info["revision"] == "B"
        assert info["major_version"] == 2
        assert info["minor_version"] == 3
        assert info["full_version"] == "B v2.3"
        assert info["version"] == "2.3"
        assert info["change_summary"] == "Bug fixes"
        assert info["change_reason"] == "Quality improvement"
