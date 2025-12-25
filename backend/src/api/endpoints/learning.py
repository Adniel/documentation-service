"""Learning module API endpoints.

Sprint 9: Learning Module Basics
Compliance: ISO 9001 training records, ISO 13485 competency verification
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import DbSession, CurrentUser
from src.db.models.quiz_attempt import AttemptStatus
from src.db.models.learning_assignment import AssignmentStatus
from src.modules.learning import service
from src.modules.learning.schemas import (
    # Assessment schemas
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentResponse,
    AssessmentWithQuestions,
    # Question schemas
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    # Assignment schemas
    AssignmentCreate,
    AssignmentBulkCreate,
    AssignmentUpdate,
    AssignmentResponse,
    AssignmentListResponse,
    # Quiz attempt schemas
    StartAttemptRequest,
    StartAttemptResponse,
    SaveAnswerRequest,
    SubmitAttemptRequest,
    AttemptResponse,
    # Acknowledgment schemas
    InitiateAcknowledgmentRequest,
    InitiateAcknowledgmentResponse,
    CompleteAcknowledgmentRequest,
    AcknowledgmentResponse,
    AcknowledgmentStatus as AckStatus,
    # Reporting schemas
    CompletionReportItem,
    OverdueReport,
    UserTrainingHistory,
    PageTrainingReport,
    ReportExportRequest,
)
from src.modules.learning.acknowledgment_service import (
    AcknowledgmentService,
    AcknowledgmentError,
    QuizNotPassedError,
    AlreadyAcknowledgedError,
)
from src.modules.document_control.signature_service import SignatureError
from src.modules.audit.audit_service import AuditService

router = APIRouter(tags=["learning"])


# =============================================================================
# ASSESSMENT ENDPOINTS
# =============================================================================

@router.post("/assessments", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_in: AssessmentCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> AssessmentResponse:
    """Create a new assessment for a page.

    Requires Editor role on the page.
    """
    # Check if assessment already exists for page
    existing = await service.get_assessment_for_page(db, assessment_in.page_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Assessment already exists for this page",
        )

    assessment = await service.create_assessment(
        db, assessment_in, str(current_user.id)
    )

    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="learning.assessment_created",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="assessment",
        resource_id=assessment.id,
        resource_name=assessment.title,
        details={"page_id": assessment_in.page_id},
    )

    await db.commit()
    return AssessmentResponse.model_validate(assessment)


@router.get("/assessments/{assessment_id}", response_model=AssessmentWithQuestions)
async def get_assessment(
    assessment_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> AssessmentWithQuestions:
    """Get an assessment with all questions."""
    assessment = await service.get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return AssessmentWithQuestions.model_validate(assessment)


@router.get("/pages/{page_id}/assessment", response_model=AssessmentWithQuestions)
async def get_page_assessment(
    page_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> AssessmentWithQuestions:
    """Get the assessment for a page (if any)."""
    assessment = await service.get_assessment_for_page(db, page_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessment for this page")

    return AssessmentWithQuestions.model_validate(assessment)


@router.patch("/assessments/{assessment_id}", response_model=AssessmentResponse)
async def update_assessment(
    assessment_id: str,
    assessment_in: AssessmentUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> AssessmentResponse:
    """Update an assessment."""
    assessment = await service.get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    updated = await service.update_assessment(db, assessment, assessment_in)
    await db.commit()

    return AssessmentResponse.model_validate(updated)


@router.delete("/assessments/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment(
    assessment_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete an assessment."""
    assessment = await service.get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    await service.delete_assessment(db, assessment)
    await db.commit()


# =============================================================================
# QUESTION ENDPOINTS
# =============================================================================

@router.post(
    "/assessments/{assessment_id}/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_question(
    assessment_id: str,
    question_in: QuestionCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> QuestionResponse:
    """Add a question to an assessment."""
    assessment = await service.get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    question = await service.add_question(db, assessment_id, question_in)
    await db.commit()

    return QuestionResponse.model_validate(question)


@router.patch("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    question_in: QuestionUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> QuestionResponse:
    """Update a question."""
    question = await service.get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    updated = await service.update_question(db, question, question_in)
    await db.commit()

    return QuestionResponse.model_validate(updated)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a question."""
    question = await service.get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    await service.delete_question(db, question)
    await db.commit()


@router.put("/assessments/{assessment_id}/questions/order", response_model=List[QuestionResponse])
async def reorder_questions(
    assessment_id: str,
    question_ids: List[str],
    db: DbSession,
    current_user: CurrentUser,
) -> List[QuestionResponse]:
    """Reorder questions in an assessment."""
    questions = await service.reorder_questions(db, assessment_id, question_ids)
    await db.commit()

    return [QuestionResponse.model_validate(q) for q in questions]


# =============================================================================
# ASSIGNMENT ENDPOINTS
# =============================================================================

@router.post("/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_in: AssignmentCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> AssignmentResponse:
    """Create a learning assignment."""
    assignment = await service.create_assignment(
        db, assignment_in, str(current_user.id)
    )

    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="learning.assignment_created",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="assignment",
        resource_id=assignment.id,
        details={
            "page_id": assignment_in.page_id,
            "user_id": assignment_in.user_id,
            "due_date": assignment_in.due_date.isoformat() if assignment_in.due_date else None,
        },
    )

    await db.commit()
    return AssignmentResponse.model_validate(assignment)


@router.post("/assignments/bulk", response_model=List[AssignmentResponse], status_code=status.HTTP_201_CREATED)
async def create_bulk_assignments(
    bulk_in: AssignmentBulkCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> List[AssignmentResponse]:
    """Create multiple assignments for different users."""
    assignments = await service.create_bulk_assignments(
        db, bulk_in, str(current_user.id)
    )

    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="learning.assignments_bulk_created",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="page",
        resource_id=bulk_in.page_id,
        details={
            "user_count": len(bulk_in.user_ids),
            "user_ids": bulk_in.user_ids,
        },
    )

    await db.commit()
    return [AssignmentResponse.model_validate(a) for a in assignments]


@router.get("/assignments", response_model=AssignmentListResponse)
async def list_assignments(
    user_id: Optional[str] = Query(None),
    page_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: DbSession = None,
    current_user: CurrentUser = None,
) -> AssignmentListResponse:
    """List assignments with filters."""
    status_enum = AssignmentStatus(status) if status else None

    assignments, total = await service.list_assignments(
        db,
        user_id=user_id,
        page_id=page_id,
        status=status_enum,
        limit=limit,
        offset=offset,
    )

    return AssignmentListResponse(
        assignments=[AssignmentResponse.model_validate(a) for a in assignments],
        total=total,
        has_more=offset + len(assignments) < total,
    )


@router.get("/assignments/me", response_model=List[AssignmentResponse])
async def get_my_assignments(
    include_completed: bool = Query(False),
    db: DbSession = None,
    current_user: CurrentUser = None,
) -> List[AssignmentResponse]:
    """Get my assignments."""
    assignments = await service.get_my_assignments(
        db, str(current_user.id), include_completed
    )
    return [AssignmentResponse.model_validate(a) for a in assignments]


@router.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> AssignmentResponse:
    """Get an assignment by ID."""
    assignment = await service.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    return AssignmentResponse.model_validate(assignment)


@router.patch("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: str,
    assignment_in: AssignmentUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> AssignmentResponse:
    """Update an assignment (e.g., extend due date)."""
    assignment = await service.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    updated = await service.update_assignment(db, assignment, assignment_in)
    await db.commit()

    return AssignmentResponse.model_validate(updated)


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_assignment(
    assignment_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Cancel an assignment."""
    assignment = await service.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    await service.cancel_assignment(db, assignment)
    await db.commit()


# =============================================================================
# QUIZ ATTEMPT ENDPOINTS
# =============================================================================

@router.post("/assessments/{assessment_id}/start", response_model=StartAttemptResponse)
async def start_quiz(
    assessment_id: str,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
    body: StartAttemptRequest = None,
) -> StartAttemptResponse:
    """Start a quiz attempt."""
    # Get assessment
    assessment = await service.get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if not assessment.is_active:
        raise HTTPException(status_code=400, detail="Assessment is not active")

    # Check for existing in-progress attempt
    existing = await service.get_in_progress_attempt(db, assessment_id, str(current_user.id))
    if existing:
        # Return existing attempt
        assessment_public = service.prepare_assessment_for_quiz(assessment)
        time_remaining = None
        if assessment.time_limit_minutes:
            elapsed = (datetime.now(timezone.utc) - existing.started_at.replace(tzinfo=timezone.utc)).total_seconds()
            time_remaining = max(0, assessment.time_limit_minutes * 60 - int(elapsed))

        return StartAttemptResponse(
            attempt_id=str(existing.id),
            assessment=assessment_public,
            attempt_number=existing.attempt_number,
            started_at=existing.started_at,
            time_remaining_seconds=time_remaining,
            existing_answers=existing.answers or {},
        )

    # Check max attempts
    if assessment.max_attempts:
        attempts = await service.get_user_attempts(db, str(current_user.id), assessment_id)
        if len(attempts) >= assessment.max_attempts:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum attempts ({assessment.max_attempts}) reached",
            )

    # Create new attempt
    assignment_id = body.assignment_id if body else None
    attempt = await service.start_attempt(
        db, assessment_id, str(current_user.id), assignment_id
    )

    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="learning.quiz_started",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="assessment",
        resource_id=assessment_id,
        resource_name=assessment.title,
        details={
            "attempt_id": attempt.id,
            "attempt_number": attempt.attempt_number,
        },
    )

    await db.commit()

    assessment_public = service.prepare_assessment_for_quiz(assessment)
    time_remaining = assessment.time_limit_minutes * 60 if assessment.time_limit_minutes else None

    return StartAttemptResponse(
        attempt_id=str(attempt.id),
        assessment=assessment_public,
        attempt_number=attempt.attempt_number,
        started_at=attempt.started_at,
        time_remaining_seconds=time_remaining,
        existing_answers={},
    )


@router.get("/attempts/{attempt_id}", response_model=AttemptResponse)
async def get_attempt(
    attempt_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> AttemptResponse:
    """Get a quiz attempt."""
    attempt = await service.get_attempt(db, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    # Only owner can view their attempt
    if attempt.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your attempt")

    return AttemptResponse.model_validate(attempt)


@router.patch("/attempts/{attempt_id}/answer", response_model=AttemptResponse)
async def save_answer(
    attempt_id: str,
    answer_in: SaveAnswerRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> AttemptResponse:
    """Save an answer for a question (auto-save)."""
    attempt = await service.get_attempt(db, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your attempt")

    if attempt.status != AttemptStatus.IN_PROGRESS.value:
        raise HTTPException(status_code=400, detail="Attempt is not in progress")

    updated = await service.save_answer(
        db, attempt, answer_in.question_id, answer_in.answer
    )
    await db.commit()

    return AttemptResponse.model_validate(updated)


@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResponse)
async def submit_attempt(
    attempt_id: str,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> AttemptResponse:
    """Submit a quiz attempt for grading."""
    attempt = await service.get_attempt(db, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your attempt")

    if attempt.status != AttemptStatus.IN_PROGRESS.value:
        raise HTTPException(status_code=400, detail="Attempt already submitted")

    # Submit and grade
    graded = await service.submit_attempt(db, attempt)

    # Audit log
    audit = AuditService(db)
    event_type = "learning.quiz_passed" if graded.passed else "learning.quiz_failed"
    await audit.log_event(
        event_type=event_type,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="quiz_attempt",
        resource_id=attempt_id,
        details={
            "score": graded.score,
            "passed": graded.passed,
            "earned_points": graded.earned_points,
            "total_points": graded.total_points,
        },
    )

    await db.commit()

    return AttemptResponse.model_validate(graded)


# =============================================================================
# ACKNOWLEDGMENT ENDPOINTS
# =============================================================================

@router.get("/pages/{page_id}/acknowledgment", response_model=AckStatus)
async def get_acknowledgment_status(
    page_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> AckStatus:
    """Get acknowledgment status for a page."""
    ack_service = AcknowledgmentService(db)
    status = await ack_service.get_acknowledgment_status(current_user, page_id)
    return status


@router.post("/pages/{page_id}/acknowledge", response_model=InitiateAcknowledgmentResponse)
async def initiate_acknowledgment(
    page_id: str,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
    body: Optional[InitiateAcknowledgmentRequest] = None,
) -> InitiateAcknowledgmentResponse:
    """Initiate an acknowledgment (starts signature flow)."""
    ack_service = AcknowledgmentService(db)

    try:
        response = await ack_service.initiate_acknowledgment(
            user=current_user,
            page_id=page_id,
            quiz_attempt_id=body.quiz_attempt_id if body else None,
            assignment_id=body.assignment_id if body else None,
            ip_address=request.client.host if request.client else None,
        )
        await db.commit()
        return response

    except QuizNotPassedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AlreadyAcknowledgedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except AcknowledgmentError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/acknowledgments/complete", response_model=AcknowledgmentResponse)
async def complete_acknowledgment(
    body: CompleteAcknowledgmentRequest,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> AcknowledgmentResponse:
    """Complete an acknowledgment with password re-authentication."""
    ack_service = AcknowledgmentService(db)

    try:
        acknowledgment = await ack_service.complete_acknowledgment(
            user=current_user,
            challenge_token=body.challenge_token,
            password=body.password,
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent"),
        )
        await db.commit()
        return AcknowledgmentResponse.model_validate(acknowledgment)

    except SignatureError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/acknowledgments/me", response_model=List[AcknowledgmentResponse])
async def get_my_acknowledgments(
    valid_only: bool = Query(False),
    db: DbSession = None,
    current_user: CurrentUser = None,
) -> List[AcknowledgmentResponse]:
    """Get my acknowledgments."""
    ack_service = AcknowledgmentService(db)
    acknowledgments = await ack_service.get_user_acknowledgments(
        str(current_user.id), valid_only
    )
    return [AcknowledgmentResponse.model_validate(a) for a in acknowledgments]


# =============================================================================
# REPORTING ENDPOINTS
# =============================================================================

@router.get("/reports/completion", response_model=List[CompletionReportItem])
async def get_completion_report(
    page_id: Optional[str] = None,
    db: DbSession = None,
    current_user: CurrentUser = None,
    _admin=None,  # Would use Depends(require_admin) in production
) -> List[CompletionReportItem]:
    """Get completion report."""
    # This is a simplified implementation
    # In production, would aggregate from assignments

    from sqlalchemy import select, func, Integer, case, literal
    from src.db.models.learning_assignment import LearningAssignment
    from src.db.models.page import Page

    query = (
        select(
            LearningAssignment.page_id,
            Page.title,
            func.count(LearningAssignment.id).label("total"),
            func.sum(
                case(
                    (LearningAssignment.status == AssignmentStatus.COMPLETED.value, 1),
                    else_=0
                )
            ).label("completed"),
            func.sum(
                case(
                    (LearningAssignment.status == AssignmentStatus.IN_PROGRESS.value, 1),
                    else_=0
                )
            ).label("in_progress"),
            func.sum(
                case(
                    (LearningAssignment.status == AssignmentStatus.OVERDUE.value, 1),
                    else_=0
                )
            ).label("overdue"),
        )
        .join(Page, Page.id == LearningAssignment.page_id)
        .group_by(LearningAssignment.page_id, Page.title)
    )

    if page_id:
        query = query.where(LearningAssignment.page_id == page_id)

    result = await db.execute(query)
    rows = result.all()

    return [
        CompletionReportItem(
            page_id=str(row.page_id),
            page_title=row.title,
            total_assigned=row.total,
            completed=row.completed or 0,
            in_progress=row.in_progress or 0,
            overdue=row.overdue or 0,
            completion_rate=(row.completed or 0) / row.total * 100 if row.total > 0 else 0,
        )
        for row in rows
    ]


@router.get("/reports/overdue", response_model=OverdueReport)
async def get_overdue_report(
    db: DbSession = None,
    current_user: CurrentUser = None,
) -> OverdueReport:
    """Get overdue assignments report."""
    from sqlalchemy import select, func
    from src.db.models.learning_assignment import LearningAssignment

    # Update overdue status first
    now = datetime.now(timezone.utc)
    overdue_query = (
        select(LearningAssignment)
        .where(
            LearningAssignment.status.in_([
                AssignmentStatus.ASSIGNED.value,
                AssignmentStatus.IN_PROGRESS.value,
            ]),
            LearningAssignment.due_date < now,
        )
    )

    result = await db.execute(overdue_query)
    overdue_assignments = list(result.scalars().all())

    for a in overdue_assignments:
        a.mark_overdue()

    await db.flush()

    # Get all overdue
    assignments, total = await service.list_assignments(
        db,
        status=AssignmentStatus.OVERDUE,
        limit=500,
    )

    return OverdueReport(
        total_overdue=total,
        assignments=[AssignmentResponse.model_validate(a) for a in assignments],
    )


@router.get("/reports/user/{user_id}", response_model=UserTrainingHistory)
async def get_user_training_history(
    user_id: str,
    db: DbSession = None,
    current_user: CurrentUser = None,
) -> UserTrainingHistory:
    """Get training history for a specific user."""
    from sqlalchemy import select, func
    from src.db.models.user import User
    from src.db.models.learning_assignment import LearningAssignment
    from src.db.models.training_acknowledgment import TrainingAcknowledgment

    # Get user info
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Count assignments by status
    status_query = (
        select(
            LearningAssignment.status,
            func.count(LearningAssignment.id).label("count"),
        )
        .where(LearningAssignment.user_id == user_id)
        .group_by(LearningAssignment.status)
    )
    status_result = await db.execute(status_query)
    status_counts = {row.status: row.count for row in status_result}

    completed = status_counts.get(AssignmentStatus.COMPLETED.value, 0)
    in_progress = status_counts.get(AssignmentStatus.IN_PROGRESS.value, 0)
    overdue = status_counts.get(AssignmentStatus.OVERDUE.value, 0)
    assigned = status_counts.get(AssignmentStatus.ASSIGNED.value, 0)
    total = sum(status_counts.values())

    # Get acknowledgments
    ack_result = await db.execute(
        select(TrainingAcknowledgment)
        .where(TrainingAcknowledgment.user_id == user_id)
        .order_by(TrainingAcknowledgment.acknowledged_at.desc())
    )
    acknowledgments = list(ack_result.scalars().all())

    return UserTrainingHistory(
        user_id=str(user.id),
        user_email=user.email,
        user_name=user.full_name or user.email,
        total_assignments=total,
        completed=completed,
        in_progress=in_progress,
        overdue=overdue,
        acknowledgments=[AcknowledgmentResponse.model_validate(a) for a in acknowledgments],
    )


@router.get("/reports/page/{page_id}", response_model=PageTrainingReport)
async def get_page_training_report(
    page_id: str,
    db: DbSession = None,
    current_user: CurrentUser = None,
) -> PageTrainingReport:
    """Get training report for a specific page."""
    from sqlalchemy import select, func
    from src.db.models.page import Page
    from src.db.models.assessment import Assessment
    from src.db.models.learning_assignment import LearningAssignment

    # Get page info
    page_result = await db.execute(
        select(Page).where(Page.id == page_id)
    )
    page = page_result.scalar_one_or_none()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    # Check for assessment
    assessment = await service.get_assessment_for_page(db, page_id)
    has_assessment = assessment is not None
    assessment_id = str(assessment.id) if assessment else None

    # Count assignments by status
    status_query = (
        select(
            LearningAssignment.status,
            func.count(LearningAssignment.id).label("count"),
        )
        .where(LearningAssignment.page_id == page_id)
        .group_by(LearningAssignment.status)
    )
    status_result = await db.execute(status_query)
    status_counts = {row.status: row.count for row in status_result}

    completed = status_counts.get(AssignmentStatus.COMPLETED.value, 0)
    total = sum(status_counts.values())
    completion_rate = (completed / total * 100) if total > 0 else 0.0

    # Get all assignments for this page
    assignments, _ = await service.list_assignments(
        db,
        page_id=page_id,
        limit=500,
    )

    return PageTrainingReport(
        page_id=str(page.id),
        page_title=page.title,
        requires_training=page.requires_training or False,
        has_assessment=has_assessment,
        assessment_id=assessment_id,
        total_assigned=total,
        completed=completed,
        completion_rate=completion_rate,
        assignments=[AssignmentResponse.model_validate(a) for a in assignments],
    )


@router.post("/reports/export")
async def export_report(
    request: ReportExportRequest,
    db: DbSession = None,
    current_user: CurrentUser = None,
):
    """Export a report in CSV or JSON format."""
    import csv
    import io
    import json
    from fastapi.responses import StreamingResponse

    if request.report_type == "completion":
        # Get completion report data
        report_items = await get_completion_report(db=db, current_user=current_user)
        data = [item.model_dump() for item in report_items]
        headers = ["page_id", "page_title", "total_assigned", "completed", "in_progress", "overdue", "completion_rate"]

    elif request.report_type == "overdue":
        # Get overdue report data
        report = await get_overdue_report(db=db, current_user=current_user)
        data = [a.model_dump() for a in report.assignments]
        headers = ["id", "page_id", "user_id", "status", "due_date", "assigned_at"]

    elif request.report_type == "user":
        if not request.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required for user report",
            )
        report = await get_user_training_history(
            user_id=request.user_id, db=db, current_user=current_user
        )
        data = [{
            "user_id": report.user_id,
            "user_email": report.user_email,
            "user_name": report.user_name,
            "total_assignments": report.total_assignments,
            "completed": report.completed,
            "in_progress": report.in_progress,
            "overdue": report.overdue,
        }]
        headers = list(data[0].keys())

    elif request.report_type == "page":
        if not request.page_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="page_id is required for page report",
            )
        report = await get_page_training_report(
            page_id=request.page_id, db=db, current_user=current_user
        )
        data = [{
            "page_id": report.page_id,
            "page_title": report.page_title,
            "requires_training": report.requires_training,
            "has_assessment": report.has_assessment,
            "total_assigned": report.total_assigned,
            "completed": report.completed,
            "completion_rate": report.completion_rate,
        }]
        headers = list(data[0].keys())

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid report type: {request.report_type}. Must be one of: completion, overdue, user, page",
        )

    # Generate output
    if request.format == "json":
        return {
            "report_type": request.report_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }

    elif request.format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={request.report_type}_report.csv"
            },
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format: {request.format}. Must be csv or json",
        )
