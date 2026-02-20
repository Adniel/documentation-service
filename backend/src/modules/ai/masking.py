"""AI-powered sensitive content detection and masking."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ai.prompts import MASKING_SYSTEM
from src.modules.ai.schemas import (
    MaskRequest,
    MaskResponse,
    SensitiveCategory,
    SensitiveMatch,
)
from src.modules.ai.service import AIService
from src.modules.content.service import get_page
from src.modules.content.tiptap_to_markdown import tiptap_to_markdown


async def detect_sensitive_content(
    db: AsyncSession,
    ai: AIService,
    request: MaskRequest,
) -> MaskResponse:
    """Detect sensitive content in text or page content."""
    # Get text from page or direct input
    if request.page_id:
        page = await get_page(db, request.page_id)
        if not page:
            raise ValueError(f"Page not found: {request.page_id}")
        text = tiptap_to_markdown(page.content)
    elif request.text:
        text = request.text
    else:
        raise ValueError("Either page_id or text must be provided")

    if not text.strip():
        return MaskResponse(
            matches=[],
            total_found=0,
            categories_found=[],
            masked_text=text,
            model_used=ai.model,
        )

    # Build user prompt
    categories_str = ""
    if request.categories:
        cats = ", ".join(c.value for c in request.categories)
        categories_str = f"\nOnly scan for these categories: {cats}"

    user_prompt = f"""Analyze the following text for sensitive content that should be masked.{categories_str}

Text to analyze:
{text}"""

    result = await ai.complete_json(
        MASKING_SYSTEM,
        user_prompt,
        temperature=0.1,  # Low temperature for consistent detection
    )

    # Parse matches
    matches = []
    for m in result.get("matches", []):
        try:
            category = SensitiveCategory(m["category"])
        except ValueError:
            continue  # Skip unknown categories

        # Filter by requested categories if specified
        if request.categories and category not in request.categories:
            continue

        matches.append(
            SensitiveMatch(
                category=category,
                text=m["text"],
                confidence=float(m.get("confidence", 0.5)),
                suggested_replacement=m.get("suggested_replacement", f"[REDACTED-{category.value.upper()}]"),
                context_snippet=m.get("context_snippet"),
            )
        )

    # Generate masked text by applying replacements (longest matches first)
    masked_text = text
    sorted_matches = sorted(matches, key=lambda m: len(m.text), reverse=True)
    for match in sorted_matches:
        masked_text = masked_text.replace(match.text, match.suggested_replacement)

    categories_found = list(set(m.category for m in matches))

    return MaskResponse(
        matches=matches,
        total_found=len(matches),
        categories_found=categories_found,
        masked_text=masked_text if matches else None,
        model_used=ai.model,
    )
