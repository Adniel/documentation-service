"""Learning service - core CRUD operations.

Sprint 9: Learning Module Basics
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.assessment import Assessment, AssessmentQuestion
from src.db.models.learning_assignment import LearningAssignment, AssignmentStatus
from src.db.models.quiz_attempt import QuizAttempt, AttemptStatus
from src.db.models.page import Page
from src.db.models.user import User
from src.modules.learning.schemas import (
    AssessmentCreate,
    AssessmentUpdate,
    QuestionCreate,
    QuestionUpdate,
    AssignmentCreate,
    AssignmentBulkCreate,
    AssignmentUpdate,
    StartAttemptRequest,
    SaveAnswerRequest,
    QuestionPublic,
    AssessmentPublic,
)
from src.modules.learning.grading_service import grade_attempt, update_attempt_with_grade


# =============================================================================
# ASSESSMENT OPERATIONS
# =============================================================================

async def create_assessment(
    db: AsyncSession,
    assessment_in: AssessmentCreate,
    created_by_id: str,
) -> Assessment:
    """Create a new assessment for a page."""
    assessment = Assessment(
        id=str(uuid4()),
        page_id=assessment_in.page_id,
        title=assessment_in.title,
        description=assessment_in.description,
        passing_score=assessment_in.passing_score,
        max_attempts=assessment_in.max_attempts,
        time_limit_minutes=assessment_in.time_limit_minutes,
        created_by_id=created_by_id,
    )
    db.add(assessment)
    await db.flush()

    # Fetch with questions eagerly loaded to avoid lazy loading issues
    result = await db.execute(
        select(Assessment)
        .where(Assessment.id == assessment.id)
        .options(selectinload(Assessment.questions))
    )
    return result.scalar_one()


async def get_assessment(
    db: AsyncSession,
    assessment_id: str,
) -> Optional[Assessment]:
    """Get an assessment by ID with questions."""
    result = await db.execute(
        select(Assessment)
        .where(Assessment.id == assessment_id)
        .options(selectinload(Assessment.questions))
    )
    return result.scalar_one_or_none()


async def get_assessment_for_page(
    db: AsyncSession,
    page_id: str,
) -> Optional[Assessment]:
    """Get the assessment for a page (if any)."""
    result = await db.execute(
        select(Assessment)
        .where(Assessment.page_id == page_id)
        .where(Assessment.is_active == True)
        .options(selectinload(Assessment.questions))
    )
    return result.scalar_one_or_none()


async def update_assessment(
    db: AsyncSession,
    assessment: Assessment,
    assessment_in: AssessmentUpdate,
) -> Assessment:
    """Update an assessment."""
    update_data = assessment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assessment, field, value)
    await db.flush()

    # Fetch with questions eagerly loaded
    result = await db.execute(
        select(Assessment)
        .where(Assessment.id == assessment.id)
        .options(selectinload(Assessment.questions))
    )
    return result.scalar_one()


async def delete_assessment(db: AsyncSession, assessment: Assessment) -> None:
    """Delete an assessment."""
    await db.delete(assessment)
    await db.flush()


# =============================================================================
# QUESTION OPERATIONS
# =============================================================================

async def add_question(
    db: AsyncSession,
    assessment_id: str,
    question_in: QuestionCreate,
) -> AssessmentQuestion:
    """Add a question to an assessment."""
    # Get max sort_order
    result = await db.execute(
        select(func.max(AssessmentQuestion.sort_order))
        .where(AssessmentQuestion.assessment_id == assessment_id)
    )
    max_order = result.scalar() or 0

    question = AssessmentQuestion(
        id=str(uuid4()),
        assessment_id=assessment_id,
        question_type=question_in.question_type.value,
        question_text=question_in.question_text,
        options=[opt.model_dump() for opt in question_in.options] if question_in.options else None,
        correct_answer=question_in.correct_answer,
        points=question_in.points,
        explanation=question_in.explanation,
        sort_order=question_in.sort_order if question_in.sort_order > 0 else max_order + 1,
    )
    db.add(question)
    await db.flush()
    await db.refresh(question)
    return question


async def get_question(
    db: AsyncSession,
    question_id: str,
) -> Optional[AssessmentQuestion]:
    """Get a question by ID."""
    result = await db.execute(
        select(AssessmentQuestion).where(AssessmentQuestion.id == question_id)
    )
    return result.scalar_one_or_none()


async def update_question(
    db: AsyncSession,
    question: AssessmentQuestion,
    question_in: QuestionUpdate,
) -> AssessmentQuestion:
    """Update a question."""
    update_data = question_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "question_type" and value:
            value = value.value
        if field == "options" and value:
            value = [opt.model_dump() if hasattr(opt, "model_dump") else opt for opt in value]
        setattr(question, field, value)
    await db.flush()
    await db.refresh(question)
    return question


async def delete_question(db: AsyncSession, question: AssessmentQuestion) -> None:
    """Delete a question."""
    await db.delete(question)
    await db.flush()


async def reorder_questions(
    db: AsyncSession,
    assessment_id: str,
    question_ids: List[str],
) -> List[AssessmentQuestion]:
    """Reorder questions by providing ordered list of IDs."""
    result = await db.execute(
        select(AssessmentQuestion)
        .where(AssessmentQuestion.assessment_id == assessment_id)
    )
    questions = {q.id: q for q in result.scalars().all()}

    for order, qid in enumerate(question_ids):
        if qid in questions:
            questions[qid].sort_order = order

    await db.flush()

    # Return in new order
    return [questions[qid] for qid in question_ids if qid in questions]


# =============================================================================
# ASSIGNMENT OPERATIONS
# =============================================================================

async def create_assignment(
    db: AsyncSession,
    assignment_in: AssignmentCreate,
    assigned_by_id: str,
) -> LearningAssignment:
    """Create a learning assignment."""
    assignment = LearningAssignment(
        id=str(uuid4()),
        page_id=assignment_in.page_id,
        user_id=assignment_in.user_id,
        assigned_by_id=assigned_by_id,
        due_date=assignment_in.due_date,
        notes=assignment_in.notes,
        assigned_at=datetime.now(timezone.utc),
    )
    db.add(assignment)
    await db.flush()
    await db.refresh(assignment)
    return assignment


async def create_bulk_assignments(
    db: AsyncSession,
    bulk_in: AssignmentBulkCreate,
    assigned_by_id: str,
) -> List[LearningAssignment]:
    """Create multiple assignments for different users."""
    assignments = []
    now = datetime.now(timezone.utc)

    for user_id in bulk_in.user_ids:
        assignment = LearningAssignment(
            id=str(uuid4()),
            page_id=bulk_in.page_id,
            user_id=user_id,
            assigned_by_id=assigned_by_id,
            due_date=bulk_in.due_date,
            notes=bulk_in.notes,
            assigned_at=now,
        )
        db.add(assignment)
        assignments.append(assignment)

    await db.flush()
    for a in assignments:
        await db.refresh(a)

    return assignments


async def get_assignment(
    db: AsyncSession,
    assignment_id: str,
) -> Optional[LearningAssignment]:
    """Get an assignment by ID."""
    result = await db.execute(
        select(LearningAssignment)
        .where(LearningAssignment.id == assignment_id)
        .options(
            selectinload(LearningAssignment.page),
            selectinload(LearningAssignment.user),
        )
    )
    return result.scalar_one_or_none()


async def list_assignments(
    db: AsyncSession,
    user_id: Optional[str] = None,
    page_id: Optional[str] = None,
    status: Optional[AssignmentStatus] = None,
    limit: int = 100,
    offset: int = 0,
) -> Tuple[List[LearningAssignment], int]:
    """List assignments with filters."""
    query = select(LearningAssignment).options(
        selectinload(LearningAssignment.page),
        selectinload(LearningAssignment.user),
    )

    conditions = []
    if user_id:
        conditions.append(LearningAssignment.user_id == user_id)
    if page_id:
        conditions.append(LearningAssignment.page_id == page_id)
    if status:
        conditions.append(LearningAssignment.status == status.value)

    if conditions:
        query = query.where(and_(*conditions))

    # Get total count
    count_query = select(func.count()).select_from(LearningAssignment)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(LearningAssignment.due_date.asc().nullslast())
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    assignments = list(result.scalars().all())

    return assignments, total


async def update_assignment(
    db: AsyncSession,
    assignment: LearningAssignment,
    assignment_in: AssignmentUpdate,
) -> LearningAssignment:
    """Update an assignment."""
    update_data = assignment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assignment, field, value)
    await db.flush()
    await db.refresh(assignment)
    return assignment


async def cancel_assignment(
    db: AsyncSession,
    assignment: LearningAssignment,
) -> LearningAssignment:
    """Cancel an assignment."""
    assignment.cancel()
    await db.flush()
    await db.refresh(assignment)
    return assignment


async def get_my_assignments(
    db: AsyncSession,
    user_id: str,
    include_completed: bool = False,
) -> List[LearningAssignment]:
    """Get assignments for a user."""
    query = (
        select(LearningAssignment)
        .where(LearningAssignment.user_id == user_id)
        .options(selectinload(LearningAssignment.page))
    )

    if not include_completed:
        query = query.where(
            LearningAssignment.status.not_in([
                AssignmentStatus.COMPLETED.value,
                AssignmentStatus.CANCELLED.value,
            ])
        )

    query = query.order_by(LearningAssignment.due_date.asc().nullslast())

    result = await db.execute(query)
    return list(result.scalars().all())


# =============================================================================
# QUIZ ATTEMPT OPERATIONS
# =============================================================================

async def start_attempt(
    db: AsyncSession,
    assessment_id: str,
    user_id: str,
    assignment_id: Optional[str] = None,
) -> QuizAttempt:
    """Start a new quiz attempt."""
    # Get attempt count for this user/assessment
    count_result = await db.execute(
        select(func.count())
        .select_from(QuizAttempt)
        .where(
            QuizAttempt.assessment_id == assessment_id,
            QuizAttempt.user_id == user_id,
        )
    )
    attempt_count = count_result.scalar() or 0

    attempt = QuizAttempt(
        id=str(uuid4()),
        assessment_id=assessment_id,
        user_id=user_id,
        assignment_id=assignment_id,
        status=AttemptStatus.IN_PROGRESS.value,
        started_at=datetime.now(timezone.utc),
        attempt_number=attempt_count + 1,
        answers={},
    )
    db.add(attempt)

    # Mark assignment as in progress if linked
    if assignment_id:
        assignment_result = await db.execute(
            select(LearningAssignment)
            .where(LearningAssignment.id == assignment_id)
        )
        assignment = assignment_result.scalar_one_or_none()
        if assignment:
            assignment.mark_started()

    await db.flush()
    await db.refresh(attempt)
    return attempt


async def get_attempt(
    db: AsyncSession,
    attempt_id: str,
) -> Optional[QuizAttempt]:
    """Get a quiz attempt by ID."""
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.id == attempt_id)
        .options(selectinload(QuizAttempt.assessment))
    )
    return result.scalar_one_or_none()


async def get_in_progress_attempt(
    db: AsyncSession,
    assessment_id: str,
    user_id: str,
) -> Optional[QuizAttempt]:
    """Get an in-progress attempt for a user/assessment."""
    result = await db.execute(
        select(QuizAttempt)
        .where(
            QuizAttempt.assessment_id == assessment_id,
            QuizAttempt.user_id == user_id,
            QuizAttempt.status == AttemptStatus.IN_PROGRESS.value,
        )
    )
    return result.scalar_one_or_none()


async def save_answer(
    db: AsyncSession,
    attempt: QuizAttempt,
    question_id: str,
    answer: str,
) -> QuizAttempt:
    """Save an answer for a question."""
    attempt.set_answer(question_id, answer)
    await db.flush()
    await db.refresh(attempt)
    return attempt


async def submit_attempt(
    db: AsyncSession,
    attempt: QuizAttempt,
) -> QuizAttempt:
    """Submit and grade a quiz attempt."""
    # Get assessment with questions
    assessment_result = await db.execute(
        select(Assessment)
        .where(Assessment.id == attempt.assessment_id)
        .options(selectinload(Assessment.questions))
    )
    assessment = assessment_result.scalar_one()

    # Grade the attempt
    grade_result = grade_attempt(
        attempt,
        assessment.questions,
        assessment.passing_score,
    )

    # Update attempt with grade
    update_attempt_with_grade(attempt, grade_result)
    attempt.submitted_at = datetime.now(timezone.utc)
    attempt.time_spent_seconds = attempt.calculate_time_spent()

    await db.flush()
    await db.refresh(attempt)

    return attempt


async def get_user_attempts(
    db: AsyncSession,
    user_id: str,
    assessment_id: Optional[str] = None,
) -> List[QuizAttempt]:
    """Get all attempts for a user."""
    query = select(QuizAttempt).where(QuizAttempt.user_id == user_id)

    if assessment_id:
        query = query.where(QuizAttempt.assessment_id == assessment_id)

    query = query.order_by(QuizAttempt.started_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_passing_attempt(
    db: AsyncSession,
    assessment_id: str,
    user_id: str,
) -> Optional[QuizAttempt]:
    """Get a passing attempt for a user/assessment if any."""
    result = await db.execute(
        select(QuizAttempt)
        .where(
            QuizAttempt.assessment_id == assessment_id,
            QuizAttempt.user_id == user_id,
            QuizAttempt.status == AttemptStatus.PASSED.value,
        )
        .order_by(QuizAttempt.submitted_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def prepare_assessment_for_quiz(assessment: Assessment) -> AssessmentPublic:
    """Prepare assessment for quiz taking (hide answers)."""
    public_questions = []
    for q in sorted(assessment.questions, key=lambda x: x.sort_order):
        # Remove is_correct from options
        options = None
        if q.options:
            options = [{"id": opt["id"], "text": opt["text"]} for opt in q.options]

        public_questions.append(QuestionPublic(
            id=str(q.id),
            question_type=q.question_type,
            question_text=q.question_text,
            options=options,
            points=q.points,
            sort_order=q.sort_order,
        ))

    return AssessmentPublic(
        id=str(assessment.id),
        title=assessment.title,
        description=assessment.description,
        passing_score=assessment.passing_score,
        max_attempts=assessment.max_attempts,
        time_limit_minutes=assessment.time_limit_minutes,
        question_count=len(assessment.questions),
        total_points=sum(q.points for q in assessment.questions),
        questions=public_questions,
    )
