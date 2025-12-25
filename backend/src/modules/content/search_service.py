"""
Meilisearch Integration Service

Provides full-text search capabilities for documentation content.
"""

import asyncio
from typing import Any

import meilisearch
from meilisearch.errors import MeilisearchApiError

from src.config import get_settings

settings = get_settings()


class SearchService:
    """Service for managing Meilisearch indexing and search operations."""

    # Index names
    PAGES_INDEX = "pages"
    SPACES_INDEX = "spaces"

    def __init__(self):
        """Initialize the Meilisearch client."""
        self.client = meilisearch.Client(
            settings.meilisearch_url,
            settings.meilisearch_api_key,
        )
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize indexes with proper settings."""
        if self._initialized:
            return

        # Run sync operations in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._setup_indexes)
        self._initialized = True

    def _setup_indexes(self) -> None:
        """Set up Meilisearch indexes with searchable attributes and filters."""
        # Pages index
        try:
            self.client.create_index(self.PAGES_INDEX, {"primaryKey": "id"})
        except MeilisearchApiError:
            pass  # Index already exists

        pages_index = self.client.index(self.PAGES_INDEX)
        pages_index.update_settings({
            "searchableAttributes": [
                "title",
                "content_text",
                "summary",
                "document_number",
            ],
            "filterableAttributes": [
                "space_id",
                "workspace_id",
                "organization_id",
                "status",
                "classification",
                "diataxis_type",
                "author_id",
            ],
            "sortableAttributes": [
                "updated_at",
                "created_at",
                "title",
            ],
            "rankingRules": [
                "words",
                "typo",
                "proximity",
                "attribute",
                "sort",
                "exactness",
            ],
            "typoTolerance": {
                "enabled": True,
                "minWordSizeForTypos": {
                    "oneTypo": 4,
                    "twoTypos": 8,
                },
            },
        })

        # Spaces index
        try:
            self.client.create_index(self.SPACES_INDEX, {"primaryKey": "id"})
        except MeilisearchApiError:
            pass

        spaces_index = self.client.index(self.SPACES_INDEX)
        spaces_index.update_settings({
            "searchableAttributes": [
                "name",
                "description",
            ],
            "filterableAttributes": [
                "workspace_id",
                "organization_id",
                "diataxis_type",
                "classification",
            ],
            "sortableAttributes": [
                "name",
                "updated_at",
            ],
        })

    async def index_page(self, page_data: dict[str, Any]) -> None:
        """Index a page document.

        Args:
            page_data: Page data including:
                - id, title, content_text, summary
                - space_id, workspace_id, organization_id
                - status, classification, diataxis_type
                - author_id, created_at, updated_at
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.index(self.PAGES_INDEX).add_documents([page_data]),
        )

    async def index_pages_batch(self, pages: list[dict[str, Any]]) -> None:
        """Index multiple pages in a batch."""
        if not pages:
            return

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.index(self.PAGES_INDEX).add_documents(pages),
        )

    async def delete_page(self, page_id: str) -> None:
        """Remove a page from the search index."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.index(self.PAGES_INDEX).delete_document(page_id),
        )

    async def index_space(self, space_data: dict[str, Any]) -> None:
        """Index a space."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.index(self.SPACES_INDEX).add_documents([space_data]),
        )

    async def search_pages(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        limit: int = 20,
        offset: int = 0,
        sort: list[str] | None = None,
    ) -> dict[str, Any]:
        """Search for pages.

        Args:
            query: Search query string
            filters: Optional filters (space_id, status, classification, etc.)
            limit: Maximum results to return
            offset: Pagination offset
            sort: Sort order (e.g., ["updated_at:desc"])

        Returns:
            Search results with hits, total count, and processing time
        """
        search_params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "attributesToRetrieve": [
                "id",
                "title",
                "summary",
                "status",
                "version",
                "document_number",
                "space_id",
                "diataxis_type",
                "updated_at",
            ],
            "attributesToHighlight": ["title", "content_text", "summary"],
            "highlightPreTag": "<mark>",
            "highlightPostTag": "</mark>",
        }

        if filters:
            filter_parts = []
            for key, value in filters.items():
                if value is not None:
                    if isinstance(value, list):
                        # OR filter for multiple values
                        or_parts = [f'{key} = "{v}"' for v in value]
                        filter_parts.append(f"({' OR '.join(or_parts)})")
                    else:
                        filter_parts.append(f'{key} = "{value}"')
            if filter_parts:
                search_params["filter"] = " AND ".join(filter_parts)

        if sort:
            search_params["sort"] = sort

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.client.index(self.PAGES_INDEX).search(query, search_params),
        )

        return {
            "hits": results["hits"],
            "total": results["estimatedTotalHits"],
            "processing_time_ms": results["processingTimeMs"],
            "query": query,
            "limit": limit,
            "offset": offset,
        }

    async def search_spaces(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search for spaces."""
        search_params: dict[str, Any] = {
            "limit": limit,
            "attributesToRetrieve": [
                "id",
                "name",
                "description",
                "diataxis_type",
                "workspace_id",
            ],
        }

        if filters:
            filter_parts = []
            for key, value in filters.items():
                if value is not None:
                    filter_parts.append(f'{key} = "{value}"')
            if filter_parts:
                search_params["filter"] = " AND ".join(filter_parts)

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self.client.index(self.SPACES_INDEX).search(query, search_params),
        )

        return {
            "hits": results["hits"],
            "total": results["estimatedTotalHits"],
        }

    async def get_suggestions(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict[str, str]]:
        """Get search suggestions/autocomplete results.

        Returns a mix of page titles and space names.
        """
        if not query or len(query) < 2:
            return []

        # Search both indexes concurrently
        pages_task = self.search_pages(query, limit=limit)
        spaces_task = self.search_spaces(query, limit=3)

        pages_results, spaces_results = await asyncio.gather(
            pages_task, spaces_task
        )

        suggestions = []

        # Add space suggestions
        for space in spaces_results["hits"]:
            suggestions.append({
                "type": "space",
                "id": space["id"],
                "title": space["name"],
                "description": space.get("description", ""),
            })

        # Add page suggestions
        for page in pages_results["hits"]:
            suggestions.append({
                "type": "page",
                "id": page["id"],
                "title": page["title"],
                "description": page.get("summary", ""),
            })

        return suggestions[:limit]


# Singleton instance
_search_service: SearchService | None = None


def get_search_service() -> SearchService:
    """Get the search service singleton."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
