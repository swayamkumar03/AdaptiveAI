"""
app/api/v1/users.py
User management endpoints.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import AdminUser, CurrentUser
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole

router = APIRouter()


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class UserInvite(BaseModel):
    email: str = Field(..., min_length=3, max_length=320)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.EMPLOYEE
    company_id: uuid.UUID | None = None


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole | None = None
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Current user
# ---------------------------------------------------------------------------

@router.get("/me", summary="Get current user profile")
async def get_me(
    current_user: CurrentUser,
):
    """
    Return the profile of the currently authenticated user.
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "company_id": (
            str(current_user.company_id)
            if current_user.company_id
            else None
        ),
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
    }


# ---------------------------------------------------------------------------
# Invite / create user
# ---------------------------------------------------------------------------

@router.post(
    "/invite",
    summary="Create a user for a company (Admin)",
    status_code=status.HTTP_201_CREATED,
)
async def invite_user(
    data: UserInvite,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a user and assign them to a company.

    SUPER_ADMIN can create users for any company.
    COMPANY_ADMIN can create users only for their own company.
    """
    # Determine which company the new user belongs to.
    if current_user.role == UserRole.SUPER_ADMIN:
        if data.company_id is None and data.role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="company_id is required unless creating a SUPER_ADMIN.",
            )
        company_id = data.company_id

    else:
        if current_user.company_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin is not assigned to a company.",
            )

        company_id = current_user.company_id

        # Company admins cannot create another company admin or super admin.
        if data.role in (UserRole.COMPANY_ADMIN, UserRole.SUPER_ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company admins can only invite EMPLOYEE or CUSTOMER accounts.",
            )

    # Prevent duplicate email addresses.
    result = await db.execute(
        select(User).where(User.email == data.email.strip().lower())
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    # Create the user.
    user = User(
        company_id=company_id,
        email=data.email.strip().lower(),
        hashed_password=hash_password(data.password),
        full_name=data.full_name.strip(),
        role=data.role,
        is_active=True,
        is_verified=True,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "company_id": str(user.company_id) if user.company_id else None,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


# ---------------------------------------------------------------------------
# List users (Admin)
# ---------------------------------------------------------------------------

@router.get("/", summary="List users (Admin)")
async def list_users(
    current_user: AdminUser,
    company_id: uuid.UUID | None = Query(None, description="Filter by company (SUPER_ADMIN only)"),
    db: AsyncSession = Depends(get_db),
):
    """
    List users:
    - COMPANY_ADMIN only sees users belonging to their own company.
    - SUPER_ADMIN can see all users or filter by company_id.
    """
    query = select(User).order_by(User.created_at.desc())

    if current_user.role == UserRole.SUPER_ADMIN:
        if company_id:
            query = query.where(User.company_id == company_id)
    else:
        if current_user.company_id is None:
            raise HTTPException(status_code=403, detail="Company-scoped account required.")
        query = query.where(User.company_id == current_user.company_id)

    result = await db.execute(query)
    users = result.scalars().all()

    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "company_id": str(u.company_id) if u.company_id else None,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


# ---------------------------------------------------------------------------
# Update user
# ---------------------------------------------------------------------------

@router.put("/{user_id}", summary="Update user (Admin)")
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Authorization checks
    if current_user.role != UserRole.SUPER_ADMIN:
        if target_user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=403,
                detail="You cannot modify users outside your company.",
            )
        if target_user.id == current_user.id and data.role is not None and data.role != current_user.role:
            raise HTTPException(status_code=403, detail="You cannot alter your own role.")
        if data.role in (UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN):
            raise HTTPException(
                status_code=403,
                detail="Cannot promote user to SUPER_ADMIN or COMPANY_ADMIN.",
            )

    if data.full_name is not None:
        target_user.full_name = data.full_name.strip()
    if data.role is not None:
        target_user.role = data.role
    if data.is_active is not None:
        if target_user.id == current_user.id and not data.is_active:
            raise HTTPException(status_code=400, detail="Cannot deactivate yourself.")
        target_user.is_active = data.is_active

    await db.commit()
    await db.refresh(target_user)

    return {
        "id": str(target_user.id),
        "email": target_user.email,
        "full_name": target_user.full_name,
        "role": target_user.role.value,
        "company_id": str(target_user.company_id) if target_user.company_id else None,
        "is_active": target_user.is_active,
        "is_verified": target_user.is_verified,
    }


# ---------------------------------------------------------------------------
# Deactivate / Remove user
# ---------------------------------------------------------------------------

@router.delete("/{user_id}", summary="Deactivate user (Admin)")
async def delete_user(
    user_id: uuid.UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot remove yourself.")

    if current_user.role != UserRole.SUPER_ADMIN:
        if target_user.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="You cannot modify users outside your company.")
        if target_user.role in (UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN):
            raise HTTPException(status_code=403, detail="Cannot deactivate admin accounts.")

    target_user.is_active = False
    await db.commit()

    return {"detail": f"User '{target_user.email}' has been deactivated.", "is_active": False}