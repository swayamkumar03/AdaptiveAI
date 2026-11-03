"""
app/models/chatbot_settings.py
ChatbotSettings model — per-company chatbot personality configuration (§14, §31).
"""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings as app_settings
from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company import Company


class ChatbotSettings(UUIDMixin, TimestampMixin, Base):
    """
    Company-specific chatbot personality and behaviour settings.

    Admins configure:
    - Bot name and tone (§14)
    - Confidence thresholds (§16)
    - Custom system prompt additions (§31)
    - Escalation behaviour
    """
    __tablename__ = "chatbot_settings"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,   # One settings record per company
        index=True,
    )

    # ── Personality (§14) ─────────────────────────────────────────────────
    bot_name: Mapped[str] = mapped_column(String(100), default="AI Assistant", nullable=False)
    tone: Mapped[str] = mapped_column(String(50), default="Professional", nullable=False)
    response_length: Mapped[str] = mapped_column(String(20), default="Medium", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    brand_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── System Prompt (§31) ───────────────────────────────────────────────
    # Admin-configurable portion (safe rules added on top of the base prompt)
    custom_prompt_addon: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Confidence Thresholds (§16) ───────────────────────────────────────
    confidence_high_threshold: Mapped[float] = mapped_column(
        Float, default=app_settings.confidence_high_threshold, nullable=False
    )
    confidence_low_threshold: Mapped[float] = mapped_column(
        Float, default=app_settings.confidence_low_threshold, nullable=False
    )

    # ── RAG Settings ──────────────────────────────────────────────────────
    rag_top_k: Mapped[int] = mapped_column(
        Integer, default=app_settings.rag_top_k_reranked, nullable=False
    )
    max_context_tokens: Mapped[int] = mapped_column(
        Integer, default=app_settings.max_context_tokens, nullable=False
    )

    # ── Escalation ────────────────────────────────────────────────────────
    auto_escalate_on_low_confidence: Mapped[bool] = mapped_column(default=True, nullable=False)

    # ── Relationships ──────────────────────────────────────────────────────
    company: Mapped["Company"] = relationship(  # type: ignore[name-defined]
        "Company", back_populates="chatbot_settings"
    )

    def __repr__(self) -> str:
        return f"<ChatbotSettings company={self.company_id} bot={self.bot_name!r}>"
