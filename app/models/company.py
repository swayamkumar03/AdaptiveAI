"""
app/models/company.py
Company (tenant) model — root of the multi-tenant hierarchy (§5, §6).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.chatbot_settings import ChatbotSettings
    from app.models.conversation import Conversation
    from app.models.document import Document
    from app.models.experience import Experience
    from app.models.knowledge_item import KnowledgeItem
    from app.models.user import User


class Company(UUIDMixin, TimestampMixin, Base):
    """
    Represents one tenant organisation.

    Every other tenant-scoped table has a FK → companies.id.
    Deleting a company cascades to all its child records.
    """
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    subscription_plan: Mapped[str] = mapped_column(
        String(50), default="free", nullable=False
    )
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Relationships ──────────────────────────────────────────────────────
    users: Mapped[list[User]] = relationship(  # type: ignore[name-defined]
        "User", back_populates="company", cascade="all, delete-orphan"
    )
    documents: Mapped[list[Document]] = relationship(  # type: ignore[name-defined]
        "Document", back_populates="company", cascade="all, delete-orphan"
    )
    knowledge_items: Mapped[list[KnowledgeItem]] = relationship(  # type: ignore[name-defined]
        "KnowledgeItem", back_populates="company", cascade="all, delete-orphan"
    )
    conversations: Mapped[list[Conversation]] = relationship(  # type: ignore[name-defined]
        "Conversation", back_populates="company", cascade="all, delete-orphan"
    )
    experiences: Mapped[list[Experience]] = relationship(  # type: ignore[name-defined]
        "Experience", back_populates="company", cascade="all, delete-orphan"
    )
    chatbot_settings: Mapped[ChatbotSettings | None] = relationship(  # type: ignore[name-defined]
        "ChatbotSettings", back_populates="company", uselist=False, cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(  # type: ignore[name-defined]
        "AuditLog", back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Company id={self.id} slug={self.slug!r}>"
