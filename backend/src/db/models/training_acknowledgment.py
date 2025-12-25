"""Training Acknowledgment model.

Records user acknowledgments of training completion with electronic signatures.

Sprint 9: Learning Module Basics
Compliance: ISO 9001 training records, 21 CFR Part 11 electronic signatures
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.electronic_signature import ElectronicSignature
    from src.db.models.learning_assignment import LearningAssignment
    from src.db.models.page import Page
    from src.db.models.quiz_attempt import QuizAttempt
    from src.db.models.user import User


class TrainingAcknowledgment(Base, UUIDMixin, TimestampMixin):
    """Record of a user acknowledging completion of document training.

    This is the final step in the training workflow. After reading a document
    and (optionally) passing an assessment, the user signs an acknowledgment
    with their electronic signature to confirm they have read and understood
    the document.

    Acknowledgments are linked to electronic signatures for 21 CFR Part 11
    compliance. They have a validity period based on the document's
    training_validity_months setting.

    Attributes:
        page_id: Document that was acknowledged
        user_id: User who made the acknowledgment
        assignment_id: Optional linked assignment
        quiz_attempt_id: Optional linked quiz attempt (if assessment required)
        signature_id: Electronic signature for this acknowledgment
        acknowledged_at: When acknowledgment was made
        valid_until: When acknowledgment expires (null = never)
        is_valid: Whether acknowledgment is currently valid
        invalidated_at: When acknowledgment was invalidated
        invalidation_reason: Why acknowledgment was invalidated
        page_version: Version of page at time of acknowledgment
        content_hash: Hash of page content at time of acknowledgment
    """

    __tablename__ = "training_acknowledgments"

    # Core references
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
    assignment_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("learning_assignments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    quiz_attempt_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("quiz_attempts.id", ondelete="SET NULL"),
        nullable=True,
    )
    signature_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("electronic_signatures.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )

    # Timing
    acknowledged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    valid_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # Validity tracking
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    invalidated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    invalidation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Document version at acknowledgment time (for audit trail)
    page_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Relationships
    page: Mapped["Page"] = relationship("Page", foreign_keys=[page_id])
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    assignment: Mapped["LearningAssignment"] = relationship(
        "LearningAssignment",
        foreign_keys=[assignment_id],
    )
    quiz_attempt: Mapped["QuizAttempt"] = relationship(
        "QuizAttempt",
        foreign_keys=[quiz_attempt_id],
    )
    signature: Mapped["ElectronicSignature"] = relationship(
        "ElectronicSignature",
        foreign_keys=[signature_id],
    )

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_training_ack_user_page", "user_id", "page_id"),
        Index("ix_training_ack_valid_user", "is_valid", "user_id"),
    )

    @property
    def is_expired(self) -> bool:
        """Check if acknowledgment has expired based on valid_until."""
        if self.valid_until is None:
            return False
        return datetime.now(self.valid_until.tzinfo) > self.valid_until

    @property
    def is_currently_valid(self) -> bool:
        """Check if acknowledgment is currently valid (not invalidated and not expired)."""
        return self.is_valid and not self.is_expired

    def invalidate(self, reason: str) -> None:
        """Invalidate this acknowledgment.

        Args:
            reason: Why the acknowledgment is being invalidated
        """
        self.is_valid = False
        self.invalidated_at = datetime.utcnow()
        self.invalidation_reason = reason
