"""Attachment API endpoints.

Sprint F: Attachments & Media Support

Handles file upload, download, metadata management, versioning,
and public access for published sites.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from src.api.deps import DbSession, CurrentUser
from src.config import get_settings
from src.db.models.attachment import Attachment, AttachmentStatus
from src.db.models.page import Page
from src.db.models.published_site import PublishedSite
from src.modules.attachments.schemas import (
    AttachmentResponse,
    AttachmentListResponse,
    AttachmentUpdate,
    AttachmentReplaceRequest,
    AttachmentDeleteRequest,
)
from src.modules.attachments.service import AttachmentService, ALLOWED_MIME_TYPES
from src.modules.attachments.storage import get_storage_backend

router = APIRouter()

settings = get_settings()


def _get_attachment_service(db) -> AttachmentService:
    """Create AttachmentService with configured storage backend."""
    storage = get_storage_backend(
        backend_type=settings.attachment_storage_backend,
        base_path=settings.attachment_storage_path,
        s3_bucket=settings.attachment_s3_bucket,
        s3_region=settings.attachment_s3_region,
        s3_endpoint_url=settings.attachment_s3_endpoint_url,
        s3_access_key=settings.attachment_s3_access_key,
        s3_secret_key=settings.attachment_s3_secret_key,
    )
    return AttachmentService(db, storage)


@router.post("/upload", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    db: DbSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    page_id: str = Form(...),
    description: str | None = Form(None),
    alt_text: str | None = Form(None),
) -> AttachmentResponse:
    """Upload a file attachment to a page.

    Accepts multipart/form-data with the file and metadata.
    Returns the created attachment metadata.
    """
    # Validate page exists
    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    # Get organization ID from page -> space -> workspace
    from src.db.models.space import Space
    from src.db.models.workspace import Workspace

    space_result = await db.execute(select(Space).where(Space.id == page.space_id))
    space = space_result.scalar_one_or_none()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    ws_result = await db.execute(
        select(Workspace).where(Workspace.id == space.workspace_id)
    )
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    org_id = workspace.organization_id

    # Validate content type
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed: {content_type}",
        )

    # Read file size
    file_data = await file.read()
    file_size = len(file_data)

    from io import BytesIO
    data_stream = BytesIO(file_data)

    service = _get_attachment_service(db)

    try:
        attachment = await service.upload(
            page_id=page_id,
            org_id=org_id,
            filename=file.filename or "unnamed",
            data=data_stream,
            content_type=content_type,
            file_size=file_size,
            uploaded_by_id=current_user.id,
            description=description,
            alt_text=alt_text,
        )
        await db.commit()
        return AttachmentResponse.model_validate(attachment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment_metadata(
    attachment_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> AttachmentResponse:
    """Get attachment metadata without downloading the file."""
    service = _get_attachment_service(db)
    attachment = await service.get_by_id(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return AttachmentResponse.model_validate(attachment)


@router.get("/{attachment_id}/content")
async def download_attachment(
    attachment_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> StreamingResponse:
    """Download attachment file content.

    Streams the file with appropriate content type and disposition headers.
    """
    service = _get_attachment_service(db)
    attachment = await service.get_by_id(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    if attachment.status == AttachmentStatus.DELETED.value:
        raise HTTPException(status_code=410, detail="Attachment has been deleted")

    try:
        content = await service.get_content(attachment)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found in storage")

    # Determine if inline or download
    inline_types = {"image/", "application/pdf", "text/"}
    disposition = "inline" if any(
        attachment.mime_type.startswith(t) for t in inline_types
    ) else "attachment"

    return StreamingResponse(
        content,
        media_type=attachment.mime_type,
        headers={
            "Content-Disposition": f'{disposition}; filename="{attachment.filename}"',
            "Content-Length": str(attachment.file_size),
            "Cache-Control": "private, max-age=3600",
            "ETag": attachment.content_hash,
        },
    )


@router.get("/{attachment_id}/thumbnail")
async def get_attachment_thumbnail(
    attachment_id: str,
    db: DbSession,
    current_user: CurrentUser,
    width: int = Query(200, ge=32, le=800),
    height: int = Query(200, ge=32, le=800),
) -> StreamingResponse:
    """Get a thumbnail for an image attachment.

    For now, returns the original image. Thumbnail generation can be
    added later with Pillow or an image processing service.
    """
    service = _get_attachment_service(db)
    attachment = await service.get_by_id(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    if not attachment.mime_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Thumbnails only available for images")

    try:
        content = await service.get_content(attachment)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found in storage")

    return StreamingResponse(
        content,
        media_type=attachment.mime_type,
        headers={
            "Cache-Control": "private, max-age=86400",
            "ETag": f"{attachment.content_hash}-thumb",
        },
    )


@router.get("/page/{page_id}", response_model=AttachmentListResponse)
async def list_page_attachments(
    page_id: str,
    db: DbSession,
    current_user: CurrentUser,
    include_replaced: bool = Query(False, description="Include replaced versions"),
) -> AttachmentListResponse:
    """List attachments for a page."""
    # Verify page exists
    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    service = _get_attachment_service(db)
    return await service.list_for_page(page_id, include_replaced=include_replaced)


@router.patch("/{attachment_id}", response_model=AttachmentResponse)
async def update_attachment_metadata(
    attachment_id: str,
    update: AttachmentUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> AttachmentResponse:
    """Update attachment metadata (description, alt_text)."""
    service = _get_attachment_service(db)
    attachment = await service.get_by_id(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    if attachment.status != AttachmentStatus.ACTIVE.value:
        raise HTTPException(status_code=400, detail="Cannot update inactive attachment")

    attachment = await service.update_metadata(attachment, update)
    await db.commit()
    return AttachmentResponse.model_validate(attachment)


@router.post("/{attachment_id}/replace", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def replace_attachment(
    attachment_id: str,
    db: DbSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    reason: str = Form(...),
) -> AttachmentResponse:
    """Replace an attachment with a new version.

    The old attachment is marked as 'replaced' and a new version is created.
    A reason for the replacement is required for the audit trail.
    """
    service = _get_attachment_service(db)
    attachment = await service.get_by_id(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    if attachment.status != AttachmentStatus.ACTIVE.value:
        raise HTTPException(status_code=400, detail="Cannot replace inactive attachment")

    # Get org_id
    page_result = await db.execute(select(Page).where(Page.id == attachment.page_id))
    page = page_result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    from src.db.models.space import Space
    from src.db.models.workspace import Workspace

    space_result = await db.execute(select(Space).where(Space.id == page.space_id))
    space = space_result.scalar_one_or_none()
    ws_result = await db.execute(
        select(Workspace).where(Workspace.id == space.workspace_id)
    )
    workspace = ws_result.scalar_one_or_none()
    org_id = workspace.organization_id

    content_type = file.content_type or "application/octet-stream"
    file_data = await file.read()
    file_size = len(file_data)

    from io import BytesIO
    data_stream = BytesIO(file_data)

    try:
        new_attachment = await service.replace(
            attachment=attachment,
            org_id=org_id,
            data=data_stream,
            content_type=content_type,
            file_size=file_size,
            filename=file.filename or "unnamed",
            uploaded_by_id=current_user.id,
            reason=reason,
        )
        await db.commit()
        return AttachmentResponse.model_validate(new_attachment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{attachment_id}", status_code=status.HTTP_200_OK)
async def delete_attachment(
    attachment_id: str,
    body: AttachmentDeleteRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    """Soft-delete an attachment.

    Requires a reason for the audit trail. The file is not immediately
    removed from storage.
    """
    service = _get_attachment_service(db)
    attachment = await service.get_by_id(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    if attachment.status == AttachmentStatus.DELETED.value:
        raise HTTPException(status_code=400, detail="Attachment already deleted")

    await service.soft_delete(attachment, reason=body.reason)
    await db.commit()
    return {"message": "Attachment deleted", "id": attachment_id}


@router.get("/public/{site_slug}/{attachment_id}/content")
async def public_attachment_content(
    site_slug: str,
    attachment_id: str,
    db: DbSession,
) -> StreamingResponse:
    """Public access to attachment content on published sites.

    Access is controlled through the parent page's visibility settings
    on the published site.
    """
    # Find the published site
    site_result = await db.execute(
        select(PublishedSite).where(PublishedSite.slug == site_slug)
    )
    site = site_result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Find the attachment
    service = _get_attachment_service(db)
    attachment = await service.get_by_id(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    if attachment.status != AttachmentStatus.ACTIVE.value:
        raise HTTPException(status_code=404, detail="Attachment not available")

    # Verify the attachment's page belongs to the site's space
    page_result = await db.execute(
        select(Page).where(Page.id == attachment.page_id)
    )
    page = page_result.scalar_one_or_none()
    if not page or page.space_id != site.space_id:
        raise HTTPException(status_code=404, detail="Attachment not found on this site")

    try:
        content = await service.get_content(attachment)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found in storage")

    inline_types = {"image/", "application/pdf", "text/"}
    disposition = "inline" if any(
        attachment.mime_type.startswith(t) for t in inline_types
    ) else "attachment"

    return StreamingResponse(
        content,
        media_type=attachment.mime_type,
        headers={
            "Content-Disposition": f'{disposition}; filename="{attachment.filename}"',
            "Content-Length": str(attachment.file_size),
            "Cache-Control": "public, max-age=86400",
            "ETag": attachment.content_hash,
        },
    )
