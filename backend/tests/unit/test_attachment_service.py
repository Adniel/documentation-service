"""Unit tests for attachment service.

Sprint F: Attachments & Media Support
"""

import hashlib
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.db.models.attachment import Attachment, AttachmentStatus
from src.modules.attachments.service import (
    AttachmentService,
    sanitize_filename,
    compute_file_hash,
    ALLOWED_MIME_TYPES,
    MAX_FILE_SIZE,
)


class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_simple_filename(self):
        """Simple filenames pass through."""
        assert sanitize_filename("document.pdf") == "document.pdf"

    def test_removes_path_separators(self):
        """Path separators are removed."""
        assert sanitize_filename("/etc/passwd") == "passwd"
        assert sanitize_filename("C:\\Windows\\system32\\cmd.exe") == "cmd.exe"

    def test_replaces_special_characters(self):
        """Special characters are replaced with underscores."""
        result = sanitize_filename("my file (v2).pdf")
        assert " " not in result
        assert "(" not in result
        assert ")" not in result
        assert result.endswith(".pdf")

    def test_collapses_multiple_underscores(self):
        """Multiple underscores are collapsed."""
        result = sanitize_filename("file___name.pdf")
        assert "___" not in result

    def test_long_filename_truncated(self):
        """Long filenames are truncated while preserving extension."""
        long_name = "a" * 300 + ".pdf"
        result = sanitize_filename(long_name)
        assert len(result) <= 200
        assert result.endswith(".pdf")

    def test_empty_extension(self):
        """Files without extension are handled."""
        result = sanitize_filename("a" * 300)
        assert len(result) <= 200

    def test_preserves_dots_hyphens_underscores(self):
        """Dots, hyphens, and underscores are preserved."""
        assert sanitize_filename("my-file_v2.0.tar.gz") == "my-file_v2.0.tar.gz"


class TestComputeFileHash:
    """Test file hash computation."""

    def test_hash_computation(self):
        """Hash is computed correctly."""
        data = BytesIO(b"test content")
        result = compute_file_hash(data)
        expected = hashlib.sha256(b"test content").hexdigest()
        assert result == expected

    def test_stream_position_reset(self):
        """Stream position is reset after hashing."""
        data = BytesIO(b"test content")
        compute_file_hash(data)
        assert data.tell() == 0

    def test_deterministic(self):
        """Same content produces same hash."""
        data1 = BytesIO(b"same content")
        data2 = BytesIO(b"same content")
        assert compute_file_hash(data1) == compute_file_hash(data2)

    def test_different_content_different_hash(self):
        """Different content produces different hash."""
        data1 = BytesIO(b"content A")
        data2 = BytesIO(b"content B")
        assert compute_file_hash(data1) != compute_file_hash(data2)

    def test_empty_file(self):
        """Empty file has a valid hash."""
        data = BytesIO(b"")
        result = compute_file_hash(data)
        assert len(result) == 64  # SHA-256 hex length


class TestAttachmentService:
    """Test AttachmentService business logic."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = AsyncMock()
        db.add = MagicMock()
        return db

    @pytest.fixture
    def mock_storage(self):
        """Create mock storage backend."""
        storage = AsyncMock()
        storage.put.return_value = "test/key"
        return storage

    @pytest.fixture
    def service(self, mock_db, mock_storage):
        """Create AttachmentService with mocks."""
        return AttachmentService(mock_db, mock_storage)

    @pytest.fixture
    def sample_data(self):
        """Create sample file data."""
        return BytesIO(b"PDF file content here")

    @pytest.fixture
    def sample_attachment(self):
        """Create a sample Attachment object."""
        att = MagicMock(spec=Attachment)
        att.id = str(uuid4())
        att.page_id = str(uuid4())
        att.filename = "document.pdf"
        att.original_filename = "document.pdf"
        att.mime_type = "application/pdf"
        att.file_size = 1024
        att.storage_key = "org1/page1/att1/v1/document.pdf"
        att.storage_backend = "local"
        att.content_hash = "abc123def456"
        att.version = 1
        att.status = AttachmentStatus.ACTIVE.value
        att.description = None
        att.alt_text = None
        return att

    # Upload tests

    @pytest.mark.asyncio
    async def test_upload_success(self, service, mock_storage, mock_db, sample_data):
        """Test successful file upload."""
        attachment = await service.upload(
            page_id="page-1",
            org_id="org-1",
            filename="test.pdf",
            data=sample_data,
            content_type="application/pdf",
            file_size=len(sample_data.getvalue()),
            uploaded_by_id="user-1",
        )

        assert attachment.filename == "test.pdf"
        assert attachment.mime_type == "application/pdf"
        assert attachment.version == 1
        assert attachment.status == AttachmentStatus.ACTIVE.value
        mock_storage.put.assert_called_once()
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_invalid_mime_type(self, service, sample_data):
        """Test upload with disallowed MIME type raises ValueError."""
        with pytest.raises(ValueError, match="File type not allowed"):
            await service.upload(
                page_id="page-1",
                org_id="org-1",
                filename="malware.exe",
                data=sample_data,
                content_type="application/x-msdownload",
                file_size=100,
                uploaded_by_id="user-1",
            )

    @pytest.mark.asyncio
    async def test_upload_file_too_large(self, service, sample_data):
        """Test upload with file exceeding size limit raises ValueError."""
        with pytest.raises(ValueError, match="File too large"):
            await service.upload(
                page_id="page-1",
                org_id="org-1",
                filename="huge.pdf",
                data=sample_data,
                content_type="application/pdf",
                file_size=MAX_FILE_SIZE + 1,
                uploaded_by_id="user-1",
            )

    @pytest.mark.asyncio
    async def test_upload_with_metadata(self, service, sample_data):
        """Test upload with description and alt_text."""
        attachment = await service.upload(
            page_id="page-1",
            org_id="org-1",
            filename="arch.png",
            data=sample_data,
            content_type="image/png",
            file_size=100,
            uploaded_by_id="user-1",
            description="Architecture diagram",
            alt_text="System architecture showing microservices",
            width=1920,
            height=1080,
        )

        assert attachment.description == "Architecture diagram"
        assert attachment.alt_text == "System architecture showing microservices"
        assert attachment.width == 1920
        assert attachment.height == 1080

    @pytest.mark.asyncio
    async def test_upload_sanitizes_filename(self, service, sample_data):
        """Test that filenames are sanitized on upload."""
        attachment = await service.upload(
            page_id="page-1",
            org_id="org-1",
            filename="../../../etc/test file (v2).pdf",
            data=sample_data,
            content_type="application/pdf",
            file_size=100,
            uploaded_by_id="user-1",
        )

        assert "/" not in attachment.filename
        assert ".." not in attachment.filename

    @pytest.mark.asyncio
    async def test_upload_computes_hash(self, service, sample_data):
        """Test that content hash is computed on upload."""
        attachment = await service.upload(
            page_id="page-1",
            org_id="org-1",
            filename="test.pdf",
            data=sample_data,
            content_type="application/pdf",
            file_size=len(sample_data.getvalue()),
            uploaded_by_id="user-1",
        )

        expected_hash = hashlib.sha256(sample_data.getvalue()).hexdigest()
        assert attachment.content_hash == expected_hash

    # Get/download tests

    @pytest.mark.asyncio
    async def test_get_by_id(self, service, mock_db, sample_attachment):
        """Test retrieving attachment by ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_attachment
        mock_db.execute.return_value = mock_result

        result = await service.get_by_id(sample_attachment.id)
        assert result == sample_attachment

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, service, mock_db):
        """Test retrieving non-existent attachment returns None."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await service.get_by_id("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_content(self, service, mock_storage, sample_attachment):
        """Test getting file content from storage."""
        expected = BytesIO(b"file content")
        mock_storage.get.return_value = expected

        result = await service.get_content(sample_attachment)
        assert result == expected
        mock_storage.get.assert_called_once_with(sample_attachment.storage_key)

    # List tests

    @pytest.mark.asyncio
    async def test_list_for_page(self, service, mock_db):
        """Test listing attachments for a page."""
        mock_att1 = MagicMock(spec=Attachment)
        mock_att1.id = str(uuid4())
        mock_att1.page_id = "page-1"

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_att1]
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        with patch(
            "src.modules.attachments.service.AttachmentResponse"
        ) as MockResponse:
            MockResponse.model_validate.return_value = MagicMock(id=mock_att1.id)
            result = await service.list_for_page("page-1")

        assert result.total == 1

    # Replace tests

    @pytest.mark.asyncio
    async def test_replace_attachment(
        self, service, mock_db, mock_storage, sample_attachment
    ):
        """Test replacing an attachment creates a new version."""
        new_data = BytesIO(b"Updated PDF content")

        new_attachment = await service.replace(
            attachment=sample_attachment,
            org_id="org-1",
            data=new_data,
            content_type="application/pdf",
            file_size=len(new_data.getvalue()),
            filename="document_v2.pdf",
            uploaded_by_id="user-1",
            reason="Updated diagram",
        )

        assert new_attachment.version == sample_attachment.version + 1
        assert new_attachment.replaces_id == sample_attachment.id
        assert new_attachment.status == AttachmentStatus.ACTIVE.value
        assert sample_attachment.status == AttachmentStatus.REPLACED.value
        mock_storage.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_replace_invalid_mime_type(self, service, sample_attachment):
        """Test replacing with disallowed MIME type raises ValueError."""
        with pytest.raises(ValueError, match="File type not allowed"):
            await service.replace(
                attachment=sample_attachment,
                org_id="org-1",
                data=BytesIO(b"data"),
                content_type="application/x-msdownload",
                file_size=100,
                filename="bad.exe",
                uploaded_by_id="user-1",
                reason="test",
            )

    # Delete tests

    @pytest.mark.asyncio
    async def test_soft_delete(self, service, mock_db, sample_attachment):
        """Test soft deletion sets status and reason."""
        await service.soft_delete(sample_attachment, reason="No longer needed")

        assert sample_attachment.status == AttachmentStatus.DELETED.value
        assert sample_attachment.deletion_reason == "No longer needed"

    # Manifest tests

    @pytest.mark.asyncio
    async def test_generate_manifest_with_attachments(self, service, mock_db):
        """Test manifest generation with attachments."""
        page = MagicMock()
        page.id = str(uuid4())
        page.title = "Test Page"

        # Mock list_for_page to return attachments
        from src.modules.attachments.schemas import AttachmentResponse, AttachmentListResponse
        from datetime import datetime

        mock_att = MagicMock()
        mock_att.filename = "doc.pdf"
        mock_att.mime_type = "application/pdf"
        mock_att.file_size = 245760  # ~240 KB
        mock_att.content_hash = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        mock_att.version = 1

        mock_listing = AttachmentListResponse(
            attachments=[mock_att],
            total=1,
        )

        with patch.object(service, "list_for_page", return_value=mock_listing):
            result = await service.generate_manifest_markdown(page)

        assert result is not None
        assert "# Attachments: Test Page" in result
        assert "doc.pdf" in result
        assert "application/pdf" in result
        assert "Generated:" in result

    @pytest.mark.asyncio
    async def test_generate_manifest_no_attachments(self, service, mock_db):
        """Test manifest returns None when no attachments."""
        page = MagicMock()
        page.id = str(uuid4())

        from src.modules.attachments.schemas import AttachmentListResponse

        mock_listing = AttachmentListResponse(attachments=[], total=0)

        with patch.object(service, "list_for_page", return_value=mock_listing):
            result = await service.generate_manifest_markdown(page)

        assert result is None

    # Hash collection tests

    @pytest.mark.asyncio
    async def test_get_active_hashes(self, service, mock_db):
        """Test collecting active attachment hashes for signing."""
        mock_result = MagicMock()
        mock_result.all.return_value = [("hash1",), ("hash2",), ("hash3",)]
        mock_db.execute.return_value = mock_result

        hashes = await service.get_active_hashes_for_page("page-1")
        assert hashes == ["hash1", "hash2", "hash3"]


class TestAllowedMimeTypes:
    """Test MIME type allowlist."""

    def test_common_image_types_allowed(self):
        """Common image types are in the allowlist."""
        assert "image/jpeg" in ALLOWED_MIME_TYPES
        assert "image/png" in ALLOWED_MIME_TYPES
        assert "image/gif" in ALLOWED_MIME_TYPES
        assert "image/webp" in ALLOWED_MIME_TYPES
        assert "image/svg+xml" in ALLOWED_MIME_TYPES

    def test_document_types_allowed(self):
        """Common document types are in the allowlist."""
        assert "application/pdf" in ALLOWED_MIME_TYPES
        assert "application/msword" in ALLOWED_MIME_TYPES
        assert "text/plain" in ALLOWED_MIME_TYPES
        assert "text/csv" in ALLOWED_MIME_TYPES

    def test_media_types_allowed(self):
        """Audio and video types are in the allowlist."""
        assert "audio/mpeg" in ALLOWED_MIME_TYPES
        assert "video/mp4" in ALLOWED_MIME_TYPES

    def test_executable_not_allowed(self):
        """Executable types are not in the allowlist."""
        assert "application/x-msdownload" not in ALLOWED_MIME_TYPES
        assert "application/x-executable" not in ALLOWED_MIME_TYPES


class TestAttachmentModel:
    """Test Attachment model properties."""

    def test_is_image(self):
        """Test is_image property."""
        att = Attachment()
        att.mime_type = "image/png"
        assert att.is_image is True

        att.mime_type = "application/pdf"
        assert att.is_image is False

    def test_is_video(self):
        """Test is_video property."""
        att = Attachment()
        att.mime_type = "video/mp4"
        assert att.is_video is True

        att.mime_type = "image/png"
        assert att.is_video is False

    def test_is_audio(self):
        """Test is_audio property."""
        att = Attachment()
        att.mime_type = "audio/mpeg"
        assert att.is_audio is True

    def test_human_file_size(self):
        """Test human-readable file size."""
        att = Attachment()

        att.file_size = 500
        assert att.human_file_size == "500 B"

        att.file_size = 1536
        assert "KB" in att.human_file_size

        att.file_size = 5 * 1024 * 1024
        assert "MB" in att.human_file_size

    def test_repr(self):
        """Test string representation."""
        att = Attachment()
        att.filename = "test.pdf"
        att.version = 2
        assert repr(att) == "<Attachment test.pdf (v2)>"

    def test_status_enum(self):
        """Test AttachmentStatus enum values."""
        assert AttachmentStatus.UPLOADING.value == "uploading"
        assert AttachmentStatus.ACTIVE.value == "active"
        assert AttachmentStatus.REPLACED.value == "replaced"
        assert AttachmentStatus.DELETED.value == "deleted"
