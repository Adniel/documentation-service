"""Export service for generating portable content archives.

Sprint G: Metadata Portability

Exports workspaces, spaces, and pages to ZIP archives containing
YAML metadata and JSON content, suitable for backup or migration.
"""

import io
import json
import zipfile
from datetime import datetime, timezone

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import Organization, Workspace, Space, Page
from src.modules.portability.schemas import (
    ExportManifest,
    ExportScope,
    PageMeta,
    SpaceMeta,
    WorkspaceMeta,
)
from src.modules.portability.metadata_service import MetadataSyncService


class ExportService:
    """Exports content hierarchy to portable ZIP archives."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_workspace(
        self,
        workspace_id: str,
        exporter_email: str,
        include_content: bool = True,
    ) -> tuple[io.BytesIO, str, dict[str, int]]:
        """Export a single workspace to ZIP.

        Returns:
            Tuple of (ZIP bytes buffer, filename, statistics dict)
        """
        workspace = await self._get_workspace_with_org(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace not found: {workspace_id}")

        org = workspace.organization
        spaces = await self._get_workspace_spaces(workspace_id)
        stats = {"workspaces": 1, "spaces": 0, "pages": 0}

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            base = f"export-{org.slug}"

            # Workspace metadata
            ws_meta = WorkspaceMeta(
                name=workspace.name,
                slug=workspace.slug,
                description=workspace.description,
                is_public=workspace.is_public,
            )
            zf.writestr(
                f"{base}/workspaces/{workspace.slug}/_workspace.yaml",
                yaml.dump(ws_meta.model_dump(exclude_none=True), default_flow_style=False, allow_unicode=True),
            )

            # Spaces and pages
            for space in spaces:
                stats["spaces"] += 1
                await self._write_space_to_zip(
                    zf, base, workspace.slug, space, include_content, stats
                )

            # Manifest
            manifest = ExportManifest(
                format_version="1.0",
                platform="documentation-service",
                exported_at=datetime.now(timezone.utc).isoformat(),
                exported_by=exporter_email,
                organization={"name": org.name, "slug": org.slug},
                statistics=stats,
            )
            zf.writestr(
                f"{base}/manifest.yaml",
                yaml.dump(manifest.model_dump(), default_flow_style=False, allow_unicode=True),
            )

        buf.seek(0)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d")
        filename = f"export-{org.slug}-{workspace.slug}-{ts}.zip"
        return buf, filename, stats

    async def export_space(
        self,
        space_id: str,
        exporter_email: str,
        include_content: bool = True,
    ) -> tuple[io.BytesIO, str, dict[str, int]]:
        """Export a single space to ZIP."""
        space = await self._get_space_with_workspace(space_id)
        if not space:
            raise ValueError(f"Space not found: {space_id}")

        workspace = space.workspace
        org = await self._get_org(workspace.organization_id)
        stats = {"workspaces": 0, "spaces": 1, "pages": 0}

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            base = f"export-{org.slug}"

            await self._write_space_to_zip(
                zf, base, workspace.slug, space, include_content, stats
            )

            manifest = ExportManifest(
                format_version="1.0",
                platform="documentation-service",
                exported_at=datetime.now(timezone.utc).isoformat(),
                exported_by=exporter_email,
                organization={"name": org.name, "slug": org.slug},
                statistics=stats,
            )
            zf.writestr(
                f"{base}/manifest.yaml",
                yaml.dump(manifest.model_dump(), default_flow_style=False, allow_unicode=True),
            )

        buf.seek(0)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d")
        filename = f"export-{org.slug}-{space.slug}-{ts}.zip"
        return buf, filename, stats

    async def export_organization(
        self,
        org_id: str,
        exporter_email: str,
        include_content: bool = True,
    ) -> tuple[io.BytesIO, str, dict[str, int]]:
        """Export entire organization to ZIP."""
        org = await self._get_org(org_id)
        if not org:
            raise ValueError(f"Organization not found: {org_id}")

        workspaces = await self._get_org_workspaces(org_id)
        stats = {"workspaces": 0, "spaces": 0, "pages": 0}

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            base = f"export-{org.slug}"

            for workspace in workspaces:
                stats["workspaces"] += 1

                ws_meta = WorkspaceMeta(
                    name=workspace.name,
                    slug=workspace.slug,
                    description=workspace.description,
                    is_public=workspace.is_public,
                )
                zf.writestr(
                    f"{base}/workspaces/{workspace.slug}/_workspace.yaml",
                    yaml.dump(ws_meta.model_dump(exclude_none=True), default_flow_style=False, allow_unicode=True),
                )

                spaces = await self._get_workspace_spaces(workspace.id)
                for space in spaces:
                    stats["spaces"] += 1
                    await self._write_space_to_zip(
                        zf, base, workspace.slug, space, include_content, stats
                    )

            manifest = ExportManifest(
                format_version="1.0",
                platform="documentation-service",
                exported_at=datetime.now(timezone.utc).isoformat(),
                exported_by=exporter_email,
                organization={"name": org.name, "slug": org.slug},
                statistics=stats,
            )
            zf.writestr(
                f"{base}/manifest.yaml",
                yaml.dump(manifest.model_dump(), default_flow_style=False, allow_unicode=True),
            )

        buf.seek(0)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d")
        filename = f"export-{org.slug}-{ts}.zip"
        return buf, filename, stats

    # ========================================================================
    # Internal helpers
    # ========================================================================

    async def _write_space_to_zip(
        self,
        zf: zipfile.ZipFile,
        base: str,
        workspace_slug: str,
        space: Space,
        include_content: bool,
        stats: dict[str, int],
    ) -> None:
        """Write a space and its pages to the ZIP archive."""
        space_path = f"{base}/workspaces/{workspace_slug}/spaces/{space.slug}"

        # Space metadata
        space_meta = SpaceMeta(
            name=space.name,
            slug=space.slug,
            description=space.description,
            diataxis_type=space.diataxis_type,
            classification=space.classification,
            sort_order=space.sort_order,
        )
        zf.writestr(
            f"{space_path}/_space.yaml",
            yaml.dump(space_meta.model_dump(exclude_none=True), default_flow_style=False, allow_unicode=True),
        )

        # Pages
        pages = await self._get_space_pages(space.id)
        for page in pages:
            stats["pages"] += 1
            page_path = f"{space_path}/pages/{page.slug}"

            # Page metadata
            page_meta = PageMeta(
                title=page.title,
                slug=page.slug,
                document_number=page.document_number,
                revision=getattr(page, "revision", None),
                version=page.version,
                status=page.status,
                classification=page.classification,
                diataxis_types=page.diataxis_types or [],
                summary=page.summary,
                effective_date=(
                    page.effective_date.isoformat()
                    if getattr(page, "effective_date", None)
                    else None
                ),
                next_review_date=(
                    page.next_review_date.isoformat()
                    if getattr(page, "next_review_date", None)
                    else None
                ),
                review_cycle_months=getattr(page, "review_cycle_months", None),
                requires_training=getattr(page, "requires_training", False),
                training_validity_months=getattr(page, "training_validity_months", None),
                sort_order=page.sort_order,
                is_template=page.is_template,
                created_at=(
                    page.created_at.isoformat()
                    if hasattr(page, "created_at") and page.created_at
                    else None
                ),
                updated_at=(
                    page.updated_at.isoformat()
                    if hasattr(page, "updated_at") and page.updated_at
                    else None
                ),
            )
            zf.writestr(
                f"{page_path}/_meta.yaml",
                yaml.dump(page_meta.model_dump(exclude_none=True), default_flow_style=False, allow_unicode=True),
            )

            # Content JSON
            if include_content and page.content:
                zf.writestr(
                    f"{page_path}/content.json",
                    json.dumps(page.content, indent=2, ensure_ascii=False),
                )

    async def _get_workspace_with_org(self, workspace_id: str) -> Workspace | None:
        result = await self.db.execute(
            select(Workspace)
            .where(Workspace.id == workspace_id)
            .options(selectinload(Workspace.organization))
        )
        return result.scalar_one_or_none()

    async def _get_space_with_workspace(self, space_id: str) -> Space | None:
        result = await self.db.execute(
            select(Space)
            .where(Space.id == space_id)
            .options(selectinload(Space.workspace))
        )
        return result.scalar_one_or_none()

    async def _get_org(self, org_id: str) -> Organization | None:
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def _get_org_workspaces(self, org_id: str) -> list[Workspace]:
        result = await self.db.execute(
            select(Workspace).where(
                Workspace.organization_id == org_id,
                Workspace.is_active == True,
            )
        )
        return list(result.scalars().all())

    async def _get_workspace_spaces(self, workspace_id: str) -> list[Space]:
        result = await self.db.execute(
            select(Space).where(
                Space.workspace_id == workspace_id,
                Space.is_active == True,
            ).order_by(Space.sort_order)
        )
        return list(result.scalars().all())

    async def _get_space_pages(self, space_id: str) -> list[Page]:
        result = await self.db.execute(
            select(Page).where(
                Page.space_id == space_id,
                Page.is_active == True,
            ).order_by(Page.sort_order)
        )
        return list(result.scalars().all())
