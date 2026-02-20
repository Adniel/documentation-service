"""Unit tests for Sprint G: ExportService.

Tests ZIP export generation for workspaces, spaces, and organizations.
"""

import io
import json
import zipfile

import pytest
import yaml
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.modules.portability.exporter import ExportService


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_org():
    org = MagicMock()
    org.id = str(uuid4())
    org.name = "Acme Corp"
    org.slug = "acme-corp"
    return org


@pytest.fixture
def mock_workspace(mock_org):
    ws = MagicMock()
    ws.id = str(uuid4())
    ws.name = "Engineering"
    ws.slug = "engineering"
    ws.description = "Eng docs"
    ws.is_public = False
    ws.is_active = True
    ws.organization_id = mock_org.id
    ws.organization = mock_org
    return ws


@pytest.fixture
def mock_space():
    space = MagicMock()
    space.id = str(uuid4())
    space.name = "Quality"
    space.slug = "quality"
    space.description = "QMS"
    space.diataxis_type = "how_to"
    space.classification = 1
    space.sort_order = 0
    space.is_active = True
    return space


@pytest.fixture
def mock_page():
    page = MagicMock()
    page.id = str(uuid4())
    page.title = "Inspection Procedure"
    page.slug = "inspection-procedure"
    page.document_number = "SOP-042"
    page.revision = "B"
    page.version = "2.1"
    page.status = "effective"
    page.classification = "internal"
    page.diataxis_types = ["how_to"]
    page.summary = "How to inspect vials"
    page.content = {"type": "doc", "content": []}
    page.effective_date = None
    page.next_review_date = None
    page.review_cycle_months = 12
    page.requires_training = True
    page.training_validity_months = 24
    page.sort_order = 0
    page.is_template = False
    page.is_active = True
    page.created_at = None
    page.updated_at = None
    return page


class TestExportSpace:
    """Test exporting a single space."""

    @pytest.mark.asyncio
    async def test_export_space_creates_zip(
        self, mock_db, mock_space, mock_workspace, mock_org, mock_page
    ):
        service = ExportService(mock_db)

        # Mock DB queries
        mock_space.workspace = mock_workspace

        # _get_space_with_workspace
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = mock_space

        # _get_org
        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = mock_org

        # _get_space_pages
        mock_result3 = MagicMock()
        mock_result3.scalars.return_value.all.return_value = [mock_page]

        mock_db.execute.side_effect = [mock_result1, mock_result2, mock_result3]

        buf, filename, stats = await service.export_space(
            mock_space.id, "user@example.com"
        )

        assert isinstance(buf, io.BytesIO)
        assert filename.endswith(".zip")
        assert "acme-corp" in filename
        assert stats["spaces"] == 1
        assert stats["pages"] == 1

    @pytest.mark.asyncio
    async def test_export_zip_contains_metadata(
        self, mock_db, mock_space, mock_workspace, mock_org, mock_page
    ):
        service = ExportService(mock_db)

        mock_space.workspace = mock_workspace

        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = mock_space
        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = mock_org
        mock_result3 = MagicMock()
        mock_result3.scalars.return_value.all.return_value = [mock_page]

        mock_db.execute.side_effect = [mock_result1, mock_result2, mock_result3]

        buf, _, _ = await service.export_space(mock_space.id, "user@example.com")

        with zipfile.ZipFile(buf, "r") as zf:
            names = zf.namelist()

            # Should contain manifest
            manifest_files = [n for n in names if n.endswith("manifest.yaml")]
            assert len(manifest_files) == 1

            # Should contain space metadata
            space_meta_files = [n for n in names if n.endswith("_space.yaml")]
            assert len(space_meta_files) == 1

            # Should contain page metadata
            page_meta_files = [n for n in names if n.endswith("_meta.yaml")]
            assert len(page_meta_files) == 1

            # Should contain page content
            content_files = [n for n in names if n.endswith("content.json")]
            assert len(content_files) == 1

            # Validate manifest content
            manifest_data = yaml.safe_load(zf.read(manifest_files[0]))
            assert manifest_data["platform"] == "documentation-service"
            assert manifest_data["format_version"] == "1.0"

            # Validate page metadata
            page_meta = yaml.safe_load(zf.read(page_meta_files[0]))
            assert page_meta["title"] == "Inspection Procedure"
            assert page_meta["document_number"] == "SOP-042"
            assert page_meta["diataxis_types"] == ["how_to"]


class TestExportWorkspace:
    """Test exporting a workspace."""

    @pytest.mark.asyncio
    async def test_export_workspace_stats(
        self, mock_db, mock_workspace, mock_org, mock_space, mock_page
    ):
        service = ExportService(mock_db)

        mock_workspace.organization = mock_org

        # _get_workspace_with_org
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = mock_workspace

        # _get_workspace_spaces
        mock_result2 = MagicMock()
        mock_result2.scalars.return_value.all.return_value = [mock_space]

        # _get_space_pages
        mock_result3 = MagicMock()
        mock_result3.scalars.return_value.all.return_value = [mock_page]

        mock_db.execute.side_effect = [mock_result1, mock_result2, mock_result3]

        buf, filename, stats = await service.export_workspace(
            mock_workspace.id, "user@example.com"
        )

        assert stats["workspaces"] == 1
        assert stats["spaces"] == 1
        assert stats["pages"] == 1


class TestExportWithoutContent:
    """Test exporting with content excluded."""

    @pytest.mark.asyncio
    async def test_no_content_json_when_excluded(
        self, mock_db, mock_space, mock_workspace, mock_org, mock_page
    ):
        service = ExportService(mock_db)

        mock_space.workspace = mock_workspace

        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = mock_space
        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = mock_org
        mock_result3 = MagicMock()
        mock_result3.scalars.return_value.all.return_value = [mock_page]

        mock_db.execute.side_effect = [mock_result1, mock_result2, mock_result3]

        buf, _, _ = await service.export_space(
            mock_space.id, "user@example.com", include_content=False
        )

        with zipfile.ZipFile(buf, "r") as zf:
            names = zf.namelist()
            content_files = [n for n in names if n.endswith("content.json")]
            assert len(content_files) == 0

            # Metadata should still be present
            meta_files = [n for n in names if n.endswith("_meta.yaml")]
            assert len(meta_files) == 1
