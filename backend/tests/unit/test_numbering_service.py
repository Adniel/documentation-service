"""Unit tests for Document Numbering Service (Sprint 6).

Tests document number generation and validation.

Compliance: ISO 13485 §4.2.4 - Document identification
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.modules.document_control.numbering_service import DocumentNumberingService
from src.db.models.document_number import DocumentNumberSequence
from src.db.models.document_lifecycle import DocumentType


class TestGenerateDocumentNumber:
    """Tests for document number generation."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = AsyncMock()
        # Default: no existing sequence
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute.return_value = mock_result
        return db

    @pytest.fixture
    def service(self, mock_db):
        """Create a numbering service instance."""
        return DocumentNumberingService(mock_db)

    @pytest.mark.asyncio
    async def test_generate_first_number_in_sequence(self, service, mock_db):
        """First number in sequence should be 001."""
        org_id = str(uuid4())

        # Capture what was added and set up the sequence properly
        added_seq = None

        def capture_add(obj):
            nonlocal added_seq
            added_seq = obj
            # Set format_pattern so generate_next works
            obj.format_pattern = "{prefix}-{number:03d}"
            obj.generate_next = lambda: f"{obj.prefix}-001"

        mock_db.add = MagicMock(side_effect=capture_add)

        number = await service.generate_document_number(
            organization_id=org_id,
            document_type=DocumentType.SOP,
        )

        assert "SOP" in number
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_increments_existing_sequence(self, service, mock_db):
        """Should increment existing sequence."""
        org_id = str(uuid4())

        # Set up existing sequence
        existing_seq = MagicMock(spec=DocumentNumberSequence)
        existing_seq.prefix = "SOP"
        existing_seq.current_number = 5
        existing_seq.generate_next = MagicMock(return_value="SOP-006")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_seq
        mock_db.execute.return_value = mock_result

        number = await service.generate_document_number(
            organization_id=org_id,
            document_type=DocumentType.SOP,
        )

        assert number == "SOP-006"
        existing_seq.generate_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_custom_prefix(self, service, mock_db):
        """Should allow custom prefix override."""
        org_id = str(uuid4())

        # Capture what was added
        added_seq = None

        def capture_add(obj):
            nonlocal added_seq
            added_seq = obj
            obj.format_pattern = "{prefix}-{number:03d}"
            obj.generate_next = lambda: f"{obj.prefix}-001"

        mock_db.add = MagicMock(side_effect=capture_add)

        number = await service.generate_document_number(
            organization_id=org_id,
            document_type=DocumentType.SOP,
            custom_prefix="QA-SOP",
        )

        assert "QA-SOP" in number

    @pytest.mark.asyncio
    async def test_generate_with_string_type(self, service, mock_db):
        """Should accept document type as string."""
        org_id = str(uuid4())

        # Capture what was added
        added_seq = None

        def capture_add(obj):
            nonlocal added_seq
            added_seq = obj
            obj.format_pattern = "{prefix}-{number:03d}"
            obj.generate_next = lambda: f"{obj.prefix}-001"

        mock_db.add = MagicMock(side_effect=capture_add)

        number = await service.generate_document_number(
            organization_id=org_id,
            document_type="sop",
        )

        assert number is not None


class TestValidateDocumentNumber:
    """Tests for document number validation."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a numbering service instance."""
        return DocumentNumberingService(mock_db)

    @pytest.mark.asyncio
    async def test_validate_unique_number(self, service, mock_db):
        """Should return True for unique number."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        is_valid = await service.validate_document_number("SOP-001")

        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_duplicate_number(self, service, mock_db):
        """Should return False for duplicate number."""
        # Existing page with this number
        existing_page = MagicMock()
        existing_page.id = str(uuid4())
        existing_page.document_number = "SOP-001"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_page
        mock_db.execute.return_value = mock_result

        is_valid = await service.validate_document_number("SOP-001")

        assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_excludes_self(self, service, mock_db):
        """Should exclude specified page when validating."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        page_id = str(uuid4())
        is_valid = await service.validate_document_number(
            "SOP-001", exclude_page_id=page_id
        )

        assert is_valid is True


class TestConfigureSequence:
    """Tests for sequence configuration."""

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
        """Create a numbering service instance."""
        return DocumentNumberingService(mock_db)

    @pytest.mark.asyncio
    async def test_create_new_sequence(self, service, mock_db):
        """Should create new sequence if none exists."""
        org_id = str(uuid4())

        seq = await service.configure_sequence(
            organization_id=org_id,
            document_type=DocumentType.SOP,
            prefix="SOP",
            format_pattern="{prefix}-{number:04d}",
        )

        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_existing_sequence(self, service, mock_db):
        """Should update existing sequence."""
        org_id = str(uuid4())

        # Set up existing sequence
        existing_seq = MagicMock(spec=DocumentNumberSequence)
        existing_seq.prefix = "SOP"
        existing_seq.format_pattern = "{prefix}-{number:03d}"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_seq
        mock_db.execute.return_value = mock_result

        await service.configure_sequence(
            organization_id=org_id,
            document_type=DocumentType.SOP,
            prefix="QA-SOP",
            format_pattern="{prefix}-{number:04d}",
        )

        assert existing_seq.prefix == "QA-SOP"
        assert existing_seq.format_pattern == "{prefix}-{number:04d}"


class TestGetSequence:
    """Tests for getting sequences."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a numbering service instance."""
        return DocumentNumberingService(mock_db)

    @pytest.mark.asyncio
    async def test_get_existing_sequence(self, service, mock_db):
        """Should return existing sequence."""
        org_id = str(uuid4())

        existing_seq = MagicMock(spec=DocumentNumberSequence)
        existing_seq.prefix = "SOP"
        existing_seq.current_number = 10

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_seq
        mock_db.execute.return_value = mock_result

        seq = await service.get_sequence(org_id, DocumentType.SOP)

        assert seq == existing_seq

    @pytest.mark.asyncio
    async def test_get_nonexistent_sequence(self, service, mock_db):
        """Should return None if sequence doesn't exist."""
        org_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        seq = await service.get_sequence(org_id, DocumentType.SOP)

        assert seq is None


class TestPreviewNextNumber:
    """Tests for previewing next number without incrementing."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a numbering service instance."""
        return DocumentNumberingService(mock_db)

    @pytest.mark.asyncio
    async def test_preview_shows_next_number(self, service, mock_db):
        """Preview should show what the next number would be."""
        org_id = str(uuid4())

        # Set up existing sequence
        existing_seq = MagicMock(spec=DocumentNumberSequence)
        existing_seq.current_number = 10
        existing_seq.preview_next = MagicMock(return_value="SOP-011")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_seq
        mock_db.execute.return_value = mock_result

        # Mock get_sequence to return the existing sequence
        service.get_sequence = AsyncMock(return_value=existing_seq)

        preview = await service.preview_next_number(
            organization_id=org_id,
            document_type=DocumentType.SOP,
        )

        assert preview == "SOP-011"
        existing_seq.preview_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_preview_returns_none_if_no_sequence(self, service, mock_db):
        """Preview should return None if no sequence exists."""
        org_id = str(uuid4())

        service.get_sequence = AsyncMock(return_value=None)

        preview = await service.preview_next_number(
            organization_id=org_id,
            document_type=DocumentType.SOP,
        )

        assert preview is None


class TestListSequences:
    """Tests for listing document number sequences."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Create a numbering service instance."""
        return DocumentNumberingService(mock_db)

    @pytest.mark.asyncio
    async def test_list_all_sequences(self, service, mock_db):
        """Should list all sequences for an organization."""
        org_id = str(uuid4())

        # Set up sequences
        seq1 = MagicMock(spec=DocumentNumberSequence)
        seq1.document_type = DocumentType.SOP.value
        seq1.current_number = 5

        seq2 = MagicMock(spec=DocumentNumberSequence)
        seq2.document_type = DocumentType.WI.value
        seq2.current_number = 12

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [seq1, seq2]
        mock_db.execute.return_value = mock_result

        sequences = await service.list_sequences(org_id)

        assert len(sequences) == 2

    @pytest.mark.asyncio
    async def test_list_empty_sequences(self, service, mock_db):
        """Should return empty list if no sequences exist."""
        org_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        sequences = await service.list_sequences(org_id)

        assert sequences == []


class TestDocumentTypeIntegration:
    """Tests for document type handling."""

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
        """Create a numbering service instance."""
        return DocumentNumberingService(mock_db)

    @pytest.mark.asyncio
    async def test_sop_type(self, service, mock_db):
        """Should handle SOP document type."""
        org_id = str(uuid4())

        added_seq = None

        def capture_add(obj):
            nonlocal added_seq
            added_seq = obj
            obj.format_pattern = "{prefix}-{number:03d}"
            obj.generate_next = lambda: f"{obj.prefix}-001"

        mock_db.add = MagicMock(side_effect=capture_add)

        await service.generate_document_number(org_id, DocumentType.SOP)

        assert added_seq is not None
        assert added_seq.document_type == "sop"

    @pytest.mark.asyncio
    async def test_wi_type(self, service, mock_db):
        """Should handle WI document type."""
        org_id = str(uuid4())

        added_seq = None

        def capture_add(obj):
            nonlocal added_seq
            added_seq = obj
            obj.format_pattern = "{prefix}-{number:03d}"
            obj.generate_next = lambda: f"{obj.prefix}-001"

        mock_db.add = MagicMock(side_effect=capture_add)

        await service.generate_document_number(org_id, DocumentType.WI)

        assert added_seq is not None
        assert added_seq.document_type == "wi"
