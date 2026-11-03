"""
app/models/escalation.py
Escalation model — tracks conversations handed to human agents (§17).
"""
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.message import Message
    from app.models.user import User


class EscalationStatus(enum.StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class EscalationReason(enum.StrEnum):
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    USER_REQUESTED = "USER_REQUESTED"
    NEGATIVE_FEEDBACK = "NEGATIVE_FEEDBACK"
    SENSITIVE_TOPIC = "SENSITIVE_TOPIC"
    MANUAL = "MANUAL"


class Escalation(UUIDMixin, TenantMixin, TimestampMixin, Base):
    """
    Records a conversation escalation to a human support agent.

    The assigned agent receives:
    - Customer question
    - Conversation history
    - Retrieved documents
    - AI's attempted answer
    - Reason for escalation (§17)
    """
    __tablename__ = "escalations"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    triggering_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    assigned_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reason: Mapped[EscalationReason] = mapped_column(
        Enum(EscalationReason, name="escalationreason"),
        nullable=False,
        default=EscalationReason.LOW_CONFIDENCE,
    )
    status: Mapped[EscalationStatus] = mapped_column(
        Enum(EscalationStatus, name="escalationstatus"),
        default=EscalationStatus.OPEN,
        nullable=False,
        index=True,
    )
    # Agent's resolution notes
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ──────────────────────────────────────────────────────
    assigned_agent: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[assigned_agent_id]
    )
    conversation: Mapped["Conversation"] = relationship(  # type: ignore[name-defined]
        "Conversation", foreign_keys=[conversation_id]
    )
    triggering_message: Mapped["Message | None"] = relationship(  # type: ignore[name-defined]
        "Message", foreign_keys=[triggering_message_id]
    )

    def __repr__(self) -> str:
        return f"<Escalation id={self.id} reason={self.reason} status={self.status}>"
