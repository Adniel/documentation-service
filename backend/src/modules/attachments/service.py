"""Attachment service - business logic for file attachments.

Sprint F: Attachments & Media Support

Handles upload, download, versioning, manifest generation,
and integration with the audit trail.
"""

import hashlib
import re
from datetime import datetime, timezone
from typing import BinaryIO
from uuid import uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.attachment import Attachment, AttachmentStatus
from src.db.models.page import Page
from src.modules.attachments.schemas import (
    AttachmentResponse,
    AttachmentListResponse,
    AttachmentUpdate,
)
from src.modules.attachments.storage import StorageBackend


# Allowed MIME types
ALLOWED_MIME_TYPES = {
    # Images
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
    "image/bmp", "image/tiff",
    # Documents
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain", "text/csv", "text/markdown",
    # Audio
    "audio/mpeg", "audio/wav", "audio/ogg", "audio/webm",
    # Video
    "video/mp4", "video/webm", "video/ogg",
    # Archives
    "application/zip", "application/gzip",
}

# Maximum file size (100 MB)
MAX_FILE_SIZE = 100 * 1024 * 1024


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe storage.

    Removes path separators, special characters, and limits length.
    """
    # Remove directory components
    filename = filename.replace("\\", "/").split("/")[-1]
    # Remove special characters except dots, hyphens, underscores
    filename = re.sub(r"[^\w\-.]", "_", filename)
    # Collapse multiple underscores
    filename = re.sub(r"_+", "_", filename)
    # Limit length (preserve extension)
    if len(filename) > 200:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:200 - len(ext) - 1] + "." + ext if ext else name[:200]
    return filename


def compute_file_hash(data: BinaryIO) -> str:
    """Compute SHA-256 hash of file data.

    Resets the stream position after reading.
    """
    sha256 = hashlib.sha256()
    data.seek(0)
    while True:
        chunk = data.read(8192)
        if not chunk:
            break
        sha256.update(chunk)
    data.seek(0)
    return sha256.hexdigest()


class AttachmentService:
    """Service for managing file attachments."""

    def __init__(self, db: AsyncSession, storage: StorageBackend):
        self.db = db
        self.storage = storage

    async def upload(
        self,
        page_id: str,
        org_id: str,
        filename: str,
        data: BinaryIO,
        content_type: str,
        file_size: int,
        uploaded_by_id: str,
        description: str | None = None,
        alt_text: str | None = None,
        width: int | None = None,
        height: int | None = None,
        duration_seconds: float | None = None,
    ) -> Attachment:
        """Upload a new attachment.

        Args:
            page_id: ID of the parent page
            org_id: Organization ID (for storage key)
            filename: Original filename
            data: File data stream
            content_type: MIME type
            file_size: File size in bytes
            uploaded_by_id: User performing the upload
            description: Optional description
            alt_text: Optional alt text for images
            width: Image width in pixels
            height: Image height in pixels
            duration_seconds: Audio/video duration

        Returns:
            Created Attachment record

        Raises:
            ValueError: If file type not allowed or size exceeds limit
        """
        if content_type not in ALLOWED_MIME_TYPES:
            raise ValueError(f"File type not allowed: {content_type}")
        if file_size > MAX_FILE_SIZE:
            raise ValueError(
                f"File too large: {file_size} bytes (max {MAX_FILE_SIZE})"
            )

        safe_filename = sanitize_filename(filename)
        content_hash = compute_file_hash(data)
        attachment_id = str(uuid4())

        # Build storage key
        storage_key = f"{org_id}/{page_id}/{attachment_id}/v1/{safe_filename}"

        # Store file
        await self.storage.put(storage_key, data, content_type)

        # Create database record
        attachment = Attachment(
            id=attachment_id,
            page_id=page_id,
            filename=safe_filename,
            original_filename=filename,
            mime_type=content_type,
            file_size=file_size,
            storage_key=storage_key,
            storage_backend="local",  # TODO: from config
            content_hash=content_hash,
            version=1,
            status=AttachmentStatus.ACTIVE.value,
            uploaded_by_id=uploaded_by_id,
            description=description,
            alt_text=alt_text,
            width=width,
            height=height,
            duration_seconds=duration_seconds,
        )

        self.db.add(attachment)
        await self.db.flush()

        return attachment

    async def get_by_id(self, attachment_id: str) -> Attachment | None:
        """Get an attachment by ID."""
        result = await self.db.execute(
            select(Attachment).where(Attachment.id == attachment_id)
        )
        return result.scalar_one_or_none()

    async def get_content(self, attachment: Attachment) -> BinaryIO:
        """Get the file content for an attachment.

        Raises:
            FileNotFoundError: If file not found in storage
        """
        return await self.storage.get(attachment.storage_key)

    async def list_for_page(
        self,
        page_id: str,
        include_replaced: bool = False,
    ) -> AttachmentListResponse:
        """List active attachments for a page."""
        query = select(Attachment).where(Attachment.page_id == page_id)

        if not include_replaced:
            query = query.where(
                Attachment.status == AttachmentStatus.ACTIVE.value
            )
        else:
            query = query.where(
                Attachment.status != AttachmentStatus.DELETED.value
            )

        query = query.order_by(Attachment.created_at.asc())
        result = await self.db.execute(query)
        attachments = list(result.scalars().all())

        return AttachmentListResponse(
            attachments=[
                AttachmentResponse.model_validate(a) for a in attachments
            ],
            total=len(attachments),
        )

    async def update_metadata(
        self,
        attachment: Attachment,
        update: AttachmentUpdate,
    ) -> Attachment:
        """Update attachment metadata (description, alt_text)."""
        update_data = update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(attachment, key, value)

        await self.db.flush()
        return attachment

    async def replace(
        self,
        attachment: Attachment,
        org_id: str,
        data: BinaryIO,
        content_type: str,
        file_size: int,
        filename: str,
        uploaded_by_id: str,
        reason: str,
        width: int | None = None,
        height: int | None = None,
        duration_seconds: float | None = None,
    ) -> Attachment:
        """Replace an attachment with a new version.

        The old attachment is marked as 'replaced', and a new attachment
        is created with version incremented.

        Args:
            attachment: The attachment being replaced
            org_id: Organization ID
            data: New file data
            content_type: New file MIME type
            file_size: New file size
            filename: New filename
            uploaded_by_id: User performing the replacement
            reason: Reason for replacement (audit trail)
            width: Image width
            height: Image height
            duration_seconds: Audio/video duration

        Returns:
            The new replacement Attachment
        """
        if content_type not in ALLOWED_MIME_TYPES:
            raise ValueError(f"File type not allowed: {content_type}")
        if file_size > MAX_FILE_SIZE:
            raise ValueError(
                f"File too large: {file_size} bytes (max {MAX_FILE_SIZE})"
            )

        safe_filename = sanitize_filename(filename)
        content_hash = compute_file_hash(data)
        new_id = str(uuid4())
        new_version = attachment.version + 1

        storage_key = (
            f"{org_id}/{attachment.page_id}/{new_id}/v{new_version}/{safe_filename}"
        )

        # Store new file
        await self.storage.put(storage_key, data, content_type)

        # Mark old as replaced
        attachment.status = AttachmentStatus.REPLACED.value

        # Create new record
        new_attachment = Attachment(
            id=new_id,
            page_id=attachment.page_id,
            filename=safe_filename,
            original_filename=filename,
            mime_type=content_type,
            file_size=file_size,
            storage_key=storage_key,
            storage_backend=attachment.storage_backend,
            content_hash=content_hash,
            version=new_version,
            replaces_id=attachment.id,
            status=AttachmentStatus.ACTIVE.value,
            uploaded_by_id=uploaded_by_id,
            description=attachment.description,
            alt_text=attachment.alt_text,
            width=width,
            height=height,
            duration_seconds=duration_seconds,
        )

        self.db.add(new_attachment)
        await self.db.flush()

        return new_attachment

    async def soft_delete(
        self,
        attachment: Attachment,
        reason: str,
    ) -> Attachment:
        """Soft-delete an attachment with reason (for audit trail).

        The file is not removed from storage immediately; a background
        job should clean up deleted files after the retention period.
        """
        attachment.status = AttachmentStatus.DELETED.value
        attachment.deletion_reason = reason
        await self.db.flush()
        return attachment

    async def generate_manifest_markdown(self, page: Page) -> str | None:
        """Generate an attachments manifest as Markdown for Git storage.

        Returns None if the page has no active attachments.
        """
        listing = await self.list_for_page(page.id)
        if listing.total == 0:
            return None

        lines = [
            f"# Attachments: {page.title}",
            "",
            "| File | Type | Size | SHA-256 | Version |",
            "|------|------|------|---------|---------|",
        ]

        for att in listing.attachments:
            # Human-readable size
            size = att.file_size
            for unit in ("B", "KB", "MB", "GB"):
                if size < 1024:
                    size_str = f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
                    break
                size /= 1024
            else:
                size_str = f"{size:.1f} TB"

            hash_short = att.content_hash[:12] + "..."
            lines.append(
                f"| {att.filename} | {att.mime_type} | {size_str} "
                f"| {hash_short} | {att.version} |"
            )

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        lines.extend(["", f"Generated: {now}"])

        return "\n".join(lines)

    async def get_active_hashes_for_page(self, page_id: str) -> list[str]:
        """Get content hashes of all active attachments for a page.

        Used for computing the combined content hash during electronic signing.
        """
        result = await self.db.execute(
            select(Attachment.content_hash)
            .where(
                Attachment.page_id == page_id,
                Attachment.status == AttachmentStatus.ACTIVE.value,
            )
            .order_by(Attachment.filename.asc())
        )
        return [row[0] for row in result.all()]
