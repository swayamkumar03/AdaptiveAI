"""
app/ai/providers/anthropic_provider.py
Anthropic Claude concrete implementation of LLMProvider.

Note: Anthropic does not provide an embedding API — use OpenAI or Gemini
embeddings alongside Anthropic for LLM generation.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import cast

import anthropic
from anthropic.types import MessageParam

from app.ai.providers.base import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
)
from app.config import settings


class AnthropicProvider(LLMProvider):
    """Anthropic Claude models via the official async SDK."""

    def __init__(self) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def model_name(self) -> str:
        return settings.anthropic_llm_model

    def _build_messages(
        self, request: LLMRequest
    ) -> tuple[str, list[MessageParam]]:
        """
        Anthropic separates system prompt from messages list.
        Returns (system_prompt, messages_list).
        """
        system_prompt = ""
        messages: list[MessageParam] = []
        for msg in request.messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                # Anthropic expects "user" | "assistant"
                role = "assistant" if msg.role == "assistant" else "user"
                messages.append(cast(MessageParam, {"role": role, "content": msg.content}))
        return system_prompt, messages

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        system_prompt, messages = self._build_messages(request)
        response = await self._client.messages.create(
            model=self.model_name,
            max_tokens=request.max_tokens,
            # Anthropic's create() accepts str (or omit) for system.
            # Pass empty string when there's no system prompt — the SDK
            # treats it the same as omitting the field.
            system=system_prompt,
            messages=messages,
            # NOTE: Anthropic's standard Messages API does not expose a
            # `temperature` parameter in its typed overloads; temperature
            # control is only available via the extended-thinking beta.
        )
        content = response.content[0].text if response.content else ""
        return LLMResponse(
            content=content,
            model=response.model,
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
            raw=response,
        )

    async def generate_with_streaming(
        self, request: LLMRequest
    ) -> AsyncGenerator[str, None]:
        system_prompt, messages = self._build_messages(request)
        async with self._client.messages.stream(
            model=self.model_name,
            max_tokens=request.max_tokens,
            system=system_prompt,
            messages=messages,
            # temperature not supported in standard Messages API
        ) as stream:
            async for text in stream.text_stream:
                yield text
