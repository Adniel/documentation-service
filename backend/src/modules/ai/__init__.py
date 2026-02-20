"""AI module — question generation, writing assistance, and document masking."""

from src.modules.ai.masking import detect_sensitive_content
from src.modules.ai.question_generator import generate_questions
from src.modules.ai.schemas import (
    GeneratedQuestion,
    GeneratedQuestionOption,
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
    MaskRequest,
    MaskResponse,
    SensitiveCategory,
    SensitiveMatch,
    WritingAction,
    WritingAssistRequest,
    WritingAssistResponse,
)
from src.modules.ai.service import AIService, get_ai_service
from src.modules.ai.writing_assistant import writing_assist

__all__ = [
    # Service
    "AIService",
    "get_ai_service",
    # Features
    "generate_questions",
    "writing_assist",
    "detect_sensitive_content",
    # Schemas
    "GenerateQuestionsRequest",
    "GenerateQuestionsResponse",
    "GeneratedQuestion",
    "GeneratedQuestionOption",
    "WritingAction",
    "WritingAssistRequest",
    "WritingAssistResponse",
    "SensitiveCategory",
    "SensitiveMatch",
    "MaskRequest",
    "MaskResponse",
]
