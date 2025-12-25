"""Quiz Attempt model.

Tracks user attempts at assessments.

Sprint 9: Learning Module Basics
Compliance: ISO 9001 training records
"""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.assessment import Assessment
    from src.db.models.learning_assignment import LearningAssignment
    from src.db.models.user import User


class AttemptStatus(str, Enum):
    """Status of a quiz attempt."""

    IN_PROGRESS = "in_progress"  # User is taking the quiz
    SUBMITTED = "submitted"      # Submitted, pending grading (for future manual review)
    PASSED = "passed"            # Graded and passed
    FAILED = "failed"            # Graded and failed
    ABANDONED = "abandoned"      # User abandoned the attempt


class QuizAttempt(Base, UUIDMixin, TimestampMixin):
    """A user's attempt at completing an assessment.

    Tracks answers, timing, and results for each attempt.
    Supports multiple attempts per user/assessment based on
    the assessment's max_attempts setting.

    Attributes:
        assessment_id: Assessment being attempted
        user_id: User taking the assessment
        assignment_id: Optional linked assignment
        status: Current status of the attempt
        score: Final score as percentage (0-100)
        answers: User's answers keyed by question ID
        started_at: When attempt was started
        submitted_at: When attempt was submitted
        time_spent_seconds: Total time spent on attempt
        attempt_number: Which attempt this is (1, 2, 3, etc.)
    """

    __tablename__ = "quiz_attempts"

    # Core references
    assessment_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("assessments.id", ondelete="CASCADE"),
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

    # Status and scoring
    status: Mapped[str] = mapped_column(
        String(50),
        default=AttemptStatus.IN_PROGRESS.value,
        nullable=False,
        index=True,
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Answers stored as JSON: {question_id: user_answer}
    answers: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Timing
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    time_spent_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Attempt tracking
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Grading details (for record keeping)
    earned_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passing_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    assignment: Mapped["LearningAssignment"] = relationship(
        "LearningAssignment",
        foreign_keys=[assignment_id],
    )

    # Composite index for finding user's attempts on an assessment
    __table_args__ = (
        Index("ix_quiz_attempts_user_assessment", "user_id", "assessment_id"),
    )

    @property
    def status_enum(self) -> AttemptStatus:
        """Get status as enum."""
        return AttemptStatus(self.status)

    @property
    def passed(self) -> bool:
        """Check if this attempt passed."""
        return self.status == AttemptStatus.PASSED.value

    @property
    def is_complete(self) -> bool:
        """Check if attempt is complete (submitted/passed/failed)."""
        return self.status in (
            AttemptStatus.SUBMITTED.value,
            AttemptStatus.PASSED.value,
            AttemptStatus.FAILED.value,
        )

    def set_answer(self, question_id: str, answer: str) -> None:
        """Set or update an answer for a question.

        Args:
            question_id: ID of the question
            answer: User's answer
        """
        from sqlalchemy.orm.attributes import flag_modified

        if self.answers is None:
            self.answers = {}
        self.answers[question_id] = answer
        # Mark the JSON column as modified so SQLAlchemy detects the change
        flag_modified(self, "answers")

    def get_answer(self, question_id: str) -> str | None:
        """Get user's answer for a question.

        Args:
            question_id: ID of the question

        Returns:
            User's answer or None if not answered
        """
        if self.answers is None:
            return None
        return self.answers.get(question_id)

    def calculate_time_spent(self) -> int:
        """Calculate time spent in seconds from started_at to now or submitted_at."""
        end_time = self.submitted_at or datetime.now(timezone.utc)
        if self.started_at:
            # Ensure both datetimes are timezone-aware for comparison
            started = self.started_at
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=timezone.utc)
            delta = end_time - started
            return int(delta.total_seconds())
        return 0
