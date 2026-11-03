"""
app/models/audit_log.py
AuditLog model — immutable record of all administrative actions (§41).
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin, utcnow

if TYPE_CHECKING:
    from app.models.company import Company


class AuditLog(UUIDMixin, Base):
    """
    Immutable audit trail for all significant platform actions (§41).

    Records:
    - Who performed the action (user_id)
    - Which company (company_id, nullable for SUPER_ADMIN ops)
    - What action (e.g., "document.upload", "experience.approve")
    - On what resource (resource_type + resource_id)
    - Extra metadata (JSONB)

    AuditLogs are INSERT-only — never updated or deleted.
    """

    __tablename__ = "audit_logs"

    # Note: No TenantMixin — company_id is nullable for SUPER_ADMIN actions
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationship back to the Company model.
    # This matches Company.audit_logs -> back_populates="company".
    company: Mapped["Company | None"] = relationship(
        "Company",
        back_populates="audit_logs",
    )

    # Dotted action name: "document.upload", "experience.approve", etc.
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    resource_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )

    # IP address or request origin
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    # Any relevant context (old/new values, reason, etc.)
    # Note: 'metadata' is reserved by SQLAlchemy declarative base.
    log_metadata: Mapped[dict | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action!r} user={self.user_id}>"