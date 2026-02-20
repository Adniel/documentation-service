"""Pydantic schemas for metadata portability.

Sprint G: Metadata Portability
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# YAML metadata schemas (serialized to/from _meta.yaml, _space.yaml, etc.)
# ============================================================================


class PageMeta(BaseModel):
    """Page metadata stored in _meta.yaml alongside content.json in Git."""

    title: str
    slug: str
    document_number: str | None = None
    revision: str | None = None
    version: str = "1.0"
    status: str = "draft"
    classification: str = "public"
    diataxis_types: list[str] = []
    summary: str | None = None
    author_email: str | None = None
    owner_email: str | None = None
    custodian_email: str | None = None
    effective_date: str | None = None
    next_review_date: str | None = None
    review_cycle_months: int | None = None
    requires_training: bool = False
    training_validity_months: int | None = None
    sort_order: int = 0
    is_template: bool = False
    tags: list[str] = []
    created_at: str | None = None
    updated_at: str | None = None


class SpaceMeta(BaseModel):
    """Space metadata stored in _space.yaml."""

    name: str
    slug: str
    description: str | None = None
    diataxis_type: str = "mixed"
    classification: int = 0
    sort_order: int = 0


class WorkspaceMeta(BaseModel):
    """Workspace metadata stored in _workspace.yaml."""

    name: str
    slug: str
    description: str | None = None
    is_public: bool = False


# ============================================================================
# Export schemas
# ============================================================================


class ExportManifest(BaseModel):
    """Manifest included in export ZIP."""

    format_version: str = "1.0"
    platform: str = "documentation-service"
    exported_at: str
    exported_by: str
    organization: dict[str, str]  # name, slug
    statistics: dict[str, int]  # workspaces, spaces, pages


class ExportFormat(str, Enum):
    """Supported export formats."""

    ZIP = "zip"
    YAML_BUNDLE = "yaml_bundle"


class ExportScope(str, Enum):
    """Scope of export."""

    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    SPACE = "space"
    PAGES = "pages"


class ExportRequest(BaseModel):
    """Request to export content."""

    scope: ExportScope
    resource_id: str = Field(..., description="ID of org/workspace/space to export")
    include_content: bool = True
    include_attachments: bool = False


class ExportResponse(BaseModel):
    """Response after export generation."""

    filename: str
    size_bytes: int
    statistics: dict[str, int]
    download_url: str


# ============================================================================
# Import schemas
# ============================================================================


class ImportFormat(str, Enum):
    """Supported import formats."""

    DOCSERVICE = "docservice"  # Our own export format
    MARKDOWN = "markdown"  # Markdown folder structure
    CONFLUENCE = "confluence"  # Confluence XML/HTML export


class ConflictAction(str, Enum):
    """How to handle conflicts during import."""

    SKIP = "skip"
    OVERWRITE = "overwrite"
    RENAME = "rename"


class ImportItemStatus(str, Enum):
    """Status of each item in import preview."""

    CREATE = "create"
    UPDATE = "update"
    CONFLICT = "conflict"
    SKIP = "skip"
    ERROR = "error"


class ImportItem(BaseModel):
    """A single item in the import preview."""

    path: str
    item_type: str  # "workspace", "space", "page"
    title: str
    slug: str
    status: ImportItemStatus
    conflict_reason: str | None = None
    existing_id: str | None = None  # ID if updating existing


class ImportPreviewResponse(BaseModel):
    """Preview of what an import will do."""

    format_detected: ImportFormat
    items: list[ImportItem]
    statistics: dict[str, int]  # create, update, conflict, skip counts
    warnings: list[str] = []


class ImportConflictResolution(BaseModel):
    """Resolution for a specific conflict."""

    path: str
    action: ConflictAction


class ImportExecuteRequest(BaseModel):
    """Request to execute an import after preview."""

    target_workspace_id: str
    target_space_id: str | None = None
    default_conflict_action: ConflictAction = ConflictAction.SKIP
    resolutions: list[ImportConflictResolution] = []


class ImportResultItem(BaseModel):
    """Result for a single imported item."""

    path: str
    item_type: str
    title: str
    status: str  # "created", "updated", "skipped", "error"
    resource_id: str | None = None
    error: str | None = None


class ImportResult(BaseModel):
    """Result of an import execution."""

    total: int
    created: int
    updated: int
    skipped: int
    errors: int
    items: list[ImportResultItem]
