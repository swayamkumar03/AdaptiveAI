"""
app/models/knowledge_item.py
KnowledgeItem model — verified knowledge entries with confidence levels (§8, §21).

Knowledge can originate from:
  - Document chunks (auto-extracted)
  - Manual FAQ entries (admin-created)
  - Verified experiences (approved corrections)
  - Website scraping (optional)
"""
import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.db.base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company import Company


class KnowledgeSourceType(enum.StrEnum):
    DOCUMENT = "DOCUMENT"
    MANUAL = "MANUAL"
    FAQ = "FAQ"
    EXPERIENCE = "EXPERIENCE"
    WEBSITE = "WEBSITE"


class ConfidenceStatus(enum.StrEnum):
    """Knowledge confidence levels (§21)."""
    UNVERIFIED = "UNVERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    VERIFIED = "VERIFIED"
    OUTDATED = "OUTDATED"
    REJECTED = "REJECTED"


class KnowledgeItem(UUIDMixin, TenantMixin, TimestampMixin, Base):
    """
    A discrete, searchable piece of company knowledge.

    Only VERIFIED items are used in RAG retrieval by default.
    Each item is embedded with pgvector for semantic search.
    Versioning tracks updates over time (§22).
    """
    __tablename__ = "knowledge_items"

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    question: Mapped[str | None] = mapped_column(Text, nullable=True)   # For FAQ-style entries
    content: Mapped[str] = mapped_column(Text, nullable=False)           # The actual knowledge text
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.embedding_dimensions), nullable=True
    )
    source_type: Mapped[KnowledgeSourceType] = mapped_column(
        Enum(KnowledgeSourceType, name="knowledgesourcetype"),
        nullable=False,
        default=KnowledgeSourceType.MANUAL,
    )
    # Optional FK to the originating document (if source_type=DOCUMENT)
    source_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    confidence_status: Mapped[ConfidenceStatus] = mapped_column(
        Enum(ConfidenceStatus, name="confidencestatus"),
        nullable=False,
        default=ConfidenceStatus.UNVERIFIED,
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
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # ── Relationships ──────────────────────────────────────────────────────
    company: Mapped["Company"] = relationship(  # type: ignore[name-defined]
        "Company", back_populates="knowledge_items"
    )

    def __repr__(self) -> str:
        return (
            f"<KnowledgeItem id={self.id} source={self.source_type} "
            f"status={self.confidence_status}>"
        )
