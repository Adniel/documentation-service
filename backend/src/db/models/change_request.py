"""Change Request model for version control workflow.

Sprint 6: Extended with approval workflow integration.

Compliance: ISO 9001 §7.5.2 - Documents must be approved before release
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.approval import ApprovalMatrix, ApprovalRecord
    from src.db.models.page import Page
    from src.db.models.user import User


class ChangeRequestStatus(str, Enum):
    """Status of a change request through its lifecycle."""

    DRAFT = "draft"  # Work in progress
    SUBMITTED = "submitted"  # Submitted for review
    IN_REVIEW = "in_review"  # Being reviewed
    CHANGES_REQUESTED = "changes_requested"  # Reviewer requested changes
    APPROVED = "approved"  # Approved, ready to publish
    PUBLISHED = "published"  # Merged to main
    REJECTED = "rejected"  # Rejected by reviewer
    CANCELLED = "cancelled"  # Cancelled by author


class ChangeRequest(Base, UUIDMixin, TimestampMixin):
    """Application-level tracking of document drafts (Git branches).

    This model abstracts Git branches into user-friendly "drafts" or "change requests".
    Users never see Git concepts - they work with drafts that can be submitted,
    reviewed, approved, and published.
    """

    __tablename__ = "change_requests"

    # Document being edited
    page_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("pages.id"), nullable=False, index=True
    )

    # Change request metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Sequential number for this page's change requests
    number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Author
    author_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False
    )

    # Git tracking (hidden from user)
    branch_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    base_commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    head_commit_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default=ChangeRequestStatus.DRAFT.value, nullable=False, index=True
    )

    # Review tracking
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reviewer_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Publication
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    published_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=True
    )
    merge_commit_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # === APPROVAL WORKFLOW FIELDS (Sprint 6) ===

    # Approval matrix for this change request
    approval_matrix_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("approval_matrices.id"), nullable=True
    )

    # Current step in approval workflow (1-indexed, 0 = not started)
    current_approval_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Overall approval status
    # Values: "pending", "in_progress", "approved", "rejected"
    approval_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)

    # === DOCUMENT CONTROL METADATA ===

    # Whether this is a major revision (requires change reason)
    is_major_revision: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Reason for change (required for major revisions)
    change_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata for revision tracking (JSON)
    # Example: {"pending_revision": "B", "pending_major_version": 1, "pending_minor_version": 0}
    revision_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    page: Mapped["Page"] = relationship("Page", back_populates="change_requests")
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id])
    reviewer: Mapped["User | None"] = relationship("User", foreign_keys=[reviewer_id])
    published_by: Mapped["User | None"] = relationship(
        "User", foreign_keys=[published_by_id]
    )
    comments: Mapped[list["ChangeRequestComment"]] = relationship(
        "ChangeRequestComment", back_populates="change_request", cascade="all, delete-orphan"
    )

    # Approval workflow relationships
    approval_matrix: Mapped["ApprovalMatrix | None"] = relationship("ApprovalMatrix")
    approval_records: Mapped[list["ApprovalRecord"]] = relationship(
        "ApprovalRecord", back_populates="change_request", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ChangeRequest CR-{self.number}: {self.title}>"

    @property
    def is_approval_complete(self) -> bool:
        """Check if approval workflow is complete."""
        return self.approval_status in ("approved", "rejected")

    @property
    def pending_revision(self) -> str | None:
        """Get pending revision from revision_metadata."""
        if self.revision_metadata:
            return self.revision_metadata.get("pending_revision")
        return None

    @property
    def pending_version(self) -> str | None:
        """Get pending version string from revision_metadata."""
        if self.revision_metadata:
            major = self.revision_metadata.get("pending_major_version", 1)
            minor = self.revision_metadata.get("pending_minor_version", 0)
            return f"{major}.{minor}"
        return None


class ChangeRequestComment(Base, UUIDMixin, TimestampMixin):
    """Comments and discussion on a change request."""

    __tablename__ = "change_request_comments"

    # Parent change request
    change_request_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("change_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Author of comment
    author_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False
    )

    # Comment content (Markdown)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Optional: line-level comment for inline feedback
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Thread support - replies to other comments
    parent_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("change_request_comments.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Relationships
    change_request: Mapped["ChangeRequest"] = relationship(
        "ChangeRequest", back_populates="comments"
    )
    author: Mapped["User"] = relationship("User")
    parent: Mapped["ChangeRequestComment | None"] = relationship(
        "ChangeRequestComment", remote_side="ChangeRequestComment.id", back_populates="replies"
    )
    replies: Mapped[list["ChangeRequestComment"]] = relationship(
        "ChangeRequestComment", back_populates="parent"
    )

    def __repr__(self) -> str:
        return f"<ChangeRequestComment {self.id[:8]}>"
