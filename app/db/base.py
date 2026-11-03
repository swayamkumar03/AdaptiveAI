"""
app/db/base.py
SQLAlchemy declarative base, UUID primary key mixin, and tenant isolation mixin.
All tenant-scoped models inherit TenantMixin to guarantee company_id presence.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Common base for all ORM models."""
    pass


class UUIDMixin:
    """Provides a UUID primary key for every model."""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class TimestampMixin:
    """Adds created_at / updated_at timestamps to every model."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )


class TenantMixin:
    """
    Enforces multi-tenant isolation (§6, §40).

    Every model that inherits this mixin carries a company_id foreign key.
    The service layer always injects `company_id = current_user.company_id`
    into every query — this mixin makes the column mandatory at the ORM level.
    """
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
