"""Change Request (Draft) API endpoints for Sprint 4 Version Control UI."""

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import DbSession, CurrentUser
from src.modules.content.change_request_schemas import (
    ChangeRequestCreate,
    ChangeRequestUpdate,
    ChangeRequestSubmit,
    ChangeRequestReview,
    ChangeRequestResponse,
    ChangeRequestListResponse,
    CommentCreate,
    CommentResponse,
    DiffResult,
)
from src.modules.content import change_request_service as cr_service
from src.modules.content import diff_service
from src.modules.content.service import get_page

router = APIRouter()


def _to_response(cr, include_author: bool = True) -> ChangeRequestResponse:
    """Convert ChangeRequest model to response schema."""
    return ChangeRequestResponse(
        id=cr.id,
        page_id=cr.page_id,
        title=cr.title,
        description=cr.description,
        number=cr.number,
        status=cr.status,
        branch_name=cr.branch_name,
        base_commit_sha=cr.base_commit_sha,
        head_commit_sha=cr.head_commit_sha,
        author_id=cr.author_id,
        author_name=cr.author.full_name if include_author and cr.author else None,
        author_email=cr.author.email if include_author and cr.author else None,
        submitted_at=cr.submitted_at,
        reviewer_id=cr.reviewer_id,
        reviewer_name=cr.reviewer.full_name if cr.reviewer else None,
        reviewed_at=cr.reviewed_at,
        review_comment=cr.review_comment,
        published_at=cr.published_at,
        published_by_id=cr.published_by_id,
        merge_commit_sha=cr.merge_commit_sha,
        created_at=cr.created_at,
        updated_at=cr.updated_at,
    )


# ==================== Draft/Change Request CRUD ====================


@router.post(
    "/pages/{page_id}/drafts",
    response_model=ChangeRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_draft(
    page_id: str,
    cr_in: ChangeRequestCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ChangeRequestResponse:
    """Create a new draft (change request) for a page."""
    # Verify page exists
    page = await get_page(db, page_id)
    if not page or not page.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    try:
        cr = await cr_service.create_change_request(
            db=db,
            page_id=page_id,
            author=current_user,
            cr_in=cr_in,
        )
        return _to_response(cr)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/pages/{page_id}/drafts", response_model=ChangeRequestListResponse)
async def list_drafts(
    page_id: str,
    db: DbSession,
    current_user: CurrentUser,
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ChangeRequestListResponse:
    """List all drafts (change requests) for a page."""
    # Verify page exists
    page = await get_page(db, page_id)
    if not page or not page.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    items, total = await cr_service.list_page_change_requests(
        db=db,
        page_id=page_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return ChangeRequestListResponse(
        items=[_to_response(cr) for cr in items],
        total=total,
    )


@router.get("/drafts/{draft_id}", response_model=ChangeRequestResponse)
async def get_draft(
    draft_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> ChangeRequestResponse:
    """Get a draft (change request) by ID."""
    cr = await cr_service.get_change_request(db, draft_id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    return _to_response(cr)


@router.patch("/drafts/{draft_id}", response_model=ChangeRequestResponse)
async def update_draft(
    draft_id: str,
    cr_in: ChangeRequestUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ChangeRequestResponse:
    """Update draft metadata (title, description)."""
    cr = await cr_service.get_change_request(db, draft_id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    # Only author can update their draft
    if cr.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author can update this draft",
        )

    try:
        updated = await cr_service.update_change_request(db, cr, cr_in)
        return _to_response(updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_draft(
    draft_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Cancel a draft (change request)."""
    cr = await cr_service.get_change_request(db, draft_id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    # Only author can cancel their draft
    if cr.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author can cancel this draft",
        )

    try:
        await cr_service.cancel_change_request(db, cr)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==================== Workflow Actions ====================


@router.post("/drafts/{draft_id}/submit", response_model=ChangeRequestResponse)
async def submit_for_review(
    draft_id: str,
    submit_in: ChangeRequestSubmit,
    db: DbSession,
    current_user: CurrentUser,
) -> ChangeRequestResponse:
    """Submit a draft for review."""
    cr = await cr_service.get_change_request(db, draft_id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    # Only author can submit their draft
    if cr.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author can submit this draft",
        )

    try:
        updated = await cr_service.submit_for_review(
            db, cr, reviewer_id=submit_in.reviewer_id
        )
        return _to_response(updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/drafts/{draft_id}/approve", response_model=ChangeRequestResponse)
async def approve_draft(
    draft_id: str,
    review_in: ChangeRequestReview,
    db: DbSession,
    current_user: CurrentUser,
) -> ChangeRequestResponse:
    """Approve a submitted draft."""
    cr = await cr_service.get_change_request(db, draft_id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    # Author cannot approve their own draft
    if cr.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authors cannot approve their own drafts",
        )

    try:
        updated = await cr_service.approve_change_request(
            db, cr, reviewer=current_user, comment=review_in.comment
        )
        return _to_response(updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/drafts/{draft_id}/request-changes", response_model=ChangeRequestResponse)
async def request_changes_on_draft(
    draft_id: str,
    review_in: ChangeRequestReview,
    db: DbSession,
    current_user: CurrentUser,
) -> ChangeRequestResponse:
    """Request changes on a submitted draft."""
    cr = await cr_service.get_change_request(db, draft_id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    if not review_in.comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment is required when requesting changes",
        )

    try:
        updated = await cr_service.request_changes(
            db, cr, reviewer=current_user, comment=review_in.comment
        )
        return _to_response(updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/drafts/{draft_id}/reject", response_model=ChangeRequestResponse)
async def reject_draft(
    draft_id: str,
    review_in: ChangeRequestReview,
    db: DbSession,
    current_user: CurrentUser,
) -> ChangeRequestResponse:
    """Reject a submitted draft."""
    cr = await cr_service.get_change_request(db, draft_id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    try:
        updated = await cr_service.reject_change_request(
            db, cr, reviewer=current_user, comment=review_in.comment
        )
        return _to_response(updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/drafts/{draft_id}/conflicts")
async def check_conflicts(
    draft_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    """Check if publishing would create merge conflicts."""
    cr = await cr_service.get_change_request(db, draft_id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    try:
        result = await cr_service.check_conflicts(db, cr)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/drafts/{draft_id}/publish", response_model=ChangeRequestResponse)
async def publish_draft(
    draft_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> ChangeRequestResponse:
    """Publish an approved draft (merge to main)."""
    cr = await cr_service.get_change_request(db, draft_id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    try:
        updated = await cr_service.publish_change_request(db, cr, publisher=current_user)
        return _to_response(updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


# ==================== Diff ====================


@router.get("/pages/{page_id}/diff", response_model=DiffResult)
async def get_page_diff(
    page_id: str,
    from_sha: str,
    to_sha: str,
    db: DbSession,
    current_user: CurrentUser,
) -> DiffResult:
    """Get diff between two versions of a page."""
    try:
        return await diff_service.get_page_diff(db, page_id, from_sha, to_sha)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/drafts/{draft_id}/diff", response_model=DiffResult)
async def get_draft_diff(
    draft_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> DiffResult:
    """Get diff showing changes in a draft compared to the published version."""
    try:
        return await diff_service.get_change_request_diff(db, draft_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==================== Comments ====================


@router.post(
    "/drafts/{draft_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    draft_id: str,
    comment_in: CommentCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> CommentResponse:
    """Add a comment to a draft."""
    cr = await cr_service.get_change_request(db, draft_id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    comment = await cr_service.create_comment(
        db, change_request_id=draft_id, author=current_user, comment_in=comment_in
    )

    return CommentResponse(
        id=comment.id,
        change_request_id=comment.change_request_id,
        author_id=comment.author_id,
        author_name=current_user.full_name,
        content=comment.content,
        file_path=comment.file_path,
        line_number=comment.line_number,
        parent_id=comment.parent_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.get("/drafts/{draft_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    draft_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> list[CommentResponse]:
    """List all comments on a draft."""
    cr = await cr_service.get_change_request(db, draft_id)
    if not cr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    comments = await cr_service.list_comments(db, draft_id)

    return [
        CommentResponse(
            id=c.id,
            change_request_id=c.change_request_id,
            author_id=c.author_id,
            author_name=c.author.full_name if c.author else None,
            content=c.content,
            file_path=c.file_path,
            line_number=c.line_number,
            parent_id=c.parent_id,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in comments
    ]
