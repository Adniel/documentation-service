"""Diff service for comparing document versions.

This service generates visual diffs between different versions
of a document, abstracting the underlying Git diff operations.

Diffs are generated in Markdown format for human readability.
"""

from difflib import unified_diff
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import ChangeRequest, Page, Space, Workspace
from src.modules.content.change_request_schemas import DiffHunk, DiffResult
from src.modules.content.git_service import get_git_service
from src.modules.content.tiptap_to_markdown import tiptap_to_markdown


def _parse_unified_diff(diff_lines: list[str]) -> tuple[list[DiffHunk], int, int]:
    """Parse unified diff output into structured hunks."""
    hunks = []
    current_hunk = None
    additions = 0
    deletions = 0

    for line in diff_lines:
        if line.startswith("@@"):
            # Parse hunk header: @@ -start,count +start,count @@
            if current_hunk:
                hunks.append(current_hunk)

            # Extract line numbers from header
            parts = line.split("@@")[1].strip().split()
            old_part = parts[0][1:]  # Remove leading -
            new_part = parts[1][1:]  # Remove leading +

            old_start, old_lines = (
                (int(old_part.split(",")[0]), int(old_part.split(",")[1]))
                if "," in old_part
                else (int(old_part), 1)
            )
            new_start, new_lines = (
                (int(new_part.split(",")[0]), int(new_part.split(",")[1]))
                if "," in new_part
                else (int(new_part), 1)
            )

            current_hunk = DiffHunk(
                old_start=old_start,
                old_lines=old_lines,
                new_start=new_start,
                new_lines=new_lines,
                content="",
            )
        elif current_hunk is not None:
            current_hunk.content += line + "\n"
            if line.startswith("+") and not line.startswith("+++"):
                additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

    if current_hunk:
        hunks.append(current_hunk)

    return hunks, additions, deletions


def _content_to_lines(file_data: dict[str, Any] | None) -> list[str]:
    """Convert document content to Markdown lines for diffing.

    Uses the TipTap to Markdown converter to generate human-readable
    diffs instead of comparing raw JSON.

    Args:
        file_data: Either a TipTap document {type: "doc", content: [...]}
                   or a Git file wrapper {title, content} where content is TipTap
    """
    if file_data is None:
        return []

    if not isinstance(file_data, dict):
        return []

    # Determine if this is a TipTap document or a Git file wrapper
    # TipTap document: {"type": "doc", "content": [...]}
    # Git file wrapper: {"title": "...", "content": {...TipTap doc...}}
    if "type" in file_data:
        # This is already a TipTap document - use it directly
        content = file_data
    elif "content" in file_data and isinstance(file_data["content"], dict):
        # This is Git wrapper format - extract the TipTap document
        content = file_data["content"]
    else:
        # Unknown format
        return []

    # Convert TipTap JSON to Markdown for readable diffs
    markdown = tiptap_to_markdown(content)
    return [line + "\n" for line in markdown.splitlines()]


async def get_page_diff(
    db: AsyncSession,
    page_id: str,
    from_sha: str,
    to_sha: str,
) -> DiffResult:
    """Generate diff between two versions of a page.

    Args:
        db: Database session
        page_id: Page ID
        from_sha: Starting commit SHA
        to_sha: Ending commit SHA

    Returns:
        DiffResult with hunks and statistics
    """
    # Get page with context
    result = await db.execute(
        select(Page)
        .options(
            selectinload(Page.space)
            .selectinload(Space.workspace)
            .selectinload(Workspace.organization)
        )
        .where(Page.id == page_id)
    )
    page = result.scalar_one_or_none()
    if not page:
        raise ValueError(f"Page not found: {page_id}")

    org_slug = page.space.workspace.organization.slug
    workspace_slug = page.space.workspace.slug
    space_slug = page.space.slug

    # Get content at both commits
    git_service = get_git_service()

    from_content = git_service.read_file(
        org_slug=org_slug,
        workspace_slug=workspace_slug,
        space_slug=space_slug,
        page_slug=page.slug,
        commit_sha=from_sha,
    )

    to_content = git_service.read_file(
        org_slug=org_slug,
        workspace_slug=workspace_slug,
        space_slug=space_slug,
        page_slug=page.slug,
        commit_sha=to_sha,
    )

    # Generate diff
    from_lines = _content_to_lines(from_content)
    to_lines = _content_to_lines(to_content)

    diff_lines = list(
        unified_diff(
            from_lines,
            to_lines,
            fromfile=f"a/{page.slug}.md",
            tofile=f"b/{page.slug}.md",
            lineterm="",
        )
    )

    hunks, additions, deletions = _parse_unified_diff(diff_lines)

    return DiffResult(
        from_sha=from_sha,
        to_sha=to_sha,
        hunks=hunks,
        additions=additions,
        deletions=deletions,
        is_binary=False,
    )


async def get_change_request_diff(
    db: AsyncSession,
    change_request_id: str,
) -> DiffResult:
    """Generate diff showing changes in a change request.

    Compares the base commit (when draft started) with the head commit
    (current state of the draft).

    Args:
        db: Database session
        change_request_id: Change request ID

    Returns:
        DiffResult with hunks and statistics
    """
    # Get change request with page
    result = await db.execute(
        select(ChangeRequest)
        .options(
            selectinload(ChangeRequest.page)
            .selectinload(Page.space)
            .selectinload(Space.workspace)
            .selectinload(Workspace.organization)
        )
        .where(ChangeRequest.id == change_request_id)
    )
    cr = result.scalar_one_or_none()
    if not cr:
        raise ValueError(f"Change request not found: {change_request_id}")

    # Use base and head commits
    from_sha = cr.base_commit_sha
    to_sha = cr.head_commit_sha or cr.base_commit_sha

    return await get_page_diff(db, cr.page_id, from_sha, to_sha)


async def get_version_content(
    db: AsyncSession,
    page_id: str,
    commit_sha: str,
) -> dict[str, Any] | None:
    """Get page content at a specific version.

    Args:
        db: Database session
        page_id: Page ID
        commit_sha: Commit SHA

    Returns:
        Document content dict or None if not found
    """
    # Get page with context
    result = await db.execute(
        select(Page)
        .options(
            selectinload(Page.space)
            .selectinload(Space.workspace)
            .selectinload(Workspace.organization)
        )
        .where(Page.id == page_id)
    )
    page = result.scalar_one_or_none()
    if not page:
        return None

    org_slug = page.space.workspace.organization.slug
    workspace_slug = page.space.workspace.slug
    space_slug = page.space.slug

    git_service = get_git_service()
    return git_service.read_file(
        org_slug=org_slug,
        workspace_slug=workspace_slug,
        space_slug=space_slug,
        page_slug=page.slug,
        commit_sha=commit_sha,
    )
