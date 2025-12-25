"""Learning Assignment model.

Tracks document training assignments to users.

Sprint 9: Learning Module Basics
Compliance: ISO 9001 training records, ISO 13485 competency tracking
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.page import Page
    from src.db.models.user import User


class AssignmentStatus(str, Enum):
    """Status of a learning assignment."""

    ASSIGNED = "assigned"      # Assigned but not started
    IN_PROGRESS = "in_progress"  # User has started reading/quiz
    COMPLETED = "completed"    # Successfully completed and acknowledged
    OVERDUE = "overdue"        # Past due date without completion
    CANCELLED = "cancelled"    # Assignment was cancelled


class LearningAssignment(Base, UUIDMixin, TimestampMixin):
    """Assignment of a document for training to a specific user.

    Tracks the lifecycle of a training assignment from assignment
    through completion. Used for compliance tracking and reporting.

    Attributes:
        page_id: Document assigned for training
        user_id: User who must complete the training
        assigned_by_id: User/admin who created the assignment
        status: Current status of the assignment
        due_date: Optional deadline for completion
        assigned_at: When the assignment was created
        started_at: When user first started the training
        completed_at: When training was successfully completed
        reminder_sent_at: When last reminder was sent
        notes: Optional notes about the assignment
    """

    __tablename__ = "learning_assignments"

    # Core assignment info
    page_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_by_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(50),
        default=AssignmentStatus.ASSIGNED.value,
        nullable=False,
        index=True,
    )

    # Dates
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    reminder_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Optional notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    page: Mapped["Page"] = relationship("Page", foreign_keys=[page_id])
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    assigned_by: Mapped["User"] = relationship("User", foreign_keys=[assigned_by_id])

    # Composite index for common queries
    __table_args__ = (
        Index("ix_learning_assignments_user_status", "user_id", "status"),
        Index("ix_learning_assignments_page_status", "page_id", "status"),
    )

    @property
    def status_enum(self) -> AssignmentStatus:
        """Get status as enum."""
        return AssignmentStatus(self.status)

    @property
    def is_overdue(self) -> bool:
        """Check if assignment is overdue."""
        if self.status == AssignmentStatus.COMPLETED.value:
            return False
        if self.due_date is None:
            return False
        return datetime.now(self.due_date.tzinfo) > self.due_date

    def mark_started(self) -> None:
        """Mark assignment as started."""
        if self.started_at is None:
            self.started_at = datetime.utcnow()
        if self.status == AssignmentStatus.ASSIGNED.value:
            self.status = AssignmentStatus.IN_PROGRESS.value

    def mark_completed(self) -> None:
        """Mark assignment as completed."""
        self.completed_at = datetime.utcnow()
        self.status = AssignmentStatus.COMPLETED.value

    def mark_overdue(self) -> None:
        """Mark assignment as overdue."""
        if self.status not in (
            AssignmentStatus.COMPLETED.value,
            AssignmentStatus.CANCELLED.value,
        ):
            self.status = AssignmentStatus.OVERDUE.value

    def cancel(self) -> None:
        """Cancel the assignment."""
        self.status = AssignmentStatus.CANCELLED.value
