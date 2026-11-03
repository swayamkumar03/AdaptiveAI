"""
app/ai/providers/base.py
Abstract LLM and Embedding provider interfaces (§36).

Design goals:
  - Prevent vendor lock-in: swap OpenAI ↔ Gemini ↔ Anthropic ↔ Local
    by changing a single environment variable (AI_PROVIDER).
  - All providers implement the same interface — the orchestrator and
    services never import vendor SDKs directly.
  - Streaming is a first-class concern for chat UX.

Section 36 specifies:
    LLMProvider
    │
    ├── OpenAIProvider
    ├── GeminiProvider
    ├── AnthropicProvider
    └── LocalModelProvider
"""
from __future__ import annotations

import abc
from collections.abc import AsyncGenerator, AsyncIterator
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Shared data types
# ---------------------------------------------------------------------------

@dataclass
class LLMMessage:
    """A single message in the conversation context sent to the LLM."""
    role: str          # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMRequest:
    """Encapsulates everything needed for a single LLM call."""
    messages: list[LLMMessage]
    temperature: float = 0.3
    max_tokens: int = 2048
    # Provider-specific overrides (e.g. {"response_format": {"type": "json_object"}})
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Structured response returned by every LLM provider."""
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    # Raw provider response for debugging
    raw: Any = None

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class EmbeddingResponse:
    """Structured response for embedding calls."""
    embedding: list[float]
    model: str
    token_count: int = 0


# ---------------------------------------------------------------------------
# Abstract LLM Provider
# ---------------------------------------------------------------------------

class LLMProvider(abc.ABC):
    """
    Abstract base class for all LLM providers.

    Concrete implementations:
      - OpenAIProvider  (app/ai/providers/openai_provider.py)
      - GeminiProvider  (app/ai/providers/gemini_provider.py)
      - AnthropicProvider (app/ai/providers/anthropic_provider.py)
      - LocalModelProvider (app/ai/providers/local_provider.py)
    """

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name (e.g. 'openai', 'gemini')."""
        ...

    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        """The model identifier being used (e.g. 'gpt-4o-mini')."""
        ...

    @abc.abstractmethod
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """
        Send a request to the LLM and return the full response.

        Args:
            request: Encapsulated messages, temperature, max_tokens.

        Returns:
            LLMResponse with content, token counts, and raw provider output.
        """
        ...

    @abc.abstractmethod
    def generate_with_streaming(
        self, request: LLMRequest
    ) -> AsyncIterator[str]:
        """
        Stream the LLM response token-by-token.

        Yields:
            str chunks as they arrive from the provider.
        """
        ...

    async def health_check(self) -> bool:
        """
        Verify that the provider is reachable and the API key is valid.
        Override for more thorough checks.
        """
        try:
            response = await self.generate_response(
                LLMRequest(
                    messages=[LLMMessage(role="user", content="Reply with: OK")],
                    max_tokens=5,
                )
            )
            return bool(response.content)
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Abstract Embedding Provider
# ---------------------------------------------------------------------------

class EmbeddingProvider(abc.ABC):
    """
    Abstract base class for all embedding providers.

    Note: The embedding provider may differ from the LLM provider.
    For example: LLM=Anthropic, Embeddings=OpenAI.
    This is configured via AI_PROVIDER and EMBEDDING_PROVIDER in .env.
    """

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def embedding_dimensions(self) -> int:
        """The vector size produced by this provider."""
        ...

    @abc.abstractmethod
    async def generate_embedding(self, text: str) -> EmbeddingResponse:
        """
        Generate an embedding vector for a single piece of text.

        Args:
            text: The text to embed (cleaned, no PII).

        Returns:
            EmbeddingResponse containing the float vector.
        """
        ...

    @abc.abstractmethod
    async def generate_embeddings_batch(
        self, texts: list[str]
    ) -> list[EmbeddingResponse]:
        """
        Generate embeddings for multiple texts in a single API call.
        Prefer this over calling generate_embedding in a loop.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of EmbeddingResponse, same order as input.
        """
        ...
