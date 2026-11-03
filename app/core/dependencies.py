"""
app/core/dependencies.py
Reusable FastAPI dependencies for authentication and tenant isolation (§6, §7).

Key dependencies:
  - get_current_user: Validates JWT and returns the User from DB
  - get_current_active_user: Adds is_active check
  - require_roles: Factory for role-based guards
  - get_tenant_id: Extracts company_id from the token (tenant isolation)
"""
import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole

# ---------------------------------------------------------------------------
# HTTP Bearer extractor
# ---------------------------------------------------------------------------
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    """
    Validate the Bearer JWT and return the authenticated User.

    Raises UnauthorizedException on any failure — invalid token,
    expired, user not found, or inactive account.
    """
    if not credentials:
        raise UnauthorizedException("Bearer token missing.")

    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload["sub"]
    except (JWTError, KeyError) as err:
        raise UnauthorizedException("Invalid or expired token.") from err

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedException("User not found.")
    if not user.is_active:
        raise UnauthorizedException("Account is inactive.")

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Alias kept for readability when only active-check is needed."""
    return current_user


def require_roles(*roles: UserRole):
    """
    Dependency factory for role-based access control (§7).

    Usage:
        @router.post("/admin-only")
        async def admin_endpoint(
            _: Annotated[User, Depends(require_roles(UserRole.COMPANY_ADMIN))]
        ):
            ...
    """
    async def _check(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(
                f"Requires one of roles: {[r.value for r in roles]}"
            )
        return current_user

    return _check


def get_tenant_id(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> uuid.UUID:
    """
    Extract and return the tenant (company) ID from the authenticated user.

    Raises ForbiddenException if the user has no company (e.g. SUPER_ADMIN
    calling a company-scoped endpoint directly).

    This is injected into every service method to enforce §6 tenant isolation.
    """
    if current_user.company_id is None:
        raise ForbiddenException(
            "This endpoint requires a company-scoped account."
        )
    return current_user.company_id

async def get_current_company_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Require an authenticated user belonging to a company."""

    if current_user.company_id is None:
        raise ForbiddenException(
            "This endpoint requires a company-scoped account."
        )

    return current_user


CurrentUser = Annotated[User, Depends(get_current_active_user)]

TenantId = Annotated[uuid.UUID, Depends(get_tenant_id)]

AdminUser = Annotated[
    User,
    Depends(require_roles(UserRole.COMPANY_ADMIN, UserRole.SUPER_ADMIN)),
]

EmployeeOrAdmin = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.EMPLOYEE,
            UserRole.COMPANY_ADMIN,
            UserRole.SUPER_ADMIN,
        )
    ),
]

CompanyUser = Annotated[
    User,
    Depends(get_current_company_user),
]