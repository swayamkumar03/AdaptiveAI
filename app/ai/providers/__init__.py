"""
app/ai/providers/__init__.py
Provider factory — returns the correct LLMProvider / EmbeddingProvider
based on the AI_PROVIDER and EMBEDDING_PROVIDER env vars.

Usage:
    from app.ai.providers import get_llm_provider, get_embedding_provider

    llm = get_llm_provider()          # Singleton per process
    embedder = get_embedding_provider()
"""
from functools import lru_cache

from app.ai.providers.base import EmbeddingProvider, LLMProvider
from app.config import settings


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider:
    """
    Returns the configured LLM provider singleton.
    Change AI_PROVIDER in .env to switch providers — no code changes needed.
    """
    provider = settings.ai_provider
    if provider == "openai":
        from app.ai.providers.openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif provider == "gemini":
        from app.ai.providers.gemini_provider import GeminiProvider
        return GeminiProvider()
    elif provider == "anthropic":
        from app.ai.providers.anthropic_provider import AnthropicProvider
        return AnthropicProvider()
    else:
        raise ValueError(
            f"Unknown AI_PROVIDER: {provider!r}. "
            "Supported: 'openai', 'gemini', 'anthropic', 'local'."
        )


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    """
    Returns the configured Embedding provider singleton.
    The embedding provider can differ from the LLM provider.
    """
    provider = settings.embedding_provider
    if provider == "openai":
        from app.ai.providers.openai_provider import OpenAIEmbeddingProvider
        return OpenAIEmbeddingProvider()
    elif provider == "gemini":
        from app.ai.providers.gemini_provider import GeminiEmbeddingProvider
        return GeminiEmbeddingProvider()
    else:
        raise ValueError(
            f"Unknown EMBEDDING_PROVIDER: {provider!r}. "
            "Supported: 'openai', 'gemini'."
        )


__all__ = ["get_llm_provider", "get_embedding_provider"]
