"""
app/models/feedback.py
Feedback model — user ratings on assistant messages (§19).
"""
import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.message import Message
    from app.models.user import User


class FeedbackRating(enum.StrEnum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"


class FeedbackCategory(enum.StrEnum):
    """Category for negative feedback (§19)."""
    INCORRECT = "INCORRECT"
    INCOMPLETE = "INCOMPLETE"
    MISUNDERSTOOD = "MISUNDERSTOOD"
    OTHER = "OTHER"


class FeedbackStatus(enum.StrEnum):
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"
    RESOLVED = "RESOLVED"


class Feedback(UUIDMixin, TenantMixin, TimestampMixin, Base):
    """
    Feedback submitted by a user on an assistant Message.

    Negative feedback with a user_correction triggers the experience
    extraction pipeline — creating an Experience record for human review.
    Only approved experiences become trusted knowledge (§18, §20).
    """
    __tablename__ = "feedback"

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,   # One feedback per message
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating: Mapped[FeedbackRating] = mapped_column(
        Enum(FeedbackRating, name="feedbackrating"), nullable=False
    )
    feedback_category: Mapped[FeedbackCategory | None] = mapped_column(
        Enum(FeedbackCategory, name="feedbackcategory"), nullable=True
    )
    # Optional correction provided by the user (§19)
    user_correction: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Free-text comment
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[FeedbackStatus] = mapped_column(
        Enum(FeedbackStatus, name="feedbackstatus"),
        default=FeedbackStatus.PENDING,
        nullable=False,
        index=True,
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Relationships ──────────────────────────────────────────────────────
    message: Mapped["Message"] = relationship(  # type: ignore[name-defined]
        "Message", back_populates="feedback"
    )
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="feedback_given", foreign_keys=[user_id]
    )
    reviewer: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[reviewed_by]
    )

    def __repr__(self) -> str:
        return f"<Feedback id={self.id} rating={self.rating} status={self.status}>"
