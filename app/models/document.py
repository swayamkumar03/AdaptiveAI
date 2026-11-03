"""
app/models/document.py
Document model — represents an uploaded file in a company's knowledge base (§8, §9).
"""
import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.document_chunk import DocumentChunk
    from app.models.user import User


class FileType(enum.StrEnum):
    PDF = "PDF"
    DOCX = "DOCX"
    TXT = "TXT"
    CSV = "CSV"
    MD = "MD"
    WEBSITE = "WEBSITE"


class DocumentStatus(enum.StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class Document(UUIDMixin, TenantMixin, TimestampMixin, Base):
    """
    A file uploaded by a company admin / employee.

    After upload, the document processing pipeline (§9) will:
      1. Validate the file
      2. Extract text
      3. Clean and chunk
      4. Generate embeddings → document_chunks rows
      5. Set status = READY
    """
    __tablename__ = "documents"

    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[FileType] = mapped_column(
        Enum(FileType, name="filetype"), nullable=False
    )
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="documentstatus"),
        default=DocumentStatus.PENDING,
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # Optional description / title set by admin
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Error message if processing failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Number of chunks created
    chunk_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ── Relationships ──────────────────────────────────────────────────────
    company: Mapped["Company"] = relationship(  # type: ignore[name-defined]
        "Company", back_populates="documents"
    )
    uploaded_by_user: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="uploaded_documents", foreign_keys=[uploaded_by]
    )
    chunks: Mapped[list["DocumentChunk"]] = relationship(  # type: ignore[name-defined]
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} filename={self.filename!r} status={self.status}>"
