"""
app/db/init_db.py
First-run database initialisation — seeds the SUPER_ADMIN account
and enables the pgvector extension.
"""
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


async def enable_pgvector(session: AsyncSession) -> None:
    """Enable the pgvector extension if not already installed."""
    await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    await session.commit()
    logger.info("pgvector extension enabled.")


async def seed_super_admin(session: AsyncSession) -> None:
    """
    Create the platform SUPER_ADMIN account on first startup.
    Credentials come from env vars — change them immediately in production.
    """
    from sqlalchemy import select

    result = await session.execute(
        select(User).where(User.email == settings.super_admin_email)
    )
    existing = result.scalar_one_or_none()

    if existing:
        logger.info("Super admin already exists — skipping seed.")
        return

    super_admin = User(
        email=settings.super_admin_email,
        hashed_password=hash_password(settings.super_admin_password),
        full_name="Platform Super Admin",
        role=UserRole.SUPER_ADMIN,
        company_id=None,
        is_active=True,
        is_verified=True,
    )
    session.add(super_admin)
    await session.commit()
    logger.info(
        "Super admin created: %s (change this password immediately!)",
        settings.super_admin_email,
    )


async def init_db() -> None:
    """Entry point called during application startup lifespan."""
    async with AsyncSessionLocal() as session:
        await enable_pgvector(session)
        await seed_super_admin(session)
