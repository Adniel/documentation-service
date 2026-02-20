"""Import service for ingesting content from external sources.

Sprint G: Metadata Portability

Orchestrates import from various formats (docservice ZIP, Markdown folders,
Confluence exports) with preview, conflict detection, and execution.
"""

import io
import json
import zipfile
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Page, Space
from src.modules.portability.schemas import (
    ConflictAction,
    ImportConflictResolution,
    ImportExecuteRequest,
    ImportFormat,
    ImportItem,
    ImportItemStatus,
    ImportPreviewResponse,
    ImportResult,
    ImportResultItem,
    PageMeta,
    SpaceMeta,
    WorkspaceMeta,
)
from src.modules.portability.markdown_adapter import MarkdownAdapter
from src.modules.portability.confluence_adapter import ConfluenceAdapter


class ImportService:
    """Orchestrates content import from various formats."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================================================================
    # Format detection
    # ========================================================================

    def detect_format(self, extract_path: Path) -> ImportFormat:
        """Detect the import format from extracted content.

        Args:
            extract_path: Path to extracted import content

        Returns:
            Detected ImportFormat
        """
        # Check for docservice manifest
        for item in extract_path.iterdir():
            if item.is_dir():
                manifest = item / "manifest.yaml"
                if manifest.exists():
                    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
                    if data and data.get("platform") == "documentation-service":
                        return ImportFormat.DOCSERVICE

        # Check for Confluence export markers
        html_files = list(extract_path.rglob("*.html"))
        if html_files:
            # Look for Confluence patterns
            for hf in html_files[:3]:
                content = hf.read_text(encoding="utf-8", errors="replace")
                if "confluence" in content.lower() or "atlassian" in content.lower():
                    return ImportFormat.CONFLUENCE
            # If there are HTML files but no Confluence markers, still treat as Confluence
            if len(html_files) > 0 and not list(extract_path.rglob("*.md")):
                return ImportFormat.CONFLUENCE

        # Check for Markdown files
        if list(extract_path.rglob("*.md")):
            return ImportFormat.MARKDOWN

        # Default to Markdown
        return ImportFormat.MARKDOWN

    # ========================================================================
    # Preview
    # ========================================================================

    async def preview(
        self,
        extract_path: Path,
        target_workspace_id: str,
        target_space_id: str | None = None,
    ) -> ImportPreviewResponse:
        """Preview what an import would do without making changes.

        Args:
            extract_path: Path to extracted import content
            target_workspace_id: Workspace to import into
            target_space_id: Optional space to import into

        Returns:
            ImportPreviewResponse with items and statistics
        """
        fmt = self.detect_format(extract_path)
        items: list[ImportItem] = []
        warnings: list[str] = []

        if fmt == ImportFormat.DOCSERVICE:
            items = await self._preview_docservice(extract_path, target_space_id)
        elif fmt == ImportFormat.CONFLUENCE:
            adapter = ConfluenceAdapter()
            items = adapter.parse_export(extract_path)
        elif fmt == ImportFormat.MARKDOWN:
            adapter = MarkdownAdapter()
            items = adapter.parse_folder(extract_path)

        # Check for conflicts against existing content
        if target_space_id:
            items = await self._check_conflicts(items, target_space_id)

        # Calculate statistics
        stats = {
            "create": sum(1 for i in items if i.status == ImportItemStatus.CREATE),
            "update": sum(1 for i in items if i.status == ImportItemStatus.UPDATE),
            "conflict": sum(1 for i in items if i.status == ImportItemStatus.CONFLICT),
            "skip": sum(1 for i in items if i.status == ImportItemStatus.SKIP),
            "total": len(items),
        }

        return ImportPreviewResponse(
            format_detected=fmt,
            items=items,
            statistics=stats,
            warnings=warnings,
        )

    async def _preview_docservice(
        self, extract_path: Path, target_space_id: str | None
    ) -> list[ImportItem]:
        """Preview a docservice-format export."""
        items: list[ImportItem] = []

        # Find the export root (contains manifest.yaml)
        export_root = None
        for item in extract_path.iterdir():
            if item.is_dir() and (item / "manifest.yaml").exists():
                export_root = item
                break

        if not export_root:
            return items

        workspaces_dir = export_root / "workspaces"
        if not workspaces_dir.exists():
            return items

        for ws_dir in sorted(workspaces_dir.iterdir()):
            if not ws_dir.is_dir():
                continue

            spaces_dir = ws_dir / "spaces"
            if not spaces_dir.exists():
                continue

            for space_dir in sorted(spaces_dir.iterdir()):
                if not space_dir.is_dir():
                    continue

                # Space item
                space_meta_path = space_dir / "_space.yaml"
                if space_meta_path.exists():
                    space_data = yaml.safe_load(space_meta_path.read_text(encoding="utf-8"))
                    items.append(ImportItem(
                        path=str(space_dir.relative_to(extract_path)),
                        item_type="space",
                        title=space_data.get("name", space_dir.name),
                        slug=space_data.get("slug", space_dir.name),
                        status=ImportItemStatus.CREATE,
                    ))

                pages_dir = space_dir / "pages"
                if not pages_dir.exists():
                    continue

                for page_dir in sorted(pages_dir.iterdir()):
                    if not page_dir.is_dir():
                        continue

                    meta_path = page_dir / "_meta.yaml"
                    if meta_path.exists():
                        meta_data = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
                        items.append(ImportItem(
                            path=str(page_dir.relative_to(extract_path)),
                            item_type="page",
                            title=meta_data.get("title", page_dir.name),
                            slug=meta_data.get("slug", page_dir.name),
                            status=ImportItemStatus.CREATE,
                        ))

        return items

    async def _check_conflicts(
        self, items: list[ImportItem], space_id: str
    ) -> list[ImportItem]:
        """Check import items against existing pages in the target space."""
        result = await self.db.execute(
            select(Page.slug, Page.id).where(
                Page.space_id == space_id,
                Page.is_active == True,
            )
        )
        existing_slugs = {row[0]: str(row[1]) for row in result.all()}

        updated = []
        for item in items:
            if item.item_type == "page" and item.slug in existing_slugs:
                item = item.model_copy(update={
                    "status": ImportItemStatus.CONFLICT,
                    "conflict_reason": f"Page with slug '{item.slug}' already exists",
                    "existing_id": existing_slugs[item.slug],
                })
            updated.append(item)

        return updated

    # ========================================================================
    # Execute
    # ========================================================================

    async def execute(
        self,
        extract_path: Path,
        request: ImportExecuteRequest,
        author_id: str,
    ) -> ImportResult:
        """Execute an import after preview.

        Args:
            extract_path: Path to extracted import content
            request: Import execution parameters
            author_id: ID of user performing the import

        Returns:
            ImportResult with outcome for each item
        """
        fmt = self.detect_format(extract_path)
        result_items: list[ImportResultItem] = []

        # Build conflict resolution map
        resolution_map = {r.path: r.action for r in request.resolutions}

        if fmt == ImportFormat.DOCSERVICE:
            result_items = await self._execute_docservice(
                extract_path, request, author_id, resolution_map
            )
        elif fmt == ImportFormat.CONFLUENCE:
            result_items = await self._execute_confluence(
                extract_path, request, author_id, resolution_map
            )
        elif fmt == ImportFormat.MARKDOWN:
            result_items = await self._execute_markdown(
                extract_path, request, author_id, resolution_map
            )

        await self.db.commit()

        return ImportResult(
            total=len(result_items),
            created=sum(1 for r in result_items if r.status == "created"),
            updated=sum(1 for r in result_items if r.status == "updated"),
            skipped=sum(1 for r in result_items if r.status == "skipped"),
            errors=sum(1 for r in result_items if r.status == "error"),
            items=result_items,
        )

    async def _execute_docservice(
        self,
        extract_path: Path,
        request: ImportExecuteRequest,
        author_id: str,
        resolution_map: dict[str, ConflictAction],
    ) -> list[ImportResultItem]:
        """Execute import from docservice format."""
        results: list[ImportResultItem] = []

        export_root = None
        for item in extract_path.iterdir():
            if item.is_dir() and (item / "manifest.yaml").exists():
                export_root = item
                break
        if not export_root:
            return results

        target_space_id = request.target_space_id
        if not target_space_id:
            # Create spaces from export
            target_space_id = await self._ensure_default_space(request.target_workspace_id)

        workspaces_dir = export_root / "workspaces"
        if not workspaces_dir.exists():
            return results

        for ws_dir in sorted(workspaces_dir.iterdir()):
            if not ws_dir.is_dir():
                continue

            spaces_dir = ws_dir / "spaces"
            if not spaces_dir.exists():
                continue

            for space_dir in sorted(spaces_dir.iterdir()):
                if not space_dir.is_dir():
                    continue

                pages_dir = space_dir / "pages"
                if not pages_dir.exists():
                    continue

                for page_dir in sorted(pages_dir.iterdir()):
                    if not page_dir.is_dir():
                        continue

                    rel_path = str(page_dir.relative_to(extract_path))
                    result = await self._import_docservice_page(
                        page_dir, target_space_id, author_id,
                        rel_path, resolution_map, request.default_conflict_action,
                    )
                    results.append(result)

        return results

    async def _import_docservice_page(
        self,
        page_dir: Path,
        space_id: str,
        author_id: str,
        rel_path: str,
        resolution_map: dict[str, ConflictAction],
        default_action: ConflictAction,
    ) -> ImportResultItem:
        """Import a single page from docservice format."""
        meta_path = page_dir / "_meta.yaml"
        content_path = page_dir / "content.json"

        if not meta_path.exists():
            return ImportResultItem(
                path=rel_path, item_type="page", title=page_dir.name,
                status="error", error="Missing _meta.yaml",
            )

        meta_data = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
        meta = PageMeta(**meta_data)
        content = None
        if content_path.exists():
            content = json.loads(content_path.read_text(encoding="utf-8"))

        return await self._create_or_update_page(
            meta, content, space_id, author_id, rel_path,
            resolution_map, default_action,
        )

    async def _execute_markdown(
        self,
        extract_path: Path,
        request: ImportExecuteRequest,
        author_id: str,
        resolution_map: dict[str, ConflictAction],
    ) -> list[ImportResultItem]:
        """Execute import from Markdown folder."""
        results: list[ImportResultItem] = []
        adapter = MarkdownAdapter()

        target_space_id = request.target_space_id
        if not target_space_id:
            target_space_id = await self._ensure_default_space(request.target_workspace_id)

        for md_file in sorted(extract_path.rglob("*.md")):
            if md_file.name.startswith("_"):
                continue

            rel_path = str(md_file.relative_to(extract_path))
            content, meta = adapter.read_page(md_file)
            result = await self._create_or_update_page(
                meta, content, target_space_id, author_id, rel_path,
                resolution_map, request.default_conflict_action,
            )
            results.append(result)

        return results

    async def _execute_confluence(
        self,
        extract_path: Path,
        request: ImportExecuteRequest,
        author_id: str,
        resolution_map: dict[str, ConflictAction],
    ) -> list[ImportResultItem]:
        """Execute import from Confluence HTML export."""
        results: list[ImportResultItem] = []
        adapter = ConfluenceAdapter()

        target_space_id = request.target_space_id
        if not target_space_id:
            target_space_id = await self._ensure_default_space(request.target_workspace_id)

        for html_file in sorted(extract_path.rglob("*.html")):
            if html_file.name.startswith("index"):
                continue

            rel_path = str(html_file.relative_to(extract_path))
            content, meta = adapter.read_page(html_file)
            result = await self._create_or_update_page(
                meta, content, target_space_id, author_id, rel_path,
                resolution_map, request.default_conflict_action,
            )
            results.append(result)

        return results

    # ========================================================================
    # Shared helpers
    # ========================================================================

    async def _create_or_update_page(
        self,
        meta: PageMeta,
        content: dict | None,
        space_id: str,
        author_id: str,
        rel_path: str,
        resolution_map: dict[str, ConflictAction],
        default_action: ConflictAction,
    ) -> ImportResultItem:
        """Create or update a page based on conflict resolution."""
        # Check for existing page with same slug
        result = await self.db.execute(
            select(Page).where(
                Page.space_id == space_id,
                Page.slug == meta.slug,
                Page.is_active == True,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            action = resolution_map.get(rel_path, default_action)
            if action == ConflictAction.SKIP:
                return ImportResultItem(
                    path=rel_path, item_type="page", title=meta.title,
                    status="skipped", resource_id=str(existing.id),
                )
            elif action == ConflictAction.OVERWRITE:
                existing.title = meta.title
                existing.content = content
                existing.summary = meta.summary
                existing.classification = meta.classification
                existing.diataxis_types = meta.diataxis_types
                existing.status = meta.status
                await self.db.flush()
                return ImportResultItem(
                    path=rel_path, item_type="page", title=meta.title,
                    status="updated", resource_id=str(existing.id),
                )
            elif action == ConflictAction.RENAME:
                # Append suffix to slug
                meta = meta.model_copy(update={
                    "slug": f"{meta.slug}-imported",
                    "title": f"{meta.title} (Imported)",
                })

        # Create new page
        try:
            page = Page(
                title=meta.title,
                slug=meta.slug,
                space_id=space_id,
                author_id=author_id,
                content=content,
                summary=meta.summary,
                classification=meta.classification,
                diataxis_types=meta.diataxis_types,
                status=meta.status,
                version=meta.version,
                sort_order=meta.sort_order,
                is_template=meta.is_template,
                requires_training=meta.requires_training,
            )
            if meta.document_number:
                page.document_number = meta.document_number
            if meta.review_cycle_months:
                page.review_cycle_months = meta.review_cycle_months

            self.db.add(page)
            await self.db.flush()
            return ImportResultItem(
                path=rel_path, item_type="page", title=meta.title,
                status="created", resource_id=str(page.id),
            )
        except Exception as e:
            return ImportResultItem(
                path=rel_path, item_type="page", title=meta.title,
                status="error", error=str(e),
            )

    async def _ensure_default_space(self, workspace_id: str) -> str:
        """Get or create a default 'imported' space in the workspace."""
        result = await self.db.execute(
            select(Space).where(
                Space.workspace_id == workspace_id,
                Space.slug == "imported",
                Space.is_active == True,
            )
        )
        space = result.scalar_one_or_none()
        if space:
            return str(space.id)

        space = Space(
            name="Imported Content",
            slug="imported",
            workspace_id=workspace_id,
            diataxis_type="mixed",
            classification=0,
        )
        self.db.add(space)
        await self.db.flush()
        return str(space.id)
