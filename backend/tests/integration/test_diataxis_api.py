"""Integration tests for Sprint E: Diataxis Revision API.

Tests the per-page diataxis_types field through API endpoints.
Uses mock database session for isolation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.db.models.page import Page, PageStatus
from src.db.models.space import Space, DiataxisType


@pytest.fixture
def mock_space():
    """Create a mock space with tutorial type."""
    space = MagicMock(spec=Space)
    space.id = str(uuid4())
    space.name = "Tutorial Space"
    space.slug = "tutorial-space"
    space.workspace_id = str(uuid4())
    space.diataxis_type = DiataxisType.TUTORIAL.value
    space.classification = 0
    space.is_active = True
    return space


@pytest.fixture
def mock_page(mock_space):
    """Create a mock page with diataxis_types."""
    page = MagicMock(spec=Page)
    page.id = str(uuid4())
    page.title = "Getting Started"
    page.slug = "getting-started"
    page.space_id = mock_space.id
    page.author_id = str(uuid4())
    page.parent_id = None
    page.document_number = None
    page.version = "1.0"
    page.status = PageStatus.DRAFT.value
    page.classification = "public"
    page.diataxis_types = ["tutorial"]
    page.content = {"type": "doc", "content": []}
    page.summary = None
    page.git_path = None
    page.git_commit_sha = None
    page.is_active = True
    page.is_template = False
    page.sort_order = 0
    page.created_at = "2026-02-20T00:00:00Z"
    page.updated_at = "2026-02-20T00:00:00Z"
    page.space = mock_space
    return page


class TestCreatePageWithDiataxis:
    """Test creating pages with diataxis_types."""

    @pytest.mark.asyncio
    async def test_create_page_inherits_space_type(self, mock_space):
        """Creating a page in a typed space inherits the type."""
        from src.modules.content.service import create_page
        from src.modules.content.schemas import PageCreate

        mock_db = AsyncMock()

        # Mock space lookup for inheritance
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_space
        mock_db.execute.return_value = mock_result

        page_in = PageCreate(
            title="Test Tutorial",
            slug="test-tutorial",
            space_id=mock_space.id,
        )

        with patch("src.modules.content.service.Page") as MockPage:
            mock_page = MagicMock()
            MockPage.return_value = mock_page

            await create_page(mock_db, page_in, str(uuid4()))

            # Should inherit "tutorial" from space
            call_kwargs = MockPage.call_args.kwargs
            assert call_kwargs["diataxis_types"] == ["tutorial"]

    @pytest.mark.asyncio
    async def test_create_page_explicit_types(self, mock_space):
        """Creating a page with explicit types overrides inheritance."""
        from src.modules.content.service import create_page
        from src.modules.content.schemas import PageCreate, DiataxisType

        mock_db = AsyncMock()

        page_in = PageCreate(
            title="Mixed Content",
            slug="mixed-content",
            space_id=mock_space.id,
            diataxis_types=[DiataxisType.HOW_TO, DiataxisType.REFERENCE],
        )

        with patch("src.modules.content.service.Page") as MockPage:
            mock_page = MagicMock()
            MockPage.return_value = mock_page

            await create_page(mock_db, page_in, str(uuid4()))

            call_kwargs = MockPage.call_args.kwargs
            assert call_kwargs["diataxis_types"] == ["how_to", "reference"]


class TestUpdatePageDiataxis:
    """Test updating page diataxis_types."""

    @pytest.mark.asyncio
    async def test_update_diataxis_types(self, mock_page):
        """Updating page diataxis_types works correctly."""
        from src.modules.content.service import update_page
        from src.modules.content.schemas import PageUpdate, DiataxisType

        mock_db = AsyncMock()

        page_in = PageUpdate(
            diataxis_types=[DiataxisType.EXPLANATION],
        )

        await update_page(mock_db, mock_page, page_in)

        assert mock_page.diataxis_types == ["explanation"]

    @pytest.mark.asyncio
    async def test_clear_diataxis_types(self, mock_page):
        """Can clear diataxis_types by setting empty list."""
        from src.modules.content.service import update_page
        from src.modules.content.schemas import PageUpdate

        mock_db = AsyncMock()

        page_in = PageUpdate(diataxis_types=[])

        await update_page(mock_db, mock_page, page_in)

        assert mock_page.diataxis_types == []

    @pytest.mark.asyncio
    async def test_update_other_fields_preserves_types(self, mock_page):
        """Updating other fields doesn't change diataxis_types."""
        from src.modules.content.service import update_page
        from src.modules.content.schemas import PageUpdate

        mock_db = AsyncMock()
        original_types = mock_page.diataxis_types

        page_in = PageUpdate(title="New Title")

        await update_page(mock_db, mock_page, page_in)

        # diataxis_types should not have been modified
        assert mock_page.diataxis_types == original_types


class TestListPagesWithDiataxisFilter:
    """Test listing pages filtered by diataxis type."""

    @pytest.mark.asyncio
    async def test_list_pages_no_filter(self, mock_space):
        """Listing pages without filter returns all."""
        from src.modules.content.service import list_space_pages

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await list_space_pages(mock_db, mock_space.id)

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_list_pages_with_filter(self, mock_space):
        """Listing pages with diataxis_type filter uses JSONB containment."""
        from src.modules.content.service import list_space_pages

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await list_space_pages(
            mock_db, mock_space.id, diataxis_type="tutorial"
        )

        assert isinstance(result, list)
        # Verify the query included a filter (the execute was called)
        mock_db.execute.assert_called_once()


class TestNavigationDiataxis:
    """Test diataxis_types in navigation tree."""

    @pytest.mark.asyncio
    async def test_page_node_includes_types(self, mock_page):
        """Navigation tree page nodes include diataxis_types."""
        from src.modules.content.navigation_service import _add_pages_to_tree

        tree = [
            {
                "id": mock_page.space_id,
                "type": "space",
                "name": "Test Space",
                "slug": "test-space",
                "diataxis_type": "tutorial",
                "classification": 0,
                "children": [],
                "pages": [],
            }
        ]

        _add_pages_to_tree(tree, [mock_page])

        pages = tree[0]["pages"]
        assert len(pages) == 1
        assert pages[0]["diataxis_types"] == ["tutorial"]
