"""MCP tool implementations.

Sprint C: MCP Integration

Provides document access tools for AI agents via the MCP protocol.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import Page, Space, Workspace
from src.db.models.service_account import ServiceAccount
from src.modules.content.search_service import SearchService
from src.modules.content.tiptap_to_markdown import tiptap_to_markdown
from src.modules.mcp.schemas import (
    DocumentContent,
    DocumentResult,
    GetDocumentParams,
    ListSpacesParams,
    SearchDocumentsParams,
    SpaceInfo,
)


class McpTools:
    """MCP tool implementations.

    Provides read-only access to documentation content for AI agents.
    All operations respect the service account's permissions.
    """

    def __init__(
        self,
        db: AsyncSession,
        service_account: ServiceAccount,
    ):
        self.db = db
        self.service_account = service_account
        self.search_service = SearchService()

    def _check_space_access(self, space_id: str) -> bool:
        """Check if service account has access to a space."""
        if self.service_account.allowed_spaces is None:
            return True
        return space_id in self.service_account.allowed_spaces

    def _check_operation_allowed(self, operation: str) -> bool:
        """Check if operation is allowed for service account."""
        if self.service_account.allowed_operations is None:
            return True
        return operation in self.service_account.allowed_operations

    async def search_documents(
        self, params: SearchDocumentsParams
    ) -> list[DocumentResult]:
        """Search for documents.

        Args:
            params: Search parameters including query and optional filters

        Returns:
            List of matching documents with excerpts
        """
        if not self._check_operation_allowed("search_documents"):
            raise PermissionError("Operation 'search_documents' not allowed")

        # Build filters
        filters = [f"organization_id = {self.service_account.organization_id}"]

        # Filter by allowed spaces
        if params.space_id:
            if not self._check_space_access(params.space_id):
                raise PermissionError("Access to space denied")
            filters.append(f"space_id = {params.space_id}")
        elif self.service_account.allowed_spaces:
            space_filter = " OR ".join(
                f"space_id = {s}" for s in self.service_account.allowed_spaces
            )
            filters.append(f"({space_filter})")

        # Only return effective documents by default
        filters.append("status = effective")

        try:
            # Search using Meilisearch
            index = self.search_service.client.index(SearchService.PAGES_INDEX)
            results = index.search(
                params.query,
                {
                    "filter": " AND ".join(filters),
                    "limit": params.limit,
                    "attributesToRetrieve": [
                        "id",
                        "title",
                        "space_id",
                        "space_name",
                        "status",
                        "updated_at",
                    ],
                    "attributesToCrop": ["content_text"],
                    "cropLength": 200,
                },
            )

            return [
                DocumentResult(
                    id=hit["id"],
                    title=hit["title"],
                    space_id=hit["space_id"],
                    space_name=hit.get("space_name", ""),
                    excerpt=hit.get("_formatted", {}).get("content_text"),
                    score=hit.get("_score"),
                    status=hit["status"],
                    updated_at=datetime.fromisoformat(hit["updated_at"]),
                )
                for hit in results["hits"]
            ]
        except Exception:
            # Fallback to database search if Meilisearch is unavailable
            return await self._search_fallback(params)

    async def _search_fallback(
        self, params: SearchDocumentsParams
    ) -> list[DocumentResult]:
        """Fallback search using database when Meilisearch is unavailable."""
        query = (
            select(Page)
            .options(selectinload(Page.space))
            .where(Page.title.ilike(f"%{params.query}%"))
            .limit(params.limit)
        )

        # Filter by organization via space
        query = query.join(Space).join(Workspace).where(
            Workspace.organization_id == self.service_account.organization_id
        )

        if params.space_id:
            query = query.where(Page.space_id == params.space_id)
        elif self.service_account.allowed_spaces:
            query = query.where(Page.space_id.in_(self.service_account.allowed_spaces))

        result = await self.db.execute(query)
        pages = result.scalars().all()

        return [
            DocumentResult(
                id=str(page.id),
                title=page.title,
                space_id=str(page.space_id),
                space_name=page.space.name if page.space else "",
                excerpt=None,
                score=None,
                status=page.status,
                updated_at=page.updated_at,
            )
            for page in pages
        ]

    async def get_document(self, params: GetDocumentParams) -> DocumentContent:
        """Get a document by ID with full content.

        Args:
            params: Parameters containing document_id

        Returns:
            Document with full content in markdown format
        """
        if not self._check_operation_allowed("get_document"):
            raise PermissionError("Operation 'get_document' not allowed")

        # Fetch page with space
        result = await self.db.execute(
            select(Page)
            .options(selectinload(Page.space))
            .where(Page.id == params.document_id)
        )
        page = result.scalar_one_or_none()

        if not page:
            raise ValueError("Document not found")

        if not self._check_space_access(str(page.space_id)):
            raise PermissionError("Access to document denied")

        # Convert TipTap content to markdown
        content_md = ""
        if page.content:
            try:
                content_md = tiptap_to_markdown(page.content)
            except Exception:
                content_md = "[Content conversion error]"

        return DocumentContent(
            id=str(page.id),
            title=page.title,
            content_markdown=content_md,
            content_html=None,
            metadata={
                "document_number": page.document_number,
                "version": page.version,
                "revision": page.revision,
                "owner_id": page.owner_id,
                "classification": page.classification,
                "space_id": str(page.space_id),
                "space_name": page.space.name if page.space else None,
            },
            version=page.version or "1.0",
            status=page.status,
            updated_at=page.updated_at,
        )

    async def get_document_content(self, params: GetDocumentParams) -> str:
        """Get document content as markdown.

        Args:
            params: Parameters containing document_id

        Returns:
            Document content in markdown format
        """
        doc = await self.get_document(params)
        return doc.content_markdown

    async def list_spaces(self, params: ListSpacesParams) -> list[SpaceInfo]:
        """List accessible spaces.

        Args:
            params: Optional workspace filter

        Returns:
            List of accessible spaces with metadata
        """
        if not self._check_operation_allowed("list_spaces"):
            raise PermissionError("Operation 'list_spaces' not allowed")

        query = (
            select(Space)
            .options(selectinload(Space.workspace))
            .join(Workspace)
            .where(Workspace.organization_id == self.service_account.organization_id)
        )

        if params.workspace_id:
            query = query.where(Space.workspace_id == params.workspace_id)

        result = await self.db.execute(query)
        spaces = result.scalars().all()

        # Filter by allowed spaces
        if self.service_account.allowed_spaces:
            allowed = set(self.service_account.allowed_spaces)
            spaces = [s for s in spaces if str(s.id) in allowed]

        # Get page counts
        space_infos = []
        for space in spaces:
            # Count pages in space
            page_count_result = await self.db.execute(
                select(Page.id).where(Page.space_id == space.id)
            )
            page_count = len(list(page_count_result.scalars().all()))

            space_infos.append(
                SpaceInfo(
                    id=str(space.id),
                    name=space.name,
                    description=space.description,
                    workspace_id=str(space.workspace_id),
                    workspace_name=space.workspace.name if space.workspace else "",
                    page_count=page_count,
                )
            )

        return space_infos

    async def get_document_metadata(self, params: GetDocumentParams) -> dict[str, Any]:
        """Get document metadata.

        Args:
            params: Parameters containing document_id

        Returns:
            Document metadata (status, version, dates, etc.)
        """
        if not self._check_operation_allowed("get_document_metadata"):
            raise PermissionError("Operation 'get_document_metadata' not allowed")

        result = await self.db.execute(
            select(Page).where(Page.id == params.document_id)
        )
        page = result.scalar_one_or_none()

        if not page:
            raise ValueError("Document not found")

        if not self._check_space_access(str(page.space_id)):
            raise PermissionError("Access to document denied")

        return {
            "id": str(page.id),
            "title": page.title,
            "document_number": page.document_number,
            "version": page.version,
            "revision": page.revision,
            "status": page.status,
            "classification": page.classification,
            "owner_id": page.owner_id,
            "effective_date": (
                page.effective_date.isoformat() if page.effective_date else None
            ),
            "next_review_date": (
                page.next_review_date.isoformat() if page.next_review_date else None
            ),
            "created_at": page.created_at.isoformat(),
            "updated_at": page.updated_at.isoformat(),
        }

    async def get_document_history(self, params: GetDocumentParams) -> list[dict]:
        """Get document version history.

        Args:
            params: Parameters containing document_id

        Returns:
            List of version history entries

        Note:
            This is a simplified implementation. Full history would require
            Git commit traversal which depends on the repository structure.
        """
        if not self._check_operation_allowed("get_document_history"):
            raise PermissionError("Operation 'get_document_history' not allowed")

        result = await self.db.execute(
            select(Page).where(Page.id == params.document_id)
        )
        page = result.scalar_one_or_none()

        if not page:
            raise ValueError("Document not found")

        if not self._check_space_access(str(page.space_id)):
            raise PermissionError("Access to document denied")

        # Return simplified history from page metadata
        # Full Git history would require additional implementation
        return [
            {
                "version": page.version or "1.0",
                "revision": page.revision or "A",
                "status": page.status,
                "updated_at": page.updated_at.isoformat(),
                "created_at": page.created_at.isoformat(),
            }
        ]
