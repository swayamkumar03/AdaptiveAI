"""
app/config.py
Pydantic Settings — all configuration loaded from environment / .env file.
"""
from functools import lru_cache
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "AdaptiveAI"
    app_version: str = "0.1.0"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    secret_key: str = "CHANGE_ME"
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── Database ─────────────────────────────────────────────────────────────
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "adaptiveai"
    postgres_user: str = "adaptiveai_user"
    postgres_password: str = "password"

    @computed_field  # type: ignore[misc]
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def database_url_sync(self) -> str:
        """Used by Alembic migrations (sync driver)."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ── JWT ───────────────────────────────────────────────────────────────────
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30

    # ── AI Provider ───────────────────────────────────────────────────────────
    ai_provider: Literal["openai", "gemini", "anthropic", "local"] = "openai"
    embedding_provider: Literal["openai", "gemini", "anthropic", "local"] = "openai"

    # OpenAI
    openai_api_key: str = ""
    openai_llm_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536

    # Gemini
    gemini_api_key: str = ""
    gemini_llm_model: str = "gemini-1.5-flash"
    gemini_embedding_model: str = "models/text-embedding-004"
    gemini_embedding_dimensions: int = 768

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_llm_model: str = "claude-3-5-haiku-20241022"

    # ── RAG / Retrieval ───────────────────────────────────────────────────────
    rag_top_k: int = 10
    rag_top_k_reranked: int = 5
    rag_similarity_threshold: float = 0.70
    max_context_tokens: int = 8000

    # ── Confidence Thresholds (§16) ───────────────────────────────────────────
    confidence_high_threshold: float = 0.80
    confidence_low_threshold: float = 0.50

    # ── Document Processing ────────────────────────────────────────────────────
    max_file_size_mb: int = 50
    allowed_file_types: list[str] = ["pdf", "docx", "txt", "csv", "md"]
    chunk_size_tokens: int = 512
    chunk_overlap_tokens: int = 64
    storage_path: str = "./storage/documents"

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    rate_limit_per_minute: int = 60

    # ── Super Admin Seed ──────────────────────────────────────────────────────
    super_admin_email: str = "superadmin@adaptiveai.dev"
    super_admin_password: str = "CHANGE_ME"

    @property
    def embedding_dimensions(self) -> int:
        """Returns the embedding vector size for the active embedding provider."""
        if self.embedding_provider == "gemini":
            return self.gemini_embedding_dimensions
        return self.openai_embedding_dimensions  # default 1536


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
