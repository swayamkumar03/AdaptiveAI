"""
app/api/v1/auth.py
Authentication endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User

router = APIRouter()


@router.post("/register", summary="Register a new company + admin user")
async def register(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # TODO: Implement company registration.
    return {"detail": "Not yet implemented"}


@router.post("/login", summary="Login and receive JWT tokens")
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Authenticate a user and return access + refresh JWT tokens.
    """

    result = await db.execute(
        select(User).where(User.email == username)
    )
    user = result.scalar_one_or_none()

    # Don't reveal whether the email exists.
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        user_id=str(user.id),
        company_id=str(user.company_id) if user.company_id else None,
        role=user.role.value,
    )

    refresh_token = create_refresh_token(
        user_id=str(user.id),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "company_id": str(user.company_id) if user.company_id else None,
        },
    }


@router.post("/refresh", summary="Refresh an access token")
async def refresh(
    refresh_token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Exchange a valid refresh token for a new access token.
    """

    try:
        payload = decode_refresh_token(refresh_token)
        user_id = payload["sub"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user.",
        )

    access_token = create_access_token(
        user_id=str(user.id),
        company_id=str(user.company_id) if user.company_id else None,
        role=user.role.value,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout", summary="Logout (client-side token invalidation)")
async def logout():
    # JWT is stateless; client discards the token.
    return {"detail": "Logged out."}