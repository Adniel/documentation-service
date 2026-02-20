"""Unit tests for Sprint G: MetadataSyncService.

Tests YAML metadata generation, reading, and writing for portability.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

import yaml

from src.modules.portability.metadata_service import MetadataSyncService
from src.modules.portability.schemas import PageMeta, SpaceMeta, WorkspaceMeta


@pytest.fixture
def tmp_repo(tmp_path):
    """Create a fake repo directory structure."""
    org_dir = tmp_path / "test-org"
    org_dir.mkdir()
    ws_dir = org_dir / "engineering"
    ws_dir.mkdir()
    space_dir = ws_dir / "quality"
    space_dir.mkdir()
    return tmp_path


@pytest.fixture
def mock_git_service(tmp_repo):
    """Create a mock GitService pointing at tmp_repo."""
    git = MagicMock()
    git._get_repo_path.return_value = tmp_repo / "test-org"
    git.get_repo.return_value = MagicMock()
    git._get_signature.return_value = MagicMock()
    return git


@pytest.fixture
def meta_service(mock_git_service):
    return MetadataSyncService(mock_git_service)


class TestBuildPageMeta:
    """Test building PageMeta from Page model."""

    def test_basic_page(self, meta_service):
        page = MagicMock()
        page.title = "Getting Started"
        page.slug = "getting-started"
        page.document_number = "SOP-001"
        page.revision = "A"
        page.version = "1.0"
        page.status = "draft"
        page.classification = "public"
        page.diataxis_types = ["tutorial"]
        page.summary = "A getting started guide"
        page.effective_date = None
        page.next_review_date = None
        page.review_cycle_months = None
        page.requires_training = False
        page.training_validity_months = None
        page.sort_order = 0
        page.is_template = False
        page.created_at = None
        page.updated_at = None

        meta = meta_service.build_page_meta(page, author_email="test@example.com")

        assert meta.title == "Getting Started"
        assert meta.slug == "getting-started"
        assert meta.document_number == "SOP-001"
        assert meta.diataxis_types == ["tutorial"]
        assert meta.author_email == "test@example.com"
        assert meta.status == "draft"

    def test_page_without_optional_fields(self, meta_service):
        page = MagicMock()
        page.title = "Minimal"
        page.slug = "minimal"
        page.document_number = None
        page.revision = None
        page.version = "1.0"
        page.status = "draft"
        page.classification = "internal"
        page.diataxis_types = []
        page.summary = None
        page.effective_date = None
        page.next_review_date = None
        page.review_cycle_months = None
        page.requires_training = False
        page.training_validity_months = None
        page.sort_order = 0
        page.is_template = False
        page.created_at = None
        page.updated_at = None

        meta = meta_service.build_page_meta(page)

        assert meta.title == "Minimal"
        assert meta.document_number is None
        assert meta.author_email is None


class TestWriteReadPageMeta:
    """Test writing and reading _meta.yaml."""

    def test_write_and_read(self, meta_service, tmp_repo):
        meta = PageMeta(
            title="Test Page",
            slug="test-page",
            version="1.0",
            status="draft",
            classification="public",
            diataxis_types=["tutorial", "how_to"],
        )

        meta_service.write_page_meta(
            "test-org", "engineering", "quality", "test-page", meta
        )

        # Verify file exists
        meta_path = tmp_repo / "test-org" / "engineering" / "quality" / "test-page_meta.yaml"
        assert meta_path.exists()

        # Read back
        read_meta = meta_service.read_page_meta(
            "test-org", "engineering", "quality", "test-page"
        )
        assert read_meta is not None
        assert read_meta.title == "Test Page"
        assert read_meta.diataxis_types == ["tutorial", "how_to"]
        assert read_meta.status == "draft"

    def test_read_nonexistent(self, meta_service):
        result = meta_service.read_page_meta(
            "test-org", "engineering", "quality", "nonexistent"
        )
        assert result is None

    def test_yaml_content(self, meta_service, tmp_repo):
        meta = PageMeta(
            title="YAML Test",
            slug="yaml-test",
            document_number="SOP-042",
            version="2.1",
            status="effective",
            classification="internal",
            diataxis_types=["how_to"],
            review_cycle_months=12,
        )

        meta_service.write_page_meta(
            "test-org", "engineering", "quality", "yaml-test", meta
        )

        meta_path = tmp_repo / "test-org" / "engineering" / "quality" / "yaml-test_meta.yaml"
        raw = yaml.safe_load(meta_path.read_text())

        assert raw["document_number"] == "SOP-042"
        assert raw["review_cycle_months"] == 12
        assert raw["diataxis_types"] == ["how_to"]

    def test_excludes_none_values(self, meta_service, tmp_repo):
        meta = PageMeta(
            title="Sparse",
            slug="sparse",
            status="draft",
        )

        meta_service.write_page_meta(
            "test-org", "engineering", "quality", "sparse", meta
        )

        meta_path = tmp_repo / "test-org" / "engineering" / "quality" / "sparse_meta.yaml"
        raw = yaml.safe_load(meta_path.read_text())

        assert "document_number" not in raw
        assert "effective_date" not in raw
        assert "title" in raw


class TestWriteReadSpaceMeta:
    """Test writing and reading _space.yaml."""

    def test_write_and_read(self, meta_service, tmp_repo):
        meta = SpaceMeta(
            name="Quality Management",
            slug="quality",
            description="QMS documentation",
            diataxis_type="how_to",
            classification=1,
            sort_order=0,
        )

        meta_service.write_space_meta("test-org", "engineering", "quality", meta)

        space_path = tmp_repo / "test-org" / "engineering" / "quality" / "_space.yaml"
        assert space_path.exists()

        read_meta = meta_service.read_space_meta("test-org", "engineering", "quality")
        assert read_meta is not None
        assert read_meta.name == "Quality Management"
        assert read_meta.diataxis_type == "how_to"
        assert read_meta.classification == 1

    def test_read_nonexistent(self, meta_service):
        result = meta_service.read_space_meta("test-org", "engineering", "nonexistent")
        assert result is None


class TestWriteReadWorkspaceMeta:
    """Test writing and reading _workspace.yaml."""

    def test_write_and_read(self, meta_service, tmp_repo):
        meta = WorkspaceMeta(
            name="Engineering",
            slug="engineering",
            description="Engineering docs",
            is_public=False,
        )

        meta_service.write_workspace_meta("test-org", "engineering", meta)

        ws_path = tmp_repo / "test-org" / "engineering" / "_workspace.yaml"
        assert ws_path.exists()

        read_meta = meta_service.read_workspace_meta("test-org", "engineering")
        assert read_meta is not None
        assert read_meta.name == "Engineering"
        assert read_meta.is_public is False


class TestBuildSpaceMeta:
    """Test building SpaceMeta from Space model."""

    def test_basic_space(self, meta_service):
        space = MagicMock()
        space.name = "Quality"
        space.slug = "quality"
        space.description = "QMS docs"
        space.diataxis_type = "reference"
        space.classification = 2
        space.sort_order = 1

        meta = meta_service.build_space_meta(space)

        assert meta.name == "Quality"
        assert meta.diataxis_type == "reference"
        assert meta.classification == 2


class TestBuildWorkspaceMeta:
    """Test building WorkspaceMeta from Workspace model."""

    def test_basic_workspace(self, meta_service):
        ws = MagicMock()
        ws.name = "Engineering"
        ws.slug = "engineering"
        ws.description = "Eng docs"
        ws.is_public = True

        meta = meta_service.build_workspace_meta(ws)

        assert meta.name == "Engineering"
        assert meta.is_public is True
