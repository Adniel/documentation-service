"""Pydantic schemas for attachment module.

Sprint F: Attachments & Media Support
"""

from datetime import datetime

from pydantic import BaseModel, Field

from src.db.models.attachment import AttachmentStatus


class AttachmentResponse(BaseModel):
    """Attachment metadata response."""

    id: str
    page_id: str
    filename: str
    original_filename: str
    mime_type: str
    file_size: int
    content_hash: str
    version: int
    replaces_id: str | None = None
    status: AttachmentStatus
    uploaded_by_id: str
    description: str | None = None
    alt_text: str | None = None
    width: int | None = None
    height: int | None = None
    duration_seconds: float | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AttachmentUpdate(BaseModel):
    """Schema for updating attachment metadata."""

    description: str | None = None
    alt_text: str | None = None


class AttachmentReplaceRequest(BaseModel):
    """Schema for replacing an attachment with a new version."""

    reason: str = Field(..., min_length=1, max_length=1000)


class AttachmentDeleteRequest(BaseModel):
    """Schema for deleting an attachment (reason required for audit)."""

    reason: str = Field(..., min_length=1, max_length=1000)


class AttachmentListResponse(BaseModel):
    """List of attachments for a page."""

    attachments: list[AttachmentResponse]
    total: int


class AttachmentManifest(BaseModel):
    """Attachment manifest for Git storage."""

    page_id: str
    page_title: str
    attachments: list[AttachmentResponse]
    generated_at: datetime
