"""Page model - the actual content documents.

Sprint 6: Added document control fields for ISO 9001/13485 compliance.

Compliance: ISO 9001 §7.5.2, ISO 13485 §4.2.4-5, ISO 15489
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.assessment import Assessment
    from src.db.models.change_request import ChangeRequest
    from src.db.models.retention_policy import RetentionPolicy
    from src.db.models.space import Space
    from src.db.models.user import User


class PageStatus(str, Enum):
    """Document lifecycle status."""

    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    EFFECTIVE = "effective"
    OBSOLETE = "obsolete"
    ARCHIVED = "archived"


class Page(Base, UUIDMixin, TimestampMixin):
    """Page - individual document with content blocks.

    Sprint 6 additions:
    - Document type and controlled document flag
    - Revision tracking (letter-based: A, B, C)
    - Major/minor version numbers
    - Approval and effective dates
    - Review scheduling (periodic review)
    - Ownership (owner/custodian)
    - Retention policy and disposition date
    - Supersession tracking
    - Change control (summary/reason)
    - Training requirements
    """

    __tablename__ = "pages"

    # === BASIC INFO ===
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), index=True, nullable=False)

    # === DOCUMENT IDENTIFICATION (ISO 13485 §4.2.4) ===
    document_number: Mapped[str | None] = mapped_column(
        String(100), unique=True, index=True, nullable=True
    )
    document_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_controlled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # === VERSION CONTROL ===
    # Legacy version field (kept for compatibility)
    version: Mapped[str] = mapped_column(String(50), default="1.0", nullable=False)

    # Revision letter (A, B, C... - major changes requiring re-approval)
    revision: Mapped[str] = mapped_column(String(20), default="A", nullable=False)

    # Version numbers (1.0, 1.1, 2.0 - minor/major within a revision)
    major_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    minor_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # === LIFECYCLE STATUS ===
    status: Mapped[str] = mapped_column(
        String(50), default=PageStatus.DRAFT.value, nullable=False, index=True
    )

    # Classification level (public, internal, confidential, restricted)
    classification: Mapped[str] = mapped_column(String(50), default="internal", nullable=False)

    # === CONTENT ===
    content: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # === GIT REFERENCE ===
    git_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    git_commit_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # === DATE TRACKING (ISO 9001 §7.5.2) ===
    # Approval
    approved_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    approved_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=True
    )

    # Effective date (when document becomes active)
    effective_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # === REVIEW SCHEDULING ===
    # How often to review (months, e.g., 12 = annual)
    review_cycle_months: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Next scheduled review
    next_review_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    # Last review tracking
    last_reviewed_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_reviewed_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=True
    )

    # === OWNERSHIP (ISO 13485 §4.2.4) ===
    owner_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=True
    )
    custodian_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=True
    )

    # === RETENTION (ISO 15489) ===
    retention_policy_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("retention_policies.id"), nullable=True
    )
    disposition_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # === SUPERSESSION (ISO 13485 §4.2.4) ===
    # Document this one supersedes (replaces)
    supersedes_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("pages.id"), nullable=True
    )
    # Document that superseded (replaced) this one
    superseded_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("pages.id"), nullable=True
    )

    # === CHANGE CONTROL (ISO 13485 §4.2.5) ===
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # === TRAINING REQUIREMENT ===
    requires_training: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    training_validity_months: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # === SETTINGS ===
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # === PARENT REFERENCES ===
    space_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("spaces.id"), nullable=False
    )
    author_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False
    )
    parent_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("pages.id"), nullable=True
    )

    # === RELATIONSHIPS ===
    space: Mapped["Space"] = relationship("Space", back_populates="pages")
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id])
    parent: Mapped["Page | None"] = relationship(
        "Page",
        remote_side="Page.id",
        back_populates="children",
        foreign_keys=[parent_id],
    )
    children: Mapped[list["Page"]] = relationship(
        "Page", back_populates="parent", foreign_keys=[parent_id]
    )
    change_requests: Mapped[list["ChangeRequest"]] = relationship(
        "ChangeRequest", back_populates="page", cascade="all, delete-orphan"
    )

    # Document control relationships
    approved_by: Mapped["User | None"] = relationship(
        "User", foreign_keys=[approved_by_id]
    )
    last_reviewed_by: Mapped["User | None"] = relationship(
        "User", foreign_keys=[last_reviewed_by_id]
    )
    owner: Mapped["User | None"] = relationship("User", foreign_keys=[owner_id])
    custodian: Mapped["User | None"] = relationship("User", foreign_keys=[custodian_id])
    retention_policy: Mapped["RetentionPolicy | None"] = relationship("RetentionPolicy")

    # Sprint 9: Learning module relationship
    assessment: Mapped["Assessment | None"] = relationship(
        "Assessment",
        back_populates="page",
        uselist=False,  # One assessment per page
        cascade="all, delete-orphan",
    )

    # Supersession relationships
    supersedes: Mapped["Page | None"] = relationship(
        "Page",
        foreign_keys=[supersedes_id],
        remote_side="Page.id",
    )
    superseded_by: Mapped["Page | None"] = relationship(
        "Page",
        foreign_keys=[superseded_by_id],
        remote_side="Page.id",
    )

    def __repr__(self) -> str:
        return f"<Page {self.title}>"

    @property
    def full_version(self) -> str:
        """Get full version string (e.g., 'Rev A v1.0')."""
        return f"Rev {self.revision} v{self.major_version}.{self.minor_version}"

    @property
    def is_review_overdue(self) -> bool:
        """Check if periodic review is overdue."""
        if not self.next_review_date:
            return False
        return datetime.now(self.next_review_date.tzinfo) > self.next_review_date

    @property
    def status_enum(self) -> PageStatus:
        """Get status as enum."""
        return PageStatus(self.status)
