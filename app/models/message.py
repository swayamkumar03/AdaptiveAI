"""
app/models/message.py
Message model — individual turns in a Conversation (§12, §15).
"""
import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.experience import Experience
    from app.models.feedback import Feedback


class MessageRole(enum.StrEnum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"


class Message(UUIDMixin, TenantMixin, TimestampMixin, Base):
    """
    A single message in a Conversation.

    Key fields:
    - confidence_score: AI-estimated reliability (§16)
    - retrieved_chunk_ids: JSONB list of DocumentChunk IDs used for RAG
    - sources: JSONB list of source references shown to user (§15)
    - is_escalated: flagged for human review
    """
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, name="messagerole"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # RAG provenance — stores list of chunk UUIDs used to build context
    retrieved_chunk_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Source attribution shown to user (§15)
    # Format: [{"filename": "...", "page": 4, "chunk_id": "..."}]
    sources: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # AI confidence score (0.0 – 1.0) (§16)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Prompt token usage tracking
    prompt_tokens: Mapped[int | None] = mapped_column(nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(nullable=True)

    # Whether this message triggered an escalation (§17)
    is_escalated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Arbitrary metadata (model used, latency, etc.)
    # Note: 'metadata' is reserved by SQLAlchemy declarative base.
    message_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    # ── Relationships ──────────────────────────────────────────────────────
    conversation: Mapped["Conversation"] = relationship(  # type: ignore[name-defined]
        "Conversation", back_populates="messages"
    )
    feedback: Mapped["Feedback | None"] = relationship(  # type: ignore[name-defined]
        "Feedback", back_populates="message", uselist=False, cascade="all, delete-orphan"
    )
    experience: Mapped["Experience | None"] = relationship(  # type: ignore[name-defined]
        "Experience", back_populates="source_message", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Message id={self.id} role={self.role} conf={self.confidence_score}>"
