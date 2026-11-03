"""
app/models/user.py
User model with role-based access control (§7).
Roles: SUPER_ADMIN | COMPANY_ADMIN | EMPLOYEE | CUSTOMER
"""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.conversation import Conversation
    from app.models.document import Document
    from app.models.feedback import Feedback


class UserRole(enum.StrEnum):
    SUPER_ADMIN = "SUPER_ADMIN"
    COMPANY_ADMIN = "COMPANY_ADMIN"
    EMPLOYEE = "EMPLOYEE"
    CUSTOMER = "CUSTOMER"


class User(UUIDMixin, TimestampMixin, Base):
    """
    Platform user.

    - SUPER_ADMIN: company_id is NULL (platform-level admin)
    - All others: company_id is required (enforces tenant boundary)
    """

    __tablename__ = "users"

    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="userrole"),
        nullable=False,
        default=UserRole.CUSTOMER,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships

    company: Mapped["Company | None"] = relationship(
        "Company",
        back_populates="users",
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="user",
        foreign_keys="Conversation.user_id",
        cascade="all, delete-orphan",
    )

    uploaded_documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="uploaded_by_user",
        foreign_keys="Document.uploaded_by",
    )

    feedback_given: Mapped[list["Feedback"]] = relationship(
        "Feedback",
        back_populates="user",
        foreign_keys="Feedback.user_id",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"