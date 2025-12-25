"""Unit tests for navigation service (Sprint 3)."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from src.modules.content.navigation_service import (
    _build_space_tree,
    _add_pages_to_tree,
)


class TestBuildSpaceTree:
    """Tests for space tree building logic."""

    def test_build_empty_tree(self):
        """Empty space list should return empty tree."""
        result = _build_space_tree([], parent_id=None, max_depth=3)
        assert result == []

    def test_build_flat_tree(self):
        """Spaces without parents should be top-level."""
        # Create mock space objects with proper attribute configuration
        space1 = MagicMock()
        space1.id = "space-1"
        space1.name = "Space 1"
        space1.slug = "space-1"
        space1.parent_id = None
        space1.diataxis_type = "tutorial"
        space1.classification = 0

        space2 = MagicMock()
        space2.id = "space-2"
        space2.name = "Space 2"
        space2.slug = "space-2"
        space2.parent_id = None
        space2.diataxis_type = "how_to"
        space2.classification = 0

        spaces = [space1, space2]

        result = _build_space_tree(spaces, parent_id=None, max_depth=3)

        assert len(result) == 2
        assert result[0]["id"] == "space-1"
        assert result[0]["name"] == "Space 1"
        assert result[0]["type"] == "space"
        assert result[1]["id"] == "space-2"

    def test_build_nested_tree(self):
        """Nested spaces should have correct parent-child relationship."""
        spaces = [
            MagicMock(
                id="parent",
                name="Parent Space",
                slug="parent",
                parent_id=None,
                diataxis_type="tutorial",
                classification=0,
            ),
            MagicMock(
                id="child",
                name="Child Space",
                slug="child",
                parent_id="parent",
                diataxis_type="tutorial",
                classification=0,
            ),
        ]

        result = _build_space_tree(spaces, parent_id=None, max_depth=3)

        assert len(result) == 1
        assert result[0]["id"] == "parent"
        assert len(result[0]["children"]) == 1
        assert result[0]["children"][0]["id"] == "child"

    def test_build_tree_respects_max_depth(self):
        """Tree building should stop at max_depth."""
        spaces = [
            MagicMock(id="level-0", name="Level 0", slug="l0", parent_id=None, diataxis_type="tutorial", classification=0),
            MagicMock(id="level-1", name="Level 1", slug="l1", parent_id="level-0", diataxis_type="tutorial", classification=0),
            MagicMock(id="level-2", name="Level 2", slug="l2", parent_id="level-1", diataxis_type="tutorial", classification=0),
            MagicMock(id="level-3", name="Level 3", slug="l3", parent_id="level-2", diataxis_type="tutorial", classification=0),
        ]

        result = _build_space_tree(spaces, parent_id=None, max_depth=2)

        assert len(result) == 1
        assert len(result[0]["children"]) == 1
        # Level 2 should be empty (max_depth=2 means depth 0 and 1 only)
        assert result[0]["children"][0]["children"] == []


class TestAddPagesToTree:
    """Tests for adding pages to space tree."""

    def test_add_pages_empty_tree(self):
        """Adding pages to empty tree should be a no-op."""
        tree = []
        pages = [MagicMock(id="page-1", space_id="space-1")]

        _add_pages_to_tree(tree, pages)

        assert tree == []

    def test_add_pages_to_correct_spaces(self):
        """Pages should be added to their parent spaces."""
        tree = [
            {"id": "space-1", "type": "space", "pages": [], "children": []},
            {"id": "space-2", "type": "space", "pages": [], "children": []},
        ]

        pages = [
            MagicMock(
                id="page-1",
                title="Page 1",
                slug="page-1",
                space_id="space-1",
                status="draft",
                version="1.0",
                document_number="DOC-001",
            ),
            MagicMock(
                id="page-2",
                title="Page 2",
                slug="page-2",
                space_id="space-2",
                status="effective",
                version="2.0",
                document_number="DOC-002",
            ),
        ]

        _add_pages_to_tree(tree, pages)

        assert len(tree[0]["pages"]) == 1
        assert tree[0]["pages"][0]["id"] == "page-1"
        assert len(tree[1]["pages"]) == 1
        assert tree[1]["pages"][0]["id"] == "page-2"

    def test_add_pages_to_nested_spaces(self):
        """Pages should be added to nested spaces correctly."""
        tree = [
            {
                "id": "parent",
                "type": "space",
                "pages": [],
                "children": [
                    {"id": "child", "type": "space", "pages": [], "children": []},
                ],
            },
        ]

        pages = [
            MagicMock(
                id="page-1",
                title="Child Page",
                slug="child-page",
                space_id="child",
                status="draft",
                version="1.0",
                document_number=None,
            ),
        ]

        _add_pages_to_tree(tree, pages)

        assert len(tree[0]["pages"]) == 0
        assert len(tree[0]["children"][0]["pages"]) == 1
        assert tree[0]["children"][0]["pages"][0]["title"] == "Child Page"

    def test_page_data_structure(self):
        """Page data in tree should have correct structure."""
        tree = [{"id": "space-1", "type": "space", "pages": [], "children": []}]

        pages = [
            MagicMock(
                id="page-1",
                title="Test Page",
                slug="test-page",
                space_id="space-1",
                status="in_review",
                version="1.5",
                document_number="DOC-100",
            ),
        ]

        _add_pages_to_tree(tree, pages)

        page_data = tree[0]["pages"][0]
        assert page_data["id"] == "page-1"
        assert page_data["title"] == "Test Page"
        assert page_data["slug"] == "test-page"
        assert page_data["type"] == "page"
        assert page_data["status"] == "in_review"
        assert page_data["version"] == "1.5"
        assert page_data["document_number"] == "DOC-100"
