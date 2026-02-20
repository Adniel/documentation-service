"""Integration tests for Sprint G: Portability API.

Tests export/import API endpoints with mock database sessions.
"""

import io
import json
import zipfile

import pytest
import yaml
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.modules.portability.exporter import ExportService
from src.modules.portability.importer import ImportService
from src.modules.portability.schemas import (
    ConflictAction,
    ImportExecuteRequest,
    ImportFormat,
    ImportItemStatus,
)


@pytest.fixture
def mock_org():
    org = MagicMock()
    org.id = str(uuid4())
    org.name = "Test Org"
    org.slug = "test-org"
    return org


@pytest.fixture
def mock_workspace(mock_org):
    ws = MagicMock()
    ws.id = str(uuid4())
    ws.name = "Docs"
    ws.slug = "docs"
    ws.description = "Documentation"
    ws.is_public = False
    ws.is_active = True
    ws.organization_id = mock_org.id
    ws.organization = mock_org
    return ws


@pytest.fixture
def mock_space():
    space = MagicMock()
    space.id = str(uuid4())
    space.name = "Guides"
    space.slug = "guides"
    space.description = "How-to guides"
    space.diataxis_type = "how_to"
    space.classification = 0
    space.sort_order = 0
    space.is_active = True
    return space


@pytest.fixture
def mock_pages():
    pages = []
    for i in range(3):
        page = MagicMock()
        page.id = str(uuid4())
        page.title = f"Page {i+1}"
        page.slug = f"page-{i+1}"
        page.document_number = f"DOC-{i+1:03d}"
        page.revision = "A"
        page.version = "1.0"
        page.status = "draft"
        page.classification = "public"
        page.diataxis_types = ["how_to"]
        page.summary = f"Summary for page {i+1}"
        page.content = {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": f"Content {i+1}"}]}]}
        page.effective_date = None
        page.next_review_date = None
        page.review_cycle_months = None
        page.requires_training = False
        page.training_validity_months = None
        page.sort_order = i
        page.is_template = False
        page.is_active = True
        page.created_at = None
        page.updated_at = None
        pages.append(page)
    return pages


class TestExportImportRoundTrip:
    """Test export then import preserves content."""

    @pytest.mark.asyncio
    async def test_export_creates_valid_zip(
        self, mock_workspace, mock_org, mock_space, mock_pages
    ):
        """Export produces a valid ZIP with correct structure."""
        mock_db = AsyncMock()
        mock_space.workspace = mock_workspace

        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = mock_space
        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = mock_org
        mock_result3 = MagicMock()
        mock_result3.scalars.return_value.all.return_value = mock_pages

        mock_db.execute.side_effect = [mock_result1, mock_result2, mock_result3]

        export_service = ExportService(mock_db)
        buf, filename, stats = await export_service.export_space(
            mock_space.id, "admin@test.com"
        )

        assert stats["pages"] == 3
        assert stats["spaces"] == 1

        with zipfile.ZipFile(buf, "r") as zf:
            names = zf.namelist()

            # Check structure
            manifest_files = [n for n in names if "manifest.yaml" in n]
            space_meta_files = [n for n in names if "_space.yaml" in n]
            page_meta_files = [n for n in names if "_meta.yaml" in n]
            content_files = [n for n in names if "content.json" in n]

            assert len(manifest_files) == 1
            assert len(space_meta_files) == 1
            assert len(page_meta_files) == 3
            assert len(content_files) == 3

            # Validate page metadata
            for pmf in page_meta_files:
                meta = yaml.safe_load(zf.read(pmf))
                assert "title" in meta
                assert "slug" in meta
                assert "diataxis_types" in meta

    @pytest.mark.asyncio
    async def test_import_preview_markdown(self, tmp_path):
        """Import preview correctly parses Markdown files."""
        # Create test Markdown files
        (tmp_path / "intro.md").write_text("# Introduction\n\nWelcome.")
        (tmp_path / "setup.md").write_text("# Setup Guide\n\nSteps here.")
        (tmp_path / "faq.md").write_text("# FAQ\n\nQ: How?\nA: Like this.")

        mock_db = AsyncMock()
        import_service = ImportService(mock_db)

        preview = await import_service.preview(
            tmp_path,
            target_workspace_id=str(uuid4()),
        )

        assert preview.format_detected == ImportFormat.MARKDOWN
        assert len(preview.items) == 3
        assert preview.statistics["create"] == 3
        assert preview.statistics["total"] == 3
        assert all(i.item_type == "page" for i in preview.items)

    @pytest.mark.asyncio
    async def test_import_preview_confluence(self, tmp_path):
        """Import preview detects Confluence format."""
        (tmp_path / "page1.html").write_text(
            "<html><head><title>Config Guide</title></head>"
            "<body>Confluence export content</body></html>"
        )

        mock_db = AsyncMock()
        import_service = ImportService(mock_db)

        preview = await import_service.preview(
            tmp_path,
            target_workspace_id=str(uuid4()),
        )

        assert preview.format_detected == ImportFormat.CONFLUENCE
        assert len(preview.items) == 1
        assert preview.items[0].title == "Config Guide"

    @pytest.mark.asyncio
    async def test_import_preview_docservice(self, tmp_path):
        """Import preview detects docservice format."""
        export_dir = tmp_path / "export-test"
        export_dir.mkdir()
        (export_dir / "manifest.yaml").write_text(yaml.dump({
            "platform": "documentation-service",
            "format_version": "1.0",
        }))

        ws_dir = export_dir / "workspaces" / "docs" / "spaces" / "guides" / "pages" / "intro"
        ws_dir.mkdir(parents=True)
        (ws_dir / "_meta.yaml").write_text(yaml.dump({
            "title": "Introduction",
            "slug": "intro",
            "status": "draft",
        }))
        (ws_dir / "content.json").write_text(json.dumps({
            "type": "doc", "content": [],
        }))

        mock_db = AsyncMock()
        import_service = ImportService(mock_db)

        preview = await import_service.preview(
            tmp_path,
            target_workspace_id=str(uuid4()),
        )

        assert preview.format_detected == ImportFormat.DOCSERVICE
        assert len(preview.items) >= 1

    @pytest.mark.asyncio
    async def test_import_conflict_detection(self, tmp_path):
        """Import detects conflicts with existing pages."""
        (tmp_path / "intro.md").write_text("# Introduction")

        mock_db = AsyncMock()

        # Mock existing page with same slug
        mock_result = MagicMock()
        mock_result.all.return_value = [("intro", str(uuid4()))]
        mock_db.execute.return_value = mock_result

        import_service = ImportService(mock_db)
        space_id = str(uuid4())

        preview = await import_service.preview(
            tmp_path,
            target_workspace_id=str(uuid4()),
            target_space_id=space_id,
        )

        conflicts = [i for i in preview.items if i.status == ImportItemStatus.CONFLICT]
        assert len(conflicts) == 1
        assert "already exists" in conflicts[0].conflict_reason

    @pytest.mark.asyncio
    async def test_import_execute_creates_pages(self, tmp_path):
        """Import execution creates pages in the database."""
        (tmp_path / "guide.md").write_text("# Quick Guide\n\nSteps...")

        mock_db = AsyncMock()

        # No existing pages
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        import_service = ImportService(mock_db)
        space_id = str(uuid4())

        request = ImportExecuteRequest(
            target_workspace_id=str(uuid4()),
            target_space_id=space_id,
            default_conflict_action=ConflictAction.SKIP,
        )

        result = await import_service.execute(
            tmp_path, request, author_id=str(uuid4())
        )

        assert result.total == 1
        assert result.created == 1
        assert result.errors == 0
        assert mock_db.add.called

    @pytest.mark.asyncio
    async def test_import_execute_skip_conflicts(self, tmp_path):
        """Import skips conflicting items when configured to skip."""
        (tmp_path / "existing.md").write_text("# Existing Page")

        mock_db = AsyncMock()

        # Existing page
        existing = MagicMock()
        existing.id = str(uuid4())
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_db.execute.return_value = mock_result

        import_service = ImportService(mock_db)

        request = ImportExecuteRequest(
            target_workspace_id=str(uuid4()),
            target_space_id=str(uuid4()),
            default_conflict_action=ConflictAction.SKIP,
        )

        result = await import_service.execute(
            tmp_path, request, author_id=str(uuid4())
        )

        assert result.skipped == 1
        assert result.created == 0
