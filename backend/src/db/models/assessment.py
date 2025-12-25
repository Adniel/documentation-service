"""Assessment model for learning module.

Implements assessments (quizzes) linked to documents for training verification.

Sprint 9: Learning Module Basics
Compliance: ISO 9001 training records, ISO 13485 competency verification
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.page import Page
    from src.db.models.user import User


class QuestionType(str, Enum):
    """Types of assessment questions."""

    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"


class Assessment(Base, UUIDMixin, TimestampMixin):
    """Assessment (quiz) linked to a document.

    Assessments contain questions that users must answer to demonstrate
    understanding of document content. Used for training verification
    and compliance with ISO 9001/13485 training requirements.

    Attributes:
        page_id: Document this assessment is for
        title: Assessment title (defaults to page title + "Assessment")
        description: Optional description/instructions
        passing_score: Minimum percentage to pass (default 80%)
        max_attempts: Maximum attempts allowed (null = unlimited)
        time_limit_minutes: Time limit per attempt (null = no limit)
        is_active: Whether assessment is currently active
        created_by_id: User who created the assessment
        questions: List of questions in this assessment
    """

    __tablename__ = "assessments"

    # Link to document
    page_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Assessment metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Scoring settings
    passing_score: Mapped[int] = mapped_column(Integer, default=80, nullable=False)

    # Attempt limits
    max_attempts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Authorship
    created_by_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    page: Mapped["Page"] = relationship("Page", back_populates="assessment")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    questions: Mapped[List["AssessmentQuestion"]] = relationship(
        "AssessmentQuestion",
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by="AssessmentQuestion.sort_order",
    )

    @property
    def question_count(self) -> int:
        """Get total number of questions."""
        return len(self.questions) if self.questions else 0

    @property
    def total_points(self) -> int:
        """Get total possible points."""
        return sum(q.points for q in self.questions) if self.questions else 0


class AssessmentQuestion(Base, UUIDMixin, TimestampMixin):
    """Individual question within an assessment.

    Supports multiple question types:
    - Multiple choice: User selects one correct answer from options
    - True/False: User selects true or false
    - Fill in the blank: User types the correct answer

    Attributes:
        assessment_id: Parent assessment
        question_type: Type of question (multiple_choice, true_false, fill_blank)
        question_text: The question to ask
        options: For MC - list of options with id, text, is_correct
        correct_answer: For T/F and fill_blank - the correct answer
        points: Points awarded for correct answer (default 1)
        explanation: Explanation shown after answering
        sort_order: Order within assessment
    """

    __tablename__ = "assessment_questions"

    # Parent assessment
    assessment_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Question content
    question_type: Mapped[str] = mapped_column(
        String(50),
        default=QuestionType.MULTIPLE_CHOICE.value,
        nullable=False,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Answer options (for multiple choice)
    # Format: [{"id": "a", "text": "Option text", "is_correct": true/false}, ...]
    options: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Correct answer (for true_false and fill_blank)
    # For true_false: "true" or "false"
    # For fill_blank: the correct text (case-insensitive matching)
    correct_answer: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Scoring
    points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Feedback
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Ordering
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    assessment: Mapped["Assessment"] = relationship(
        "Assessment", back_populates="questions"
    )

    @property
    def question_type_enum(self) -> QuestionType:
        """Get question type as enum."""
        return QuestionType(self.question_type)

    def is_answer_correct(self, user_answer: str | None) -> bool:
        """Check if the user's answer is correct.

        Args:
            user_answer: The user's submitted answer

        Returns:
            True if answer is correct, False otherwise
        """
        if user_answer is None:
            return False

        if self.question_type == QuestionType.MULTIPLE_CHOICE.value:
            # Check if selected option is correct
            if not self.options:
                return False
            for option in self.options:
                if option.get("id") == user_answer:
                    return option.get("is_correct", False)
            return False

        elif self.question_type == QuestionType.TRUE_FALSE.value:
            # Case-insensitive comparison
            return user_answer.lower() == (self.correct_answer or "").lower()

        elif self.question_type == QuestionType.FILL_BLANK.value:
            # Case-insensitive, whitespace-trimmed comparison
            user_clean = user_answer.strip().lower()
            correct_clean = (self.correct_answer or "").strip().lower()
            return user_clean == correct_clean

        return False
