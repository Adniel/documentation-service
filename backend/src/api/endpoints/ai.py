"""AI feature endpoints — question generation, writing assistance, document masking."""

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser, DbSession
from src.modules.ai.masking import detect_sensitive_content
from src.modules.ai.question_generator import generate_questions
from src.modules.ai.schemas import (
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
    MaskRequest,
    MaskResponse,
    WritingAssistRequest,
    WritingAssistResponse,
)
from src.modules.ai.service import AIService, get_ai_service
from src.modules.ai.writing_assistant import writing_assist
from src.modules.audit.audit_service import AuditService

router = APIRouter()


def _require_ai() -> AIService:
    """Get AI service or raise 503 if not configured."""
    service = get_ai_service()
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured. Set AI_API_KEY in environment.",
        )
    return service


@router.post("/generate-questions", response_model=GenerateQuestionsResponse)
async def api_generate_questions(
    request: GenerateQuestionsRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """Generate assessment questions from a page's content."""
    ai = _require_ai()
    try:
        result = await generate_questions(db, ai, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    await AuditService(db).log_event(
        event_type="ai.questions_generated",
        actor_id=str(current_user.id),
        actor_email=current_user.email,
        resource_type="page",
        resource_id=request.page_id,
        details={
            "count": len(result.questions),
            "difficulty": request.difficulty,
            "model": result.model_used,
        },
    )
    return result


@router.post("/writing-assist", response_model=WritingAssistResponse)
async def api_writing_assist(
    request: WritingAssistRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """Apply AI writing assistance to text."""
    ai = _require_ai()
    result = await writing_assist(ai, request)

    await AuditService(db).log_event(
        event_type="ai.writing_assist",
        actor_id=str(current_user.id),
        actor_email=current_user.email,
        resource_type="text",
        details={
            "action": request.action.value,
            "text_length": len(request.text),
            "model": result.model_used,
        },
    )
    return result


@router.post("/mask", response_model=MaskResponse)
async def api_mask(
    request: MaskRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """Detect sensitive content in text or page content."""
    ai = _require_ai()
    try:
        result = await detect_sensitive_content(db, ai, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    await AuditService(db).log_event(
        event_type="ai.mask_detected",
        actor_id=str(current_user.id),
        actor_email=current_user.email,
        resource_type="page" if request.page_id else "text",
        resource_id=request.page_id,
        details={
            "total_found": result.total_found,
            "categories": [c.value for c in result.categories_found],
            "model": result.model_used,
        },
    )
    return result
