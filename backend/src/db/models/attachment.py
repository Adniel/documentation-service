"""Attachment model - binary file attachments linked to pages.

Sprint F: Attachments & Media Support

Supports images, PDFs, documents, audio, and video files attached to pages.
Attachments inherit access control from their parent page.

Compliance: 21 CFR Part 11 (attachment hashes included in signature content hash)
"""

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.page import Page
    from src.db.models.user import User


class AttachmentStatus(str, Enum):
    """Attachment lifecycle status."""

    UPLOADING = "uploading"
    ACTIVE = "active"
    REPLACED = "replaced"
    DELETED = "deleted"


class Attachment(Base, UUIDMixin, TimestampMixin):
    """Attachment - binary file linked to a page.

    Storage key format: {org_id}/{page_id}/{attachment_id}/v{version}/{filename}

    Access control is inherited from the parent page's classification and ACL.
    Content hash (SHA-256) is included in the page's signature content hash
    for 21 CFR Part 11 compliance.
    """

    __tablename__ = "attachments"

    # === PARENT PAGE ===
    page_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    # === FILE IDENTITY ===
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)

    # === STORAGE ===
    storage_key: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    storage_backend: Mapped[str] = mapped_column(
        String(50), default="local", nullable=False
    )

    # === INTEGRITY ===
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256

    # === VERSIONING ===
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    replaces_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("attachments.id", ondelete="SET NULL"),
        nullable=True,
    )

    # === STATUS ===
    status: Mapped[str] = mapped_column(
        String(50), default=AttachmentStatus.ACTIVE.value, nullable=False, index=True,
    )

    # === UPLOADER ===
    uploaded_by_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False,
    )

    # === METADATA ===
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    alt_text: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Image dimensions
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Audio/video duration
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    # === DELETION TRACKING ===
    deletion_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # === RELATIONSHIPS ===
    page: Mapped["Page"] = relationship("Page", back_populates="attachments")
    uploaded_by: Mapped["User"] = relationship("User", foreign_keys=[uploaded_by_id])
    replaces: Mapped["Attachment | None"] = relationship(
        "Attachment",
        foreign_keys=[replaces_id],
        remote_side="Attachment.id",
    )

    def __repr__(self) -> str:
        return f"<Attachment {self.filename} (v{self.version})>"

    @property
    def is_image(self) -> bool:
        """Check if attachment is an image."""
        return self.mime_type.startswith("image/")

    @property
    def is_video(self) -> bool:
        """Check if attachment is a video."""
        return self.mime_type.startswith("video/")

    @property
    def is_audio(self) -> bool:
        """Check if attachment is audio."""
        return self.mime_type.startswith("audio/")

    @property
    def human_file_size(self) -> str:
        """Get human-readable file size."""
        size = self.file_size
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
