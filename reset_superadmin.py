import asyncio

from sqlalchemy import update

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User


async def main():
    new_password = "AdaptiveAI123"
    new_hash = hash_password(new_password)

    async with AsyncSessionLocal() as db:
        await db.execute(
            update(User)
            .where(User.email == "superadmin@adaptiveai.dev")
            .values(hashed_password=new_hash)
        )

        await db.commit()

    print("Super Admin password reset successfully.")


asyncio.run(main())