"""Attachments module - binary file attachment support.

Sprint F: Attachments & Media Support
"""

from src.modules.attachments.schemas import (
    AttachmentResponse,
    AttachmentListResponse,
    AttachmentUpdate,
    AttachmentReplaceRequest,
    AttachmentDeleteRequest,
    AttachmentManifest,
)
from src.modules.attachments.service import AttachmentService
from src.modules.attachments.storage import (
    StorageBackend,
    LocalFilesystemStorage,
    S3Storage,
    get_storage_backend,
)

__all__ = [
    # Schemas
    "AttachmentResponse",
    "AttachmentListResponse",
    "AttachmentUpdate",
    "AttachmentReplaceRequest",
    "AttachmentDeleteRequest",
    "AttachmentManifest",
    # Service
    "AttachmentService",
    # Storage
    "StorageBackend",
    "LocalFilesystemStorage",
    "S3Storage",
    "get_storage_backend",
]
