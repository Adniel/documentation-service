"""Metadata sync service for Git-side YAML files.

Sprint G: Metadata Portability

Writes _meta.yaml alongside content.json and _space.yaml alongside
space directories in Git repos, providing portable metadata that
travels with the content.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from src.modules.portability.schemas import PageMeta, SpaceMeta, WorkspaceMeta


class MetadataSyncService:
    """Syncs database metadata to YAML files in Git repositories."""

    def __init__(self, git_service):
        self.git_service = git_service

    # ========================================================================
    # Page metadata
    # ========================================================================

    def build_page_meta(self, page, author_email: str | None = None) -> PageMeta:
        """Build PageMeta from a Page model instance."""
        return PageMeta(
            title=page.title,
            slug=page.slug,
            document_number=page.document_number,
            revision=getattr(page, "revision", None),
            version=page.version,
            status=page.status,
            classification=page.classification,
            diataxis_types=page.diataxis_types or [],
            summary=page.summary,
            author_email=author_email,
            owner_email=None,  # Resolved at export time if needed
            custodian_email=None,
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
            tags=[],
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

    def write_page_meta(
        self,
        org_slug: str,
        workspace_slug: str,
        space_slug: str,
        page_slug: str,
        meta: PageMeta,
    ) -> None:
        """Write _meta.yaml for a page into the Git repo working directory."""
        repo_path = self.git_service._get_repo_path(org_slug)
        meta_path = repo_path / workspace_slug / space_slug / f"{page_slug}_meta.yaml"
        meta_path.parent.mkdir(parents=True, exist_ok=True)

        meta_dict = meta.model_dump(exclude_none=True)
        meta_path.write_text(
            yaml.dump(meta_dict, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )

    def read_page_meta(
        self,
        org_slug: str,
        workspace_slug: str,
        space_slug: str,
        page_slug: str,
    ) -> PageMeta | None:
        """Read _meta.yaml for a page from the Git repo working directory."""
        repo_path = self.git_service._get_repo_path(org_slug)
        meta_path = repo_path / workspace_slug / space_slug / f"{page_slug}_meta.yaml"

        if not meta_path.exists():
            return None

        data = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
        return PageMeta(**data) if data else None

    # ========================================================================
    # Space metadata
    # ========================================================================

    def build_space_meta(self, space) -> SpaceMeta:
        """Build SpaceMeta from a Space model instance."""
        return SpaceMeta(
            name=space.name,
            slug=space.slug,
            description=space.description,
            diataxis_type=space.diataxis_type,
            classification=space.classification,
            sort_order=space.sort_order,
        )

    def write_space_meta(
        self,
        org_slug: str,
        workspace_slug: str,
        space_slug: str,
        meta: SpaceMeta,
    ) -> None:
        """Write _space.yaml into the Git repo working directory."""
        repo_path = self.git_service._get_repo_path(org_slug)
        space_dir = repo_path / workspace_slug / space_slug
        space_dir.mkdir(parents=True, exist_ok=True)

        meta_path = space_dir / "_space.yaml"
        meta_dict = meta.model_dump(exclude_none=True)
        meta_path.write_text(
            yaml.dump(meta_dict, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )

    def read_space_meta(
        self,
        org_slug: str,
        workspace_slug: str,
        space_slug: str,
    ) -> SpaceMeta | None:
        """Read _space.yaml from the Git repo working directory."""
        repo_path = self.git_service._get_repo_path(org_slug)
        meta_path = repo_path / workspace_slug / space_slug / "_space.yaml"

        if not meta_path.exists():
            return None

        data = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
        return SpaceMeta(**data) if data else None

    # ========================================================================
    # Workspace metadata
    # ========================================================================

    def build_workspace_meta(self, workspace) -> WorkspaceMeta:
        """Build WorkspaceMeta from a Workspace model instance."""
        return WorkspaceMeta(
            name=workspace.name,
            slug=workspace.slug,
            description=workspace.description,
            is_public=workspace.is_public,
        )

    def write_workspace_meta(
        self,
        org_slug: str,
        workspace_slug: str,
        meta: WorkspaceMeta,
    ) -> None:
        """Write _workspace.yaml into the Git repo working directory."""
        repo_path = self.git_service._get_repo_path(org_slug)
        ws_dir = repo_path / workspace_slug
        ws_dir.mkdir(parents=True, exist_ok=True)

        meta_path = ws_dir / "_workspace.yaml"
        meta_dict = meta.model_dump(exclude_none=True)
        meta_path.write_text(
            yaml.dump(meta_dict, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )

    def read_workspace_meta(
        self,
        org_slug: str,
        workspace_slug: str,
    ) -> WorkspaceMeta | None:
        """Read _workspace.yaml from the Git repo working directory."""
        repo_path = self.git_service._get_repo_path(org_slug)
        meta_path = repo_path / workspace_slug / "_workspace.yaml"

        if not meta_path.exists():
            return None

        data = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
        return WorkspaceMeta(**data) if data else None

    # ========================================================================
    # Commit helpers
    # ========================================================================

    def commit_metadata(
        self,
        org_slug: str,
        file_paths: list[str],
        author_name: str,
        author_email: str,
        message: str = "Update metadata",
    ) -> str | None:
        """Stage and commit metadata files in the Git repo.

        Args:
            org_slug: Organization slug
            file_paths: Relative paths within the repo to stage
            author_name: Commit author name
            author_email: Commit author email
            message: Commit message

        Returns:
            Commit SHA or None if nothing to commit
        """
        import pygit2

        repo = self.git_service.get_repo(org_slug)
        if not repo:
            return None

        # Stage files
        for fp in file_paths:
            repo.index.add(fp)
        repo.index.write()

        # Check if there are actual changes
        if repo.head_is_unborn:
            return None

        status = repo.status()
        staged = {
            path
            for path, flags in status.items()
            if flags & (pygit2.GIT_STATUS_INDEX_NEW | pygit2.GIT_STATUS_INDEX_MODIFIED)
        }
        if not staged:
            return None

        sig = self.git_service._get_signature(author_name, author_email)
        tree = repo.index.write_tree()
        parent = repo.head.peel().id
        commit_id = repo.create_commit("HEAD", sig, sig, message, tree, [parent])
        return str(commit_id)

    def sync_page_metadata(
        self,
        org_slug: str,
        workspace_slug: str,
        space_slug: str,
        page_slug: str,
        page,
        author_name: str,
        author_email: str,
    ) -> str | None:
        """Write and commit page _meta.yaml in one step."""
        meta = self.build_page_meta(page, author_email=author_email)
        self.write_page_meta(org_slug, workspace_slug, space_slug, page_slug, meta)

        rel_path = f"{workspace_slug}/{space_slug}/{page_slug}_meta.yaml"
        return self.commit_metadata(
            org_slug,
            [rel_path],
            author_name,
            author_email,
            f"Sync metadata: {page.title}",
        )

    def sync_space_metadata(
        self,
        org_slug: str,
        workspace_slug: str,
        space,
        author_name: str,
        author_email: str,
    ) -> str | None:
        """Write and commit space _space.yaml in one step."""
        meta = self.build_space_meta(space)
        self.write_space_meta(org_slug, workspace_slug, space.slug, meta)

        rel_path = f"{workspace_slug}/{space.slug}/_space.yaml"
        return self.commit_metadata(
            org_slug,
            [rel_path],
            author_name,
            author_email,
            f"Sync space metadata: {space.name}",
        )
