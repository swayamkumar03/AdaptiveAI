"""
app/ai/providers/openai_provider.py
OpenAI concrete implementation of LLMProvider and EmbeddingProvider.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import cast

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.ai.providers.base import (
    EmbeddingProvider,
    EmbeddingResponse,
    LLMProvider,
    LLMRequest,
    LLMResponse,
)
from app.config import settings


class OpenAIProvider(LLMProvider):
    """OpenAI GPT models via the official async SDK."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return settings.openai_llm_model

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        messages = cast(
            list[ChatCompletionMessageParam],
            [{"role": msg.role, "content": msg.content} for msg in request.messages],
        )
        response = await self._client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            **request.extra,
        )
        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            raw=response,
        )

    async def generate_with_streaming(
        self, request: LLMRequest
    ) -> AsyncGenerator[str, None]:
        messages = cast(
            list[ChatCompletionMessageParam],
            [{"role": msg.role, "content": msg.content} for msg in request.messages],
        )
        stream = await self._client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
            **request.extra,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI text-embedding models."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return settings.openai_embedding_model

    @property
    def embedding_dimensions(self) -> int:
        return settings.openai_embedding_dimensions

    async def generate_embedding(self, text: str) -> EmbeddingResponse:
        response = await self._client.embeddings.create(
            model=self.model_name,
            input=text,
            dimensions=self.embedding_dimensions,
        )
        return EmbeddingResponse(
            embedding=response.data[0].embedding,
            model=response.model,
            token_count=response.usage.prompt_tokens,
        )

    async def generate_embeddings_batch(
        self, texts: list[str]
    ) -> list[EmbeddingResponse]:
        response = await self._client.embeddings.create(
            model=self.model_name,
            input=texts,
            dimensions=self.embedding_dimensions,
        )
        return [
            EmbeddingResponse(
                embedding=item.embedding,
                model=response.model,
                token_count=0,  # Usage is aggregate; per-item not available
            )
            for item in sorted(response.data, key=lambda x: x.index)
        ]
