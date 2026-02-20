"""Unit tests for Sprint E: Diataxis Revision.

Tests per-page diataxis_types field handling in service layer and schemas.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.db.models.page import Page
from src.db.models.space import DiataxisType
from src.modules.content.schemas import (
    DiataxisType as SchemaDiataxisType,
    PageCreate,
    PageUpdate,
    PageResponse,
    PageSummary,
)


class TestPageModel:
    """Test Page model diataxis_types field."""

    def test_default_diataxis_types(self):
        """Page model has empty list default for diataxis_types."""
        page = Page(
            title="Test",
            slug="test",
            space_id=str(uuid4()),
            author_id=str(uuid4()),
        )
        assert page.diataxis_types == [] or page.diataxis_types is None

    def test_set_diataxis_types(self):
        """Page can store multiple diataxis types."""
        page = Page(
            title="Test",
            slug="test",
            space_id=str(uuid4()),
            author_id=str(uuid4()),
            diataxis_types=["tutorial", "how_to"],
        )
        assert page.diataxis_types == ["tutorial", "how_to"]

    def test_single_diataxis_type(self):
        """Page can store a single diataxis type."""
        page = Page(
            title="Test",
            slug="test",
            space_id=str(uuid4()),
            author_id=str(uuid4()),
            diataxis_types=["reference"],
        )
        assert page.diataxis_types == ["reference"]


class TestSchemas:
    """Test Pydantic schema changes for diataxis_types."""

    def test_page_create_default_none(self):
        """PageCreate diataxis_types defaults to None (inherit from space)."""
        page = PageCreate(
            title="Test",
            slug="test",
            space_id=str(uuid4()),
        )
        assert page.diataxis_types is None

    def test_page_create_with_types(self):
        """PageCreate accepts explicit diataxis_types."""
        page = PageCreate(
            title="Test",
            slug="test",
            space_id=str(uuid4()),
            diataxis_types=[SchemaDiataxisType.TUTORIAL, SchemaDiataxisType.HOW_TO],
        )
        assert len(page.diataxis_types) == 2
        assert SchemaDiataxisType.TUTORIAL in page.diataxis_types

    def test_page_create_empty_list(self):
        """PageCreate accepts empty list (no types)."""
        page = PageCreate(
            title="Test",
            slug="test",
            space_id=str(uuid4()),
            diataxis_types=[],
        )
        assert page.diataxis_types == []

    def test_page_update_with_types(self):
        """PageUpdate can set diataxis_types."""
        update = PageUpdate(
            diataxis_types=[SchemaDiataxisType.REFERENCE],
        )
        assert update.diataxis_types == [SchemaDiataxisType.REFERENCE]

    def test_page_update_without_types(self):
        """PageUpdate without diataxis_types leaves field unset."""
        update = PageUpdate(title="New Title")
        data = update.model_dump(exclude_unset=True)
        assert "diataxis_types" not in data

    def test_page_response_includes_types(self):
        """PageResponse includes diataxis_types."""
        response = PageResponse(
            id=str(uuid4()),
            title="Test",
            slug="test",
            space_id=str(uuid4()),
            author_id=str(uuid4()),
            parent_id=None,
            document_number=None,
            version="1.0",
            status="draft",
            classification="public",
            diataxis_types=["tutorial"],
            content=None,
            summary=None,
            git_path=None,
            git_commit_sha=None,
            is_active=True,
            is_template=False,
            sort_order=0,
            created_at="2026-02-20T00:00:00Z",
            updated_at="2026-02-20T00:00:00Z",
        )
        assert response.diataxis_types == ["tutorial"]

    def test_page_response_empty_types(self):
        """PageResponse defaults to empty list."""
        response = PageResponse(
            id=str(uuid4()),
            title="Test",
            slug="test",
            space_id=str(uuid4()),
            author_id=str(uuid4()),
            parent_id=None,
            document_number=None,
            version="1.0",
            status="draft",
            classification="public",
            content=None,
            summary=None,
            git_path=None,
            git_commit_sha=None,
            is_active=True,
            is_template=False,
            sort_order=0,
            created_at="2026-02-20T00:00:00Z",
            updated_at="2026-02-20T00:00:00Z",
        )
        assert response.diataxis_types == []

    def test_page_summary_includes_types(self):
        """PageSummary includes diataxis_types."""
        summary = PageSummary(
            id=str(uuid4()),
            title="Test",
            slug="test",
            status="draft",
            version="1.0",
            diataxis_types=["how_to", "reference"],
            updated_at="2026-02-20T00:00:00Z",
        )
        assert summary.diataxis_types == ["how_to", "reference"]


class TestContentServiceDiataxis:
    """Test content service diataxis_types handling."""

    @pytest.mark.asyncio
    async def test_create_page_inherits_from_space(self):
        """create_page inherits diataxis_type from space when not specified."""
        from src.modules.content.service import create_page

        mock_db = AsyncMock()

        # Mock space lookup
        mock_space = MagicMock()
        mock_space.diataxis_type = "tutorial"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_space
        mock_db.execute.return_value = mock_result

        page_in = PageCreate(
            title="Test Page",
            slug="test-page",
            space_id=str(uuid4()),
        )

        # Mock the Page constructor by patching
        with patch("src.modules.content.service.Page") as MockPage:
            mock_page = MagicMock()
            MockPage.return_value = mock_page

            await create_page(mock_db, page_in, str(uuid4()))

            # Verify Page was called with inherited diataxis_types
            call_kwargs = MockPage.call_args
            assert call_kwargs.kwargs["diataxis_types"] == ["tutorial"]

    @pytest.mark.asyncio
    async def test_create_page_mixed_space_empty_types(self):
        """Pages in 'mixed' spaces get empty diataxis_types."""
        from src.modules.content.service import create_page

        mock_db = AsyncMock()

        mock_space = MagicMock()
        mock_space.diataxis_type = "mixed"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_space
        mock_db.execute.return_value = mock_result

        page_in = PageCreate(
            title="Test Page",
            slug="test-page",
            space_id=str(uuid4()),
        )

        with patch("src.modules.content.service.Page") as MockPage:
            mock_page = MagicMock()
            MockPage.return_value = mock_page

            await create_page(mock_db, page_in, str(uuid4()))

            call_kwargs = MockPage.call_args
            assert call_kwargs.kwargs["diataxis_types"] == []

    @pytest.mark.asyncio
    async def test_create_page_explicit_types(self):
        """Explicit diataxis_types override space default."""
        from src.modules.content.service import create_page

        mock_db = AsyncMock()

        page_in = PageCreate(
            title="Test Page",
            slug="test-page",
            space_id=str(uuid4()),
            diataxis_types=[SchemaDiataxisType.REFERENCE, SchemaDiataxisType.EXPLANATION],
        )

        with patch("src.modules.content.service.Page") as MockPage:
            mock_page = MagicMock()
            MockPage.return_value = mock_page

            await create_page(mock_db, page_in, str(uuid4()))

            call_kwargs = MockPage.call_args
            assert call_kwargs.kwargs["diataxis_types"] == ["reference", "explanation"]

    @pytest.mark.asyncio
    async def test_update_page_sets_types(self):
        """update_page correctly sets diataxis_types."""
        from src.modules.content.service import update_page

        mock_db = AsyncMock()
        mock_page = MagicMock()
        mock_page.diataxis_types = []

        page_in = PageUpdate(
            diataxis_types=[SchemaDiataxisType.TUTORIAL],
        )

        result = await update_page(mock_db, mock_page, page_in)

        # Verify diataxis_types was set
        assert mock_page.diataxis_types == ["tutorial"]


class TestDiataxisTypeEnum:
    """Test DiataxisType enum values."""

    def test_all_types_present(self):
        """All 5 Diataxis types are defined."""
        assert DiataxisType.TUTORIAL.value == "tutorial"
        assert DiataxisType.HOW_TO.value == "how_to"
        assert DiataxisType.REFERENCE.value == "reference"
        assert DiataxisType.EXPLANATION.value == "explanation"
        assert DiataxisType.MIXED.value == "mixed"

    def test_schema_enum_matches_model(self):
        """Schema DiataxisType matches model DiataxisType values."""
        for schema_type in SchemaDiataxisType:
            assert schema_type.value in [t.value for t in DiataxisType]
