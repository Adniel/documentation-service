"""Change Request service for version control workflow.

This service manages the lifecycle of change requests (drafts),
abstracting Git operations into user-friendly concepts.
"""

import re
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import ChangeRequest, ChangeRequestComment, Page, User, Space, Workspace
from src.db.models.change_request import ChangeRequestStatus
from src.db.models.page import PageStatus
from src.modules.content.change_request_schemas import (
    ChangeRequestCreate,
    ChangeRequestUpdate,
    CommentCreate,
)
from src.modules.content.git_service import get_git_service


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:50]  # Limit length


async def _get_next_cr_number(db: AsyncSession, page_id: str) -> int:
    """Get the next change request number for a page."""
    result = await db.execute(
        select(func.coalesce(func.max(ChangeRequest.number), 0)).where(
            ChangeRequest.page_id == page_id
        )
    )
    return result.scalar() + 1


async def _get_page_with_context(db: AsyncSession, page_id: str) -> Page | None:
    """Get a page with its space and workspace loaded."""
    result = await db.execute(
        select(Page)
        .options(
            selectinload(Page.space)
            .selectinload(Space.workspace)
            .selectinload(Workspace.organization)
        )
        .where(Page.id == page_id)
    )
    return result.scalar_one_or_none()


async def create_change_request(
    db: AsyncSession,
    page_id: str,
    author: User,
    cr_in: ChangeRequestCreate,
) -> ChangeRequest:
    """Create a new change request (draft) for a page.

    This creates a Git branch and a database record to track the draft.
    """
    # Get page with context for Git paths
    page = await _get_page_with_context(db, page_id)
    if not page:
        raise ValueError(f"Page not found: {page_id}")

    # Get organization slug for Git operations
    org_slug = page.space.workspace.organization.slug

    # Get next CR number
    cr_number = await _get_next_cr_number(db, page_id)

    # Generate branch name
    title_slug = _slugify(cr_in.title)
    branch_name = f"draft/CR-{cr_number:04d}-{title_slug}"

    # Get current commit SHA
    base_commit_sha = page.git_commit_sha
    if not base_commit_sha:
        raise ValueError("Page has no Git commit - cannot create draft")

    # Create Git branch
    git_service = get_git_service()
    success = git_service.create_branch(org_slug, branch_name, base_commit_sha)
    if not success:
        raise RuntimeError(f"Failed to create Git branch: {branch_name}")

    # Create database record
    change_request = ChangeRequest(
        page_id=page_id,
        title=cr_in.title,
        description=cr_in.description,
        number=cr_number,
        author_id=author.id,
        branch_name=branch_name,
        base_commit_sha=base_commit_sha,
        head_commit_sha=base_commit_sha,  # Initially same as base
        status=ChangeRequestStatus.DRAFT.value,
    )

    db.add(change_request)
    await db.commit()
    await db.refresh(change_request)

    return change_request


async def get_change_request(
    db: AsyncSession, cr_id: str
) -> ChangeRequest | None:
    """Get a change request by ID."""
    result = await db.execute(
        select(ChangeRequest)
        .options(
            selectinload(ChangeRequest.author),
            selectinload(ChangeRequest.reviewer),
            selectinload(ChangeRequest.page),
        )
        .where(ChangeRequest.id == cr_id)
    )
    return result.scalar_one_or_none()


async def list_page_change_requests(
    db: AsyncSession,
    page_id: str,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[ChangeRequest], int]:
    """List change requests for a page."""
    query = (
        select(ChangeRequest)
        .options(
            selectinload(ChangeRequest.author),
            selectinload(ChangeRequest.reviewer),
        )
        .where(ChangeRequest.page_id == page_id)
    )

    if status:
        query = query.where(ChangeRequest.status == status)

    # Get total count
    count_query = select(func.count()).select_from(
        query.subquery()
    )
    total = await db.execute(count_query)
    total_count = total.scalar()

    # Get items with pagination
    query = query.order_by(ChangeRequest.created_at.desc())
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    items = list(result.scalars().all())

    return items, total_count


async def update_change_request(
    db: AsyncSession,
    change_request: ChangeRequest,
    cr_in: ChangeRequestUpdate,
) -> ChangeRequest:
    """Update change request metadata."""
    if change_request.status not in [
        ChangeRequestStatus.DRAFT.value,
        ChangeRequestStatus.CHANGES_REQUESTED.value,
    ]:
        raise ValueError("Can only update drafts or change requests needing changes")

    update_data = cr_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(change_request, field, value)

    await db.commit()
    await db.refresh(change_request)
    return change_request


async def save_draft_content(
    db: AsyncSession,
    change_request: ChangeRequest,
    content: dict,
    author: User,
) -> ChangeRequest:
    """Save content changes to a draft.

    This commits changes to the draft's Git branch.
    """
    if change_request.status not in [
        ChangeRequestStatus.DRAFT.value,
        ChangeRequestStatus.CHANGES_REQUESTED.value,
    ]:
        raise ValueError("Can only save to drafts or change requests needing changes")

    # Get page with context
    page = await _get_page_with_context(db, change_request.page_id)
    if not page:
        raise ValueError("Associated page not found")

    org_slug = page.space.workspace.organization.slug
    workspace_slug = page.space.workspace.slug
    space_slug = page.space.slug

    # Save to Git on the draft branch
    git_service = get_git_service()

    # TODO: Switch to draft branch before saving
    # For now, we'll update the file directly and commit
    commit_sha = git_service.update_file(
        org_slug=org_slug,
        workspace_slug=workspace_slug,
        space_slug=space_slug,
        page_slug=page.slug,
        content=content,
        author_name=author.full_name,
        author_email=author.email,
        message=f"Update draft: {change_request.title}",
    )

    # Update head commit SHA
    change_request.head_commit_sha = commit_sha
    await db.commit()
    await db.refresh(change_request)

    return change_request


async def submit_for_review(
    db: AsyncSession,
    change_request: ChangeRequest,
    reviewer_id: str | None = None,
) -> ChangeRequest:
    """Submit a change request for review."""
    if change_request.status not in [
        ChangeRequestStatus.DRAFT.value,
        ChangeRequestStatus.CHANGES_REQUESTED.value,
    ]:
        raise ValueError("Can only submit drafts or change requests needing changes")

    change_request.status = ChangeRequestStatus.SUBMITTED.value
    change_request.submitted_at = datetime.now(timezone.utc)

    if reviewer_id:
        change_request.reviewer_id = reviewer_id

    await db.commit()
    await db.refresh(change_request)
    return change_request


async def start_review(
    db: AsyncSession,
    change_request: ChangeRequest,
    reviewer: User,
) -> ChangeRequest:
    """Start reviewing a change request."""
    if change_request.status != ChangeRequestStatus.SUBMITTED.value:
        raise ValueError("Can only start review on submitted change requests")

    change_request.status = ChangeRequestStatus.IN_REVIEW.value
    change_request.reviewer_id = reviewer.id

    await db.commit()
    await db.refresh(change_request)
    return change_request


async def approve_change_request(
    db: AsyncSession,
    change_request: ChangeRequest,
    reviewer: User,
    comment: str | None = None,
) -> ChangeRequest:
    """Approve a change request."""
    if change_request.status not in [
        ChangeRequestStatus.SUBMITTED.value,
        ChangeRequestStatus.IN_REVIEW.value,
    ]:
        raise ValueError("Can only approve submitted or in-review change requests")

    change_request.status = ChangeRequestStatus.APPROVED.value
    change_request.reviewer_id = reviewer.id
    change_request.reviewed_at = datetime.now(timezone.utc)
    change_request.review_comment = comment

    await db.commit()
    await db.refresh(change_request)
    return change_request


async def request_changes(
    db: AsyncSession,
    change_request: ChangeRequest,
    reviewer: User,
    comment: str,
) -> ChangeRequest:
    """Request changes on a change request."""
    if change_request.status not in [
        ChangeRequestStatus.SUBMITTED.value,
        ChangeRequestStatus.IN_REVIEW.value,
    ]:
        raise ValueError("Can only request changes on submitted or in-review change requests")

    change_request.status = ChangeRequestStatus.CHANGES_REQUESTED.value
    change_request.reviewer_id = reviewer.id
    change_request.reviewed_at = datetime.now(timezone.utc)
    change_request.review_comment = comment

    await db.commit()
    await db.refresh(change_request)
    return change_request


async def reject_change_request(
    db: AsyncSession,
    change_request: ChangeRequest,
    reviewer: User,
    comment: str | None = None,
) -> ChangeRequest:
    """Reject a change request."""
    if change_request.status not in [
        ChangeRequestStatus.SUBMITTED.value,
        ChangeRequestStatus.IN_REVIEW.value,
    ]:
        raise ValueError("Can only reject submitted or in-review change requests")

    change_request.status = ChangeRequestStatus.REJECTED.value
    change_request.reviewer_id = reviewer.id
    change_request.reviewed_at = datetime.now(timezone.utc)
    change_request.review_comment = comment

    await db.commit()
    await db.refresh(change_request)
    return change_request


async def check_conflicts(
    db: AsyncSession,
    change_request: ChangeRequest,
) -> dict:
    """Check if publishing would create conflicts.

    Returns:
        Dict with conflict status and details
    """
    # Get page with context
    page = await _get_page_with_context(db, change_request.page_id)
    if not page:
        raise ValueError("Associated page not found")

    org_slug = page.space.workspace.organization.slug

    git_service = get_git_service()
    result = git_service.check_merge_conflicts(
        org_slug=org_slug,
        source_branch=change_request.branch_name,
        target_branch="master",
    )

    return result


async def publish_change_request(
    db: AsyncSession,
    change_request: ChangeRequest,
    publisher: User,
) -> ChangeRequest:
    """Publish an approved change request (merge to main).

    This merges the draft branch into main and updates the page.
    """
    if change_request.status != ChangeRequestStatus.APPROVED.value:
        raise ValueError("Can only publish approved change requests")

    # Get page with context
    page = await _get_page_with_context(db, change_request.page_id)
    if not page:
        raise ValueError("Associated page not found")

    org_slug = page.space.workspace.organization.slug

    # Merge the branch
    git_service = get_git_service()
    merge_sha = git_service.merge_branch(
        org_slug=org_slug,
        source_branch=change_request.branch_name,
        target_branch="master",  # or "main" depending on setup
        author_name=publisher.full_name,
        author_email=publisher.email,
        message=f"Publish: {change_request.title} (CR-{change_request.number})",
    )

    if not merge_sha:
        raise RuntimeError("Merge failed - possible conflict")

    # Update change request
    change_request.status = ChangeRequestStatus.PUBLISHED.value
    change_request.published_at = datetime.now(timezone.utc)
    change_request.published_by_id = publisher.id
    change_request.merge_commit_sha = merge_sha

    # Update page with new commit SHA
    page.git_commit_sha = merge_sha

    # Update page status and version based on workflow
    now = datetime.now(timezone.utc)

    if page.status == PageStatus.DRAFT.value:
        # First publish: transition from DRAFT to EFFECTIVE
        page.status = PageStatus.EFFECTIVE.value
        page.effective_date = now
        page.approved_date = now
        page.approved_by_id = publisher.id

    elif page.status == PageStatus.EFFECTIVE.value:
        # Subsequent publish: increment version
        if change_request.is_major_revision:
            # Major revision: increment major version, reset minor
            page.major_version += 1
            page.minor_version = 0
            # Increment revision letter (A→B, B→C, etc.)
            current_rev = page.revision or "A"
            next_rev = chr(ord(current_rev[-1]) + 1) if current_rev else "B"
            page.revision = next_rev
        else:
            # Minor revision: increment minor version
            page.minor_version += 1

        # Update legacy version field to match
        page.version = f"{page.major_version}.{page.minor_version}"
        page.effective_date = now

    # For IN_REVIEW or APPROVED pages, also transition to EFFECTIVE
    elif page.status in [PageStatus.IN_REVIEW.value, PageStatus.APPROVED.value]:
        page.status = PageStatus.EFFECTIVE.value
        page.effective_date = now

    await db.commit()
    await db.refresh(change_request)

    # Optionally delete the branch
    git_service.delete_branch(org_slug, change_request.branch_name)

    return change_request


async def cancel_change_request(
    db: AsyncSession,
    change_request: ChangeRequest,
) -> ChangeRequest:
    """Cancel a change request."""
    if change_request.status == ChangeRequestStatus.PUBLISHED.value:
        raise ValueError("Cannot cancel a published change request")

    # Get page with context for branch cleanup
    page = await _get_page_with_context(db, change_request.page_id)
    if page:
        org_slug = page.space.workspace.organization.slug
        git_service = get_git_service()
        git_service.delete_branch(org_slug, change_request.branch_name)

    change_request.status = ChangeRequestStatus.CANCELLED.value
    await db.commit()
    await db.refresh(change_request)

    return change_request


# Comment operations
async def create_comment(
    db: AsyncSession,
    change_request_id: str,
    author: User,
    comment_in: CommentCreate,
) -> ChangeRequestComment:
    """Create a comment on a change request."""
    comment = ChangeRequestComment(
        change_request_id=change_request_id,
        author_id=author.id,
        content=comment_in.content,
        file_path=comment_in.file_path,
        line_number=comment_in.line_number,
        parent_id=comment_in.parent_id,
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def list_comments(
    db: AsyncSession,
    change_request_id: str,
) -> list[ChangeRequestComment]:
    """List all comments on a change request."""
    result = await db.execute(
        select(ChangeRequestComment)
        .options(selectinload(ChangeRequestComment.author))
        .where(ChangeRequestComment.change_request_id == change_request_id)
        .order_by(ChangeRequestComment.created_at)
    )
    return list(result.scalars().all())
