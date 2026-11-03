import asyncio

from sqlalchemy import select

from app.core.security import verify_password
from app.db.session import AsyncSessionLocal
from app.models.user import User


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(
                User.email == "superadmin@adaptiveai.dev"
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            print("USER NOT FOUND")
            return

        print("USER FOUND")
        print("Email:", user.email)
        print("Role:", user.role)
        print(
            "Password correct:",
            verify_password("AdaptiveAI123", user.hashed_password)
        )


asyncio.run(main())