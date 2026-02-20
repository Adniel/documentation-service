"""AI-powered question generation from page content."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ai.prompts import QUESTION_GENERATION_SYSTEM
from src.modules.ai.schemas import (
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
    GeneratedQuestion,
    GeneratedQuestionOption,
)
from src.modules.ai.service import AIService
from src.modules.content.service import get_page
from src.modules.content.tiptap_to_markdown import tiptap_to_markdown


async def generate_questions(
    db: AsyncSession,
    ai: AIService,
    request: GenerateQuestionsRequest,
) -> GenerateQuestionsResponse:
    """Generate assessment questions from a page's content.

    Fetches the page, converts to markdown, and uses AI to generate questions.
    """
    page = await get_page(db, request.page_id)
    if not page:
        raise ValueError(f"Page not found: {request.page_id}")

    markdown = tiptap_to_markdown(page.content)
    if not markdown.strip():
        raise ValueError("Page has no content to generate questions from")

    # Build user prompt
    types_str = ", ".join(request.question_types)
    topics_str = ""
    if request.focus_topics:
        topics_str = f"\nFocus on these topics: {', '.join(request.focus_topics)}"

    user_prompt = f"""Generate {request.count} assessment questions from the following document content.

Requirements:
- Question types: {types_str}
- Difficulty: {request.difficulty}
- Questions must be based on the document content below{topics_str}

Document title: {page.title}

Document content:
{markdown}"""

    result = await ai.complete_json(
        QUESTION_GENERATION_SYSTEM,
        user_prompt,
        temperature=0.7,
    )

    # Parse response into schema
    questions = []
    for q in result.get("questions", []):
        options = [
            GeneratedQuestionOption(
                id=opt["id"],
                text=opt["text"],
                is_correct=opt.get("is_correct", False),
            )
            for opt in q.get("options", [])
        ]
        questions.append(
            GeneratedQuestion(
                question_type=q["question_type"],
                question_text=q["question_text"],
                options=options,
                correct_answer=q.get("correct_answer", ""),
                explanation=q.get("explanation", ""),
                points=q.get("points", 1),
                difficulty=q.get("difficulty", request.difficulty),
                source_excerpt=q.get("source_excerpt", ""),
            )
        )

    return GenerateQuestionsResponse(
        questions=questions,
        page_id=request.page_id,
        page_title=page.title,
        model_used=ai.model,
    )
