"""
app/models/experience.py
Experience model — verified Q&A pairs from real interactions (§18, §20).

Experiences form a separate, human-verified knowledge layer.
Only APPROVED experiences are included in RAG retrieval.
This is the core of AdaptiveAI's continuous improvement mechanism.
"""
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.db.base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.message import Message
    from app.models.user import User


class ExperienceVerificationStatus(enum.StrEnum):
    """Approval lifecycle for an experience (§20)."""
    PENDING = "PENDING"       # Awaiting human review
    APPROVED = "APPROVED"     # Trusted — used in RAG
    REJECTED = "REJECTED"     # Discarded


class Experience(UUIDMixin, TenantMixin, TimestampMixin, Base):
    """
    A verified interaction experience.

    Lifecycle:
      1. User gives negative feedback → Experience created (PENDING)
      2. Employee/Admin reviews → approves or rejects
      3. APPROVED experiences are embedded and included in knowledge retrieval
      4. Future similar questions benefit from the corrected answer

    This creates the controlled adaptive learning loop (§18, §46).
    """
    __tablename__ = "experiences"

    # Source message that triggered this experience
    source_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    original_answer: Mapped[str] = mapped_column(Text, nullable=False)
    # Human-provided correction (may be null if admin creates experience directly)
    corrected_answer: Mapped[str | None] = mapped_column(Text, nullable=True)

    verification_status: Mapped[ExperienceVerificationStatus] = mapped_column(
        Enum(ExperienceVerificationStatus, name="experienceverificationstatus"),
        default=ExperienceVerificationStatus.PENDING,
        nullable=False,
        index=True,
    )
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Embedding of the question (generated after approval)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.embedding_dimensions), nullable=True
    )

    # Reason for rejection (optional)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ──────────────────────────────────────────────────────
    company: Mapped["Company"] = relationship(  # type: ignore[name-defined]
        "Company", back_populates="experiences"
    )
    source_message: Mapped["Message | None"] = relationship(  # type: ignore[name-defined]
        "Message", back_populates="experience"
    )
    verified_by_user: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[verified_by]
    )

    def __repr__(self) -> str:
        return (
            f"<Experience id={self.id} status={self.verification_status}>"
        )
