"""
app/ai/providers/gemini_provider.py

Google Gemini implementation using the google-genai SDK.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from google import genai
from google.genai import types

from app.ai.providers.base import (
    EmbeddingProvider,
    EmbeddingResponse,
    LLMProvider,
    LLMRequest,
    LLMResponse,
)
from app.config import settings


class GeminiProvider(LLMProvider):
    """Google Gemini models."""

    def __init__(self) -> None:
        self._client = genai.Client(
            api_key=settings.gemini_api_key
        )

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return settings.gemini_llm_model

    async def generate_response(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        system_instruction = None
        contents = []

        for message in request.messages:
            if message.role == "system":
                system_instruction = message.content

            elif message.role == "user":
                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(
                                text=message.content
                            )
                        ],
                    )
                )

            elif message.role == "assistant":
                contents.append(
                    types.Content(
                        role="model",
                        parts=[
                            types.Part.from_text(
                                text=message.content
                            )
                        ],
                    )
                )

        used_model = self.model_name
        try:
            response = await self._client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=request.temperature,
                    max_output_tokens=request.max_tokens,
                ),
            )
        except Exception as exc:
            error_str = str(exc)
            if (
                ("429" in error_str or "RESOURCE_EXHAUSTED" in error_str)
                and self.model_name != "gemini-3.5-flash"
            ):
                used_model = "gemini-3.5-flash"
                response = await self._client.aio.models.generate_content(
                    model=used_model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=request.temperature,
                        max_output_tokens=request.max_tokens,
                    ),
                )
            else:
                raise

        usage = response.usage_metadata

        prompt_tokens = (
            usage.prompt_token_count
            if usage and usage.prompt_token_count is not None
            else 0
        )

        completion_tokens = (
            usage.candidates_token_count
            if usage and usage.candidates_token_count is not None
            else 0
        )

        return LLMResponse(
            content=response.text or "",
            model=used_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            raw=response,
        )

    async def generate_with_streaming(
        self,
        request: LLMRequest,
    ) -> AsyncGenerator[str, None]:

        system_instruction = None
        contents = []

        for message in request.messages:
            if message.role == "system":
                system_instruction = message.content

            elif message.role == "user":
                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(
                                text=message.content
                            )
                        ],
                    )
                )

            elif message.role == "assistant":
                contents.append(
                    types.Content(
                        role="model",
                        parts=[
                            types.Part.from_text(
                                text=message.content
                            )
                        ],
                    )
                )

        stream = await self._client.aio.models.generate_content_stream(
            model=self.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
            ),
        )

        async for chunk in stream:
            if chunk.text:
                yield chunk.text


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Google Gemini embedding provider."""

    def __init__(self) -> None:
        self._client = genai.Client(
            api_key=settings.gemini_api_key
        )

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return settings.gemini_embedding_model

    @property
    def embedding_dimensions(self) -> int:
        return settings.gemini_embedding_dimensions

    async def generate_embedding(
        self,
        text: str,
    ) -> EmbeddingResponse:

        response = await self._client.aio.models.embed_content(
            model=self.model_name,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=self.embedding_dimensions,
            ),
        )

        if not response.embeddings:
            raise RuntimeError(
                "Gemini returned no embedding."
            )

        values = response.embeddings[0].values

        if values is None:
            raise RuntimeError(
                "Gemini returned an embedding with no values."
            )

        return EmbeddingResponse(
            embedding=list(values),
            model=self.model_name,
        )

    async def generate_embeddings_batch(
        self,
        texts: list[str],
    ) -> list[EmbeddingResponse]:

        if not texts:
            return []

        response = await self._client.aio.models.embed_content(
            model=self.model_name,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=self.embedding_dimensions,
            ),
        )

        if not response.embeddings:
            raise RuntimeError(
                "Gemini returned no embeddings."
            )

        results = []

        for embedding in response.embeddings:
            if embedding.values is None:
                raise RuntimeError(
                    "Gemini returned an embedding with no values."
                )

            results.append(
                EmbeddingResponse(
                    embedding=list(embedding.values),
                    model=self.model_name,
                )
            )

        if len(results) != len(texts):
            raise RuntimeError(
                f"Gemini returned {len(results)} embeddings "
                f"for {len(texts)} texts."
            )

        return results