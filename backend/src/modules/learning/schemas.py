"""Pydantic schemas for learning module.

Sprint 9: Learning Module Basics
Compliance: ISO 9001 training records, ISO 13485 competency verification
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# =============================================================================
# ENUMS
# =============================================================================

class QuestionType(str, Enum):
    """Types of assessment questions."""

    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"


class AssignmentStatus(str, Enum):
    """Status of a learning assignment."""

    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class AttemptStatus(str, Enum):
    """Status of a quiz attempt."""

    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    PASSED = "passed"
    FAILED = "failed"
    ABANDONED = "abandoned"


# =============================================================================
# QUESTION SCHEMAS
# =============================================================================

class MultipleChoiceOption(BaseModel):
    """Option for a multiple choice question."""

    id: str = Field(..., description="Option identifier (e.g., 'a', 'b', 'c')")
    text: str = Field(..., min_length=1, description="Option text")
    is_correct: bool = Field(default=False, description="Whether this is the correct answer")


class QuestionBase(BaseModel):
    """Base question schema."""

    question_type: QuestionType = Field(default=QuestionType.MULTIPLE_CHOICE)
    question_text: str = Field(..., min_length=1, description="The question text")
    options: Optional[List[MultipleChoiceOption]] = Field(
        None, description="Options for multiple choice questions"
    )
    correct_answer: Optional[str] = Field(
        None, description="Correct answer for true/false or fill-in-blank"
    )
    points: int = Field(default=1, ge=1, description="Points for this question")
    explanation: Optional[str] = Field(None, description="Explanation shown after answering")
    sort_order: int = Field(default=0, description="Order within assessment")


class QuestionCreate(QuestionBase):
    """Create question schema."""

    pass


class QuestionUpdate(BaseModel):
    """Update question schema."""

    question_type: Optional[QuestionType] = None
    question_text: Optional[str] = Field(None, min_length=1)
    options: Optional[List[MultipleChoiceOption]] = None
    correct_answer: Optional[str] = None
    points: Optional[int] = Field(None, ge=1)
    explanation: Optional[str] = None
    sort_order: Optional[int] = None


class QuestionResponse(QuestionBase):
    """Question response schema."""

    id: str
    assessment_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionPublic(BaseModel):
    """Public question schema (without correct answers - for quiz taking)."""

    id: str
    question_type: QuestionType
    question_text: str
    options: Optional[List[dict]] = Field(
        None, description="Options without is_correct flag"
    )
    points: int
    sort_order: int

    class Config:
        from_attributes = True


# =============================================================================
# ASSESSMENT SCHEMAS
# =============================================================================

class AssessmentBase(BaseModel):
    """Base assessment schema."""

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    passing_score: int = Field(default=80, ge=0, le=100, description="Passing percentage")
    max_attempts: Optional[int] = Field(None, ge=1, description="Max attempts (null = unlimited)")
    time_limit_minutes: Optional[int] = Field(None, ge=1, description="Time limit in minutes")


class AssessmentCreate(AssessmentBase):
    """Create assessment schema."""

    page_id: str = Field(..., description="Page this assessment is for")


class AssessmentUpdate(BaseModel):
    """Update assessment schema."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    passing_score: Optional[int] = Field(None, ge=0, le=100)
    max_attempts: Optional[int] = Field(None, ge=1)
    time_limit_minutes: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class AssessmentResponse(AssessmentBase):
    """Assessment response schema."""

    id: str
    page_id: str
    is_active: bool
    created_by_id: Optional[str]
    question_count: int
    total_points: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssessmentWithQuestions(AssessmentResponse):
    """Assessment with questions."""

    questions: List[QuestionResponse]


class AssessmentPublic(BaseModel):
    """Public assessment info for quiz taking (without answers)."""

    id: str
    title: str
    description: Optional[str]
    passing_score: int
    max_attempts: Optional[int]
    time_limit_minutes: Optional[int]
    question_count: int
    total_points: int
    questions: List[QuestionPublic]

    class Config:
        from_attributes = True


# =============================================================================
# ASSIGNMENT SCHEMAS
# =============================================================================

class AssignmentBase(BaseModel):
    """Base assignment schema."""

    page_id: str = Field(..., description="Page to assign")
    due_date: Optional[datetime] = Field(None, description="Due date for completion")
    notes: Optional[str] = Field(None, description="Notes about the assignment")


class AssignmentCreate(AssignmentBase):
    """Create assignment schema."""

    user_id: str = Field(..., description="User to assign to")


class AssignmentBulkCreate(BaseModel):
    """Bulk create assignments schema."""

    page_id: str = Field(..., description="Page to assign")
    user_ids: List[str] = Field(..., min_length=1, description="Users to assign to")
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class AssignmentUpdate(BaseModel):
    """Update assignment schema."""

    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class AssignmentResponse(BaseModel):
    """Assignment response schema."""

    id: str
    page_id: str
    page_title: Optional[str] = None
    user_id: str
    user_email: Optional[str] = None
    assigned_by_id: Optional[str]
    status: AssignmentStatus
    due_date: Optional[datetime]
    assigned_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    notes: Optional[str]
    is_overdue: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssignmentListResponse(BaseModel):
    """List of assignments response."""

    assignments: List[AssignmentResponse]
    total: int
    has_more: bool


# =============================================================================
# QUIZ ATTEMPT SCHEMAS
# =============================================================================

class StartAttemptRequest(BaseModel):
    """Request to start a quiz attempt."""

    assignment_id: Optional[str] = Field(None, description="Optional linked assignment")


class StartAttemptResponse(BaseModel):
    """Response when starting a quiz attempt."""

    attempt_id: str
    assessment: AssessmentPublic
    attempt_number: int
    started_at: datetime
    time_remaining_seconds: Optional[int] = None
    existing_answers: dict = Field(default_factory=dict)


class SaveAnswerRequest(BaseModel):
    """Request to save an answer."""

    question_id: str
    answer: str


class SubmitAttemptRequest(BaseModel):
    """Request to submit a quiz attempt."""

    pass  # No additional data needed


class AttemptResponse(BaseModel):
    """Quiz attempt response."""

    id: str
    assessment_id: str
    user_id: str
    assignment_id: Optional[str]
    status: AttemptStatus
    score: Optional[float]
    answers: dict
    started_at: datetime
    submitted_at: Optional[datetime]
    time_spent_seconds: Optional[int]
    attempt_number: int
    earned_points: Optional[int]
    total_points: Optional[int]
    passing_score: Optional[int]
    passed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GradeResult(BaseModel):
    """Result of grading an attempt."""

    score: float
    passed: bool
    earned_points: int
    total_points: int
    passing_score: int
    question_results: List[dict] = Field(
        default_factory=list,
        description="Results per question"
    )


# =============================================================================
# ACKNOWLEDGMENT SCHEMAS
# =============================================================================

class InitiateAcknowledgmentRequest(BaseModel):
    """Request to initiate an acknowledgment."""

    quiz_attempt_id: Optional[str] = Field(
        None, description="Quiz attempt (required if page has assessment)"
    )
    assignment_id: Optional[str] = Field(None, description="Optional linked assignment")


class InitiateAcknowledgmentResponse(BaseModel):
    """Response when initiating acknowledgment."""

    challenge_token: str
    expires_at: datetime
    content_hash: str
    document_title: str
    requires_quiz: bool
    quiz_passed: Optional[bool] = None


class CompleteAcknowledgmentRequest(BaseModel):
    """Request to complete acknowledgment with password."""

    challenge_token: str
    password: str


class AcknowledgmentResponse(BaseModel):
    """Acknowledgment response."""

    id: str
    page_id: str
    page_title: Optional[str] = None
    user_id: str
    assignment_id: Optional[str]
    quiz_attempt_id: Optional[str]
    signature_id: str
    acknowledged_at: datetime
    valid_until: Optional[datetime]
    is_valid: bool
    is_expired: bool
    invalidated_at: Optional[datetime]
    invalidation_reason: Optional[str]
    page_version: Optional[str]
    content_hash: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AcknowledgmentStatus(BaseModel):
    """Status of user's acknowledgment for a page."""

    page_id: str
    has_valid_acknowledgment: bool
    acknowledgment: Optional[AcknowledgmentResponse] = None
    requires_training: bool
    has_assessment: bool
    has_passed_quiz: bool
    can_acknowledge: bool
    reason: Optional[str] = None


# =============================================================================
# REPORTING SCHEMAS
# =============================================================================

class CompletionReportItem(BaseModel):
    """Item in completion report."""

    page_id: str
    page_title: str
    total_assigned: int
    completed: int
    in_progress: int
    overdue: int
    completion_rate: float


class UserTrainingHistory(BaseModel):
    """User's training history."""

    user_id: str
    user_email: str
    user_name: str
    total_assignments: int
    completed: int
    in_progress: int
    overdue: int
    acknowledgments: List[AcknowledgmentResponse]


class PageTrainingReport(BaseModel):
    """Training report for a page."""

    page_id: str
    page_title: str
    requires_training: bool
    has_assessment: bool
    assessment_id: Optional[str]
    total_assigned: int
    completed: int
    completion_rate: float
    assignments: List[AssignmentResponse]


class OverdueReport(BaseModel):
    """Report of overdue assignments."""

    total_overdue: int
    assignments: List[AssignmentResponse]


class ReportExportRequest(BaseModel):
    """Request to export a report."""

    report_type: str = Field(..., description="completion, overdue, user, page")
    format: str = Field(default="csv", description="csv or json")
    page_id: Optional[str] = None
    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
