"""Content (Pages) API endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request, status

from src.api.deps import DbSession, CurrentUser
from src.db.models.page import PageStatus
from src.modules.content.schemas import (
    PageCreate,
    PageUpdate,
    PageResponse,
    PageSummary,
)
from src.modules.content.service import (
    create_page,
    get_page,
    get_page_with_space,
    list_space_pages,
    update_page,
    delete_page,
    get_space,
    get_workspace,
    get_organization,
)
from src.modules.content.git_service import get_git_service
from src.modules.audit.audit_service import AuditService
from src.modules.document_control.content_hash_service import compute_content_hash

router = APIRouter()


@router.post("/pages", response_model=PageResponse, status_code=status.HTTP_201_CREATED)
async def create_pg(
    page_in: PageCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> PageResponse:
    """Create a new page in a space."""
    # Verify space exists
    space = await get_space(db, page_in.space_id)
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found",
        )

    # Get workspace and organization for Git path
    workspace = await get_workspace(db, space.workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    org = await get_organization(db, workspace.organization_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Create page in database
    page = await create_page(db, page_in, current_user.id)

    # Save content to Git
    content_hash = None
    if page_in.content:
        content_hash = compute_content_hash(page_in.content)
        git_service = get_git_service()
        commit_sha = git_service.create_file(
            org_slug=org.slug,
            workspace_slug=workspace.slug,
            space_slug=space.slug,
            page_slug=page.slug,
            content={
                "title": page.title,
                "content": page_in.content,
                "metadata": {
                    "author_id": current_user.id,
                    "classification": page.classification,
                },
            },
            author_name=current_user.full_name,
            author_email=current_user.email,
            message=f"Create page: {page.title}",
        )

        # Update page with Git info
        page.git_path = f"{workspace.slug}/{space.slug}/{page.slug}.json"
        page.git_commit_sha = commit_sha
        await db.commit()
        await db.refresh(page)

    # Audit: Log page creation (21 CFR §11.10(e))
    audit_service = AuditService(db)
    await audit_service.log_content_created(
        actor_id=str(current_user.id),
        actor_email=current_user.email,
        resource_type="page",
        resource_id=str(page.id),
        resource_name=page.title,
        content_hash=content_hash,
        parent_id=str(space.id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await db.commit()

    return PageResponse.model_validate(page)


@router.get("/space/{space_id}/pages", response_model=list[PageSummary])
async def list_pg_by_space(
    space_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> list[PageSummary]:
    """List pages in a space."""
    pages = await list_space_pages(db, space_id)
    return [PageSummary.model_validate(pg) for pg in pages]


@router.get("/pages/{page_id}", response_model=PageResponse)
async def get_pg(
    page_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> PageResponse:
    """Get a page by ID."""
    page = await get_page(db, page_id)
    if not page or not page.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )
    return PageResponse.model_validate(page)


@router.patch("/pages/{page_id}", response_model=PageResponse)
async def update_pg(
    page_id: str,
    page_in: PageUpdate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
    reason: Optional[str] = Query(
        None,
        min_length=10,
        max_length=1000,
        description="Reason for the change (required for compliance)"
    ),
) -> PageResponse:
    """Update a page.

    For compliance with 21 CFR §11.10(e), a reason for the change
    should be provided via the 'reason' query parameter.
    """
    page = await get_page_with_space(db, page_id)
    if not page or not page.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    # Enforce read-only for controlled documents (ISO 9001 compliance)
    # Pages in EFFECTIVE, IN_REVIEW, or APPROVED status require a Change Request
    controlled_statuses = [
        PageStatus.EFFECTIVE.value,
        PageStatus.IN_REVIEW.value,
        PageStatus.APPROVED.value,
    ]
    if page.status in controlled_statuses:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "controlled_document",
                "message": "This document is under control. Create a change request to propose edits.",
                "page_status": page.status,
                "action": "create_change_request",
            },
        )

    # Capture previous content hash for audit
    previous_hash = None
    if page_in.content is not None:
        # Get current content from Git if available
        if page.git_path:
            workspace = await get_workspace(db, page.space.workspace_id)
            org = await get_organization(db, workspace.organization_id)
            git_service = get_git_service()
            try:
                current_content = git_service.get_file_content(
                    org_slug=org.slug,
                    workspace_slug=workspace.slug,
                    space_slug=page.space.slug,
                    page_slug=page.slug,
                )
                if current_content and current_content.get("content"):
                    previous_hash = compute_content_hash(current_content["content"])
            except FileNotFoundError:
                pass

    # Update in database
    updated = await update_page(db, page, page_in)

    # If content changed, update Git
    new_hash = None
    if page_in.content is not None:
        new_hash = compute_content_hash(page_in.content)
        workspace = await get_workspace(db, page.space.workspace_id)
        org = await get_organization(db, workspace.organization_id)

        git_service = get_git_service()
        try:
            commit_sha = git_service.update_file(
                org_slug=org.slug,
                workspace_slug=workspace.slug,
                space_slug=page.space.slug,
                page_slug=page.slug,
                content={
                    "title": updated.title,
                    "content": page_in.content,
                    "metadata": {
                        "author_id": current_user.id,
                        "classification": updated.classification,
                    },
                },
                author_name=current_user.full_name,
                author_email=current_user.email,
                message=f"Update page: {updated.title}" + (f" - {reason}" if reason else ""),
            )
            updated.git_commit_sha = commit_sha
            await db.commit()
            await db.refresh(updated)
        except FileNotFoundError:
            # File doesn't exist in Git yet, create it
            commit_sha = git_service.create_file(
                org_slug=org.slug,
                workspace_slug=workspace.slug,
                space_slug=page.space.slug,
                page_slug=page.slug,
                content={
                    "title": updated.title,
                    "content": page_in.content,
                    "metadata": {
                        "author_id": current_user.id,
                        "classification": updated.classification,
                    },
                },
                author_name=current_user.full_name,
                author_email=current_user.email,
                message=f"Create page: {updated.title}",
            )
            updated.git_path = f"{workspace.slug}/{page.space.slug}/{page.slug}.json"
            updated.git_commit_sha = commit_sha
            await db.commit()
            await db.refresh(updated)

    # Audit: Log page update (21 CFR §11.10(e))
    audit_service = AuditService(db)
    await audit_service.log_content_updated(
        actor_id=str(current_user.id),
        actor_email=current_user.email,
        resource_type="page",
        resource_id=str(page.id),
        resource_name=updated.title,
        reason=reason or "No reason provided",
        previous_hash=previous_hash,
        new_hash=new_hash,
        changes={
            "title_changed": page_in.title is not None,
            "content_changed": page_in.content is not None,
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await db.commit()

    return PageResponse.model_validate(updated)


@router.delete("/pages/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pg(
    page_id: str,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
    reason: str = Query(
        ...,
        min_length=10,
        max_length=1000,
        description="Reason for deletion (required for compliance)"
    ),
) -> None:
    """Delete a page (soft delete).

    For compliance with 21 CFR §11.10(e), a reason for deletion
    is required via the 'reason' query parameter.
    """
    page = await get_page(db, page_id)
    if not page or not page.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    # Capture page info before deletion for audit
    page_title = page.title
    page_id_str = str(page.id)

    await delete_page(db, page)

    # Audit: Log page deletion (21 CFR §11.10(e))
    audit_service = AuditService(db)
    await audit_service.log_content_deleted(
        actor_id=str(current_user.id),
        actor_email=current_user.email,
        resource_type="page",
        resource_id=page_id_str,
        resource_name=page_title,
        reason=reason,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await db.commit()


@router.get("/pages/{page_id}/history")
async def get_pg_history(
    page_id: str,
    db: DbSession,
    current_user: CurrentUser,
    limit: int = 50,
) -> list[dict]:
    """Get version history for a page."""
    page = await get_page_with_space(db, page_id)
    if not page or not page.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    if not page.git_path:
        return []

    workspace = await get_workspace(db, page.space.workspace_id)
    org = await get_organization(db, workspace.organization_id)

    git_service = get_git_service()
    history = git_service.get_file_history(
        org_slug=org.slug,
        workspace_slug=workspace.slug,
        space_slug=page.space.slug,
        page_slug=page.slug,
        limit=limit,
    )

    return history
