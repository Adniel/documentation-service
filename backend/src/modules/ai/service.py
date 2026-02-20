"""AI service abstraction supporting OpenAI-compatible and Anthropic providers."""

import json
import re

from src.config import get_settings


class AIService:
    """Provider-agnostic AI service.

    Supports two paths:
    - OpenAI-compatible (openai SDK): openai, openrouter, ollama
    - Anthropic native (anthropic SDK): anthropic
    """

    def __init__(
        self,
        provider: str,
        api_key: str,
        model: str,
        base_url: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: int = 60,
    ):
        self.provider = provider
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout

        if provider == "anthropic":
            import anthropic

            self._anthropic_client = anthropic.AsyncAnthropic(
                api_key=api_key,
                timeout=timeout,
            )
        else:
            import openai

            self._openai_client = openai.AsyncOpenAI(
                api_key=api_key or "ollama",
                base_url=base_url,
                timeout=timeout,
            )

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate a text completion."""
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens or self.max_tokens

        if self.provider == "anthropic":
            response = await self._anthropic_client.messages.create(
                model=self.model,
                max_tokens=tokens,
                temperature=temp,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        else:
            response = await self._openai_client.chat.completions.create(
                model=self.model,
                max_tokens=tokens,
                temperature=temp,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict:
        """Generate a completion and parse as JSON.

        Appends JSON instruction to user prompt, strips code fences, parses result.
        """
        json_instruction = "\n\nRespond with valid JSON only. No markdown code fences or explanations."
        raw = await self.complete(
            system_prompt,
            user_prompt + json_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Strip markdown code fences if present
        cleaned = raw.strip()
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()

        return json.loads(cleaned)


def get_ai_service() -> "AIService | None":
    """Factory to create AIService from settings.

    Returns None if no API key configured (and provider != ollama).
    """
    settings = get_settings()

    if not settings.ai_api_key and settings.ai_provider != "ollama":
        return None

    return AIService(
        provider=settings.ai_provider,
        api_key=settings.ai_api_key,
        model=settings.ai_model,
        base_url=settings.ai_resolved_base_url,
        max_tokens=settings.ai_max_tokens,
        temperature=settings.ai_temperature,
        timeout=settings.ai_timeout_seconds,
    )
