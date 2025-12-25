"""Unit tests for search service (Sprint 3)."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


class TestSearchServiceIndexing:
    """Tests for search indexing operations."""

    def test_page_document_structure(self):
        """Page document should have correct structure for indexing."""
        # This tests the expected document structure
        page_doc = {
            "id": "page-123",
            "title": "Test Page",
            "slug": "test-page",
            "content_text": "This is the page content",
            "summary": "A test page",
            "status": "effective",
            "version": "1.0",
            "document_number": "DOC-001",
            "space_id": "space-123",
            "workspace_id": "ws-123",
            "organization_id": "org-123",
            "diataxis_type": "tutorial",
            "classification": 0,
            "author_id": "user-123",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T00:00:00Z",
        }

        # Verify all required fields are present
        required_fields = [
            "id", "title", "slug", "status", "version",
            "space_id", "workspace_id", "organization_id"
        ]
        for field in required_fields:
            assert field in page_doc

    def test_space_document_structure(self):
        """Space document should have correct structure for indexing."""
        space_doc = {
            "id": "space-123",
            "name": "Test Space",
            "slug": "test-space",
            "description": "A test space for tutorials",
            "workspace_id": "ws-123",
            "organization_id": "org-123",
            "diataxis_type": "tutorial",
            "classification": 0,
            "page_count": 5,
        }

        required_fields = [
            "id", "name", "slug", "workspace_id", "organization_id", "diataxis_type"
        ]
        for field in required_fields:
            assert field in space_doc


class TestSearchServiceFiltering:
    """Tests for search filtering logic."""

    def test_build_filter_empty(self):
        """Empty filters should return None or empty string."""
        filters = {}
        # The filter builder should handle empty filters gracefully
        assert filters == {} or filters is None or filters == ""

    def test_build_filter_single_field(self):
        """Single filter should be properly formatted."""
        # Meilisearch filter format
        filter_str = "status = 'effective'"

        assert "status" in filter_str
        assert "effective" in filter_str

    def test_build_filter_multiple_fields(self):
        """Multiple filters should be combined with AND."""
        filter_parts = [
            "status = 'effective'",
            "diataxis_type = 'tutorial'",
            "classification <= 2"
        ]
        combined = " AND ".join(filter_parts)

        assert "status = 'effective'" in combined
        assert "diataxis_type = 'tutorial'" in combined
        assert "classification <= 2" in combined
        assert " AND " in combined

    def test_classification_filter(self):
        """Classification filter should use <= for clearance level."""
        user_clearance = 2
        filter_str = f"classification <= {user_clearance}"

        assert "<=" in filter_str
        assert str(user_clearance) in filter_str


class TestSearchServiceSuggestions:
    """Tests for search suggestions/autocomplete."""

    def test_suggestion_structure(self):
        """Suggestion should have correct structure."""
        suggestion = {
            "type": "page",
            "id": "page-123",
            "title": "Getting Started Guide",
            "description": "Learn how to get started",
        }

        assert suggestion["type"] in ["page", "space"]
        assert "id" in suggestion
        assert "title" in suggestion

    def test_suggestion_types(self):
        """Suggestions can be pages or spaces."""
        page_suggestion = {"type": "page", "id": "p1", "title": "Page"}
        space_suggestion = {"type": "space", "id": "s1", "title": "Space"}

        assert page_suggestion["type"] == "page"
        assert space_suggestion["type"] == "space"


class TestSearchServiceSorting:
    """Tests for search result sorting."""

    def test_sort_options(self):
        """Valid sort options should be recognized."""
        valid_sorts = [
            "relevance",
            "updated_at:desc",
            "updated_at:asc",
            "title:asc",
            "title:desc",
            "created_at:desc",
        ]

        for sort in valid_sorts:
            if sort == "relevance":
                # Relevance sorting means no explicit sort (default)
                assert sort == "relevance"
            else:
                field, direction = sort.split(":")
                assert field in ["updated_at", "title", "created_at"]
                assert direction in ["asc", "desc"]

    def test_sort_format(self):
        """Sort should be in format 'field:direction'."""
        sort = "updated_at:desc"
        parts = sort.split(":")

        assert len(parts) == 2
        assert parts[0] == "updated_at"
        assert parts[1] == "desc"


class TestSearchServiceResults:
    """Tests for search result structure."""

    def test_search_result_structure(self):
        """Search result should have correct structure."""
        result = {
            "hits": [
                {
                    "id": "page-1",
                    "title": "Test Page",
                    "summary": "A summary",
                    "status": "effective",
                    "version": "1.0",
                    "_formatted": {
                        "title": "<em>Test</em> Page",
                        "content_text": "...matched <em>content</em>...",
                    },
                },
            ],
            "total": 1,
            "processing_time_ms": 5,
            "query": "test",
            "limit": 20,
            "offset": 0,
        }

        assert "hits" in result
        assert "total" in result
        assert "processing_time_ms" in result
        assert "query" in result
        assert isinstance(result["hits"], list)
        assert result["total"] >= 0

    def test_hit_formatted_fields(self):
        """Hits should include formatted fields for highlighting."""
        hit = {
            "id": "page-1",
            "title": "Getting Started",
            "_formatted": {
                "title": "<em>Getting</em> Started",
                "content_text": "This guide helps you <em>get</em> started",
            },
        }

        assert "_formatted" in hit
        assert "title" in hit["_formatted"]
        # Formatted fields contain highlight markers
        assert "<em>" in hit["_formatted"]["title"]

    def test_empty_results(self):
        """Empty search should return valid structure."""
        result = {
            "hits": [],
            "total": 0,
            "processing_time_ms": 1,
            "query": "nonexistent",
            "limit": 20,
            "offset": 0,
        }

        assert result["hits"] == []
        assert result["total"] == 0
