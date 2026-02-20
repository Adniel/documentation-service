"""AI-powered writing assistance for documentation."""

from src.modules.ai.prompts import WRITING_ACTION_INSTRUCTIONS, WRITING_ASSIST_SYSTEM
from src.modules.ai.schemas import WritingAction, WritingAssistRequest, WritingAssistResponse
from src.modules.ai.service import AIService

# Temperature overrides per action
ACTION_TEMPERATURES: dict[WritingAction, float] = {
    WritingAction.fix_grammar: 0.3,
    WritingAction.formalize: 0.5,
    WritingAction.translate: 0.3,
}


async def writing_assist(
    ai: AIService,
    request: WritingAssistRequest,
) -> WritingAssistResponse:
    """Apply a writing action to the provided text."""
    # Build action instruction
    instruction = WRITING_ACTION_INSTRUCTIONS.get(
        request.action.value, "Improve the text."
    )
    if request.action == WritingAction.translate:
        lang = request.target_language or "English"
        instruction = instruction.format(target_language=lang)

    # Build user prompt
    parts = [instruction]
    if request.custom_instruction:
        parts.append(f"\nAdditional instruction: {request.custom_instruction}")
    if request.context:
        parts.append(f"\nDocument context: {request.context}")
    parts.append(f"\n\nText to process:\n{request.text}")

    user_prompt = "\n".join(parts)
    temperature = ACTION_TEMPERATURES.get(request.action, 0.7)

    suggested = await ai.complete(
        WRITING_ASSIST_SYSTEM,
        user_prompt,
        temperature=temperature,
    )

    # Generate a brief changes summary
    summary_prompt = (
        f"In one sentence, describe what changed between the original and revised text.\n\n"
        f"Original:\n{request.text[:500]}\n\nRevised:\n{suggested[:500]}"
    )
    changes_summary = await ai.complete(
        "You summarize text changes concisely in one sentence.",
        summary_prompt,
        temperature=0.3,
        max_tokens=150,
    )

    return WritingAssistResponse(
        original_text=request.text,
        suggested_text=suggested.strip(),
        action=request.action,
        changes_summary=changes_summary.strip(),
        model_used=ai.model,
    )
