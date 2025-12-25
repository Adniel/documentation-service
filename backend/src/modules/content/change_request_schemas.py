"""Pydantic schemas for change request (draft) management."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ChangeRequestStatus(str, Enum):
    """Status of a change request through its lifecycle."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


# Change Request schemas
class ChangeRequestCreate(BaseModel):
    """Create a new change request (draft)."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None


class ChangeRequestUpdate(BaseModel):
    """Update change request metadata."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None


class ChangeRequestSubmit(BaseModel):
    """Submit change request for review."""

    reviewer_id: str | None = None  # Optional: assign specific reviewer


class ChangeRequestReview(BaseModel):
    """Review action on a change request."""

    comment: str | None = None


class ChangeRequestResponse(BaseModel):
    """Change request response schema."""

    id: str
    page_id: str
    title: str
    description: str | None
    number: int
    status: ChangeRequestStatus
    branch_name: str
    base_commit_sha: str
    head_commit_sha: str | None

    # Author
    author_id: str
    author_name: str | None = None
    author_email: str | None = None

    # Review
    submitted_at: datetime | None
    reviewer_id: str | None
    reviewer_name: str | None = None
    reviewed_at: datetime | None
    review_comment: str | None

    # Publication
    published_at: datetime | None
    published_by_id: str | None
    merge_commit_sha: str | None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChangeRequestListResponse(BaseModel):
    """List of change requests."""

    items: list[ChangeRequestResponse]
    total: int


# Comment schemas
class CommentCreate(BaseModel):
    """Create a comment on a change request."""

    content: str = Field(..., min_length=1)
    file_path: str | None = None
    line_number: int | None = None
    parent_id: str | None = None  # For replies


class CommentResponse(BaseModel):
    """Comment response schema."""

    id: str
    change_request_id: str
    author_id: str
    author_name: str | None = None
    content: str
    file_path: str | None
    line_number: int | None
    parent_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Diff schemas
class DiffHunk(BaseModel):
    """A single diff hunk."""

    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    content: str


class DiffResult(BaseModel):
    """Result of a diff operation."""

    from_sha: str
    to_sha: str
    hunks: list[DiffHunk]
    additions: int
    deletions: int
    is_binary: bool = False
