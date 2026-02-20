"""AI module schemas for request/response models."""

from enum import Enum

from pydantic import BaseModel, Field


class WritingAction(str, Enum):
    """Available writing assistant actions."""

    improve = "improve"
    summarize = "summarize"
    expand = "expand"
    simplify = "simplify"
    formalize = "formalize"
    fix_grammar = "fix_grammar"
    translate = "translate"


class SensitiveCategory(str, Enum):
    """Categories of sensitive content."""

    pii = "pii"
    financial = "financial"
    medical = "medical"
    credentials = "credentials"
    proprietary = "proprietary"


# --- Question Generation ---


class GenerateQuestionsRequest(BaseModel):
    """Request to generate assessment questions from a page."""

    page_id: str
    count: int = Field(default=5, ge=1, le=20)
    question_types: list[str] = Field(
        default=["multiple_choice", "true_false"],
        description="Types: multiple_choice, true_false, fill_blank",
    )
    difficulty: str = Field(
        default="medium",
        description="easy, medium, or hard",
    )
    focus_topics: list[str] = Field(
        default_factory=list,
        description="Optional topics to focus questions on",
    )


class GeneratedQuestionOption(BaseModel):
    """A single option for a generated question."""

    id: str
    text: str
    is_correct: bool


class GeneratedQuestion(BaseModel):
    """A single AI-generated question."""

    question_type: str
    question_text: str
    options: list[GeneratedQuestionOption] = Field(default_factory=list)
    correct_answer: str
    explanation: str = ""
    points: int = 1
    difficulty: str = "medium"
    source_excerpt: str = ""


class GenerateQuestionsResponse(BaseModel):
    """Response from question generation."""

    questions: list[GeneratedQuestion]
    page_id: str
    page_title: str
    model_used: str


# --- Writing Assistant ---


class WritingAssistRequest(BaseModel):
    """Request for writing assistance."""

    text: str = Field(min_length=1, max_length=50000)
    action: WritingAction
    context: str | None = Field(
        default=None,
        description="Additional context about the document",
    )
    target_language: str | None = Field(
        default=None,
        description="Target language for translation action",
    )
    custom_instruction: str | None = Field(
        default=None,
        description="Custom instruction to override default action behavior",
    )


class WritingAssistResponse(BaseModel):
    """Response from writing assistance."""

    original_text: str
    suggested_text: str
    action: WritingAction
    changes_summary: str
    model_used: str


# --- Document Masking ---


class MaskRequest(BaseModel):
    """Request to detect sensitive content."""

    page_id: str | None = None
    text: str | None = Field(default=None, max_length=100000)
    categories: list[SensitiveCategory] | None = Field(
        default=None,
        description="Categories to scan for. None = all categories.",
    )


class SensitiveMatch(BaseModel):
    """A single sensitive content match."""

    category: SensitiveCategory
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    suggested_replacement: str
    context_snippet: str | None = None


class MaskResponse(BaseModel):
    """Response from sensitive content detection."""

    matches: list[SensitiveMatch]
    total_found: int
    categories_found: list[SensitiveCategory]
    masked_text: str | None = None
    model_used: str
