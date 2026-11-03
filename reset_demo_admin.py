import asyncio

from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User


async def reset_password():
    email = "admin@adaptiveai-demo.com"
    new_password = "DemoAdmin123!"

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == email)
        )

        user = result.scalar_one_or_none()

        if user is None:
            print("Demo admin not found.")
            return

        user.hashed_password = hash_password(new_password)

        await db.commit()

        print("Password reset successfully.")
        print(f"Email: {email}")
        print(f"Password: {new_password}")


asyncio.run(reset_password())