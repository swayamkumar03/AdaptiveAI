"""
app/models/conversation.py
Conversation model — a chat session between a user and the AI (§13).
"""
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.message import Message
    from app.models.user import User


class ConversationStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    ESCALATED = "ESCALATED"   # Handed to human agent (§17)


class Conversation(UUIDMixin, TenantMixin, TimestampMixin, Base):
    """
    A conversation session.

    Maintains context for the AI (§13 — conversation memory).
    Escalated conversations are routed to human support agents.
    """
    __tablename__ = "conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus, name="conversationstatus"),
        default=ConversationStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    escalated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # ID of the support agent handling an escalation
    assigned_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Relationships ──────────────────────────────────────────────────────
    company: Mapped["Company"] = relationship(  # type: ignore[name-defined]
        "Company", back_populates="conversations"
    )
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="conversations", foreign_keys=[user_id]
    )
    assigned_agent: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[assigned_agent_id]
    )
    messages: Mapped[list["Message"]] = relationship(  # type: ignore[name-defined]
        "Message", back_populates="conversation", cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} status={self.status}>"
