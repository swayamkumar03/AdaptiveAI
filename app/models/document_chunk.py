"""
app/models/document_chunk.py
DocumentChunk model — stores text chunks with pgvector embeddings (§11).
"""
import uuid
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.db.base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.document import Document


class DocumentChunk(UUIDMixin, TenantMixin, TimestampMixin, Base):
    """
    A single chunk of text extracted from a Document.

    The `embedding` column uses pgvector's VECTOR type.
    Vector dimension is read from settings so it matches the chosen
    embedding provider (OpenAI=1536, Gemini=768, etc.).

    The `metadata` JSONB field stores page_number, chunk_index,
    source headings, and any other parser-extracted context.
    """
    __tablename__ = "document_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # pgvector column — dimension set from config
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.embedding_dimensions), nullable=True
    )
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Stores extra context: {"heading": "...", "section": "...", ...}
    # Note: 'metadata' is reserved by SQLAlchemy; column name kept as 'metadata' in DB.
    chunk_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    # ── Relationships ──────────────────────────────────────────────────────
    document: Mapped["Document"] = relationship(  # type: ignore[name-defined]
        "Document", back_populates="chunks"
    )

    def __repr__(self) -> str:
        return (
            f"<DocumentChunk id={self.id} doc={self.document_id} "
            f"chunk_index={self.chunk_index}>"
        )
