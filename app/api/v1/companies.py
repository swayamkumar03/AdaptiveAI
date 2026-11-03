"""
app/api/v1/companies.py
Company management endpoints and platform-level admin endpoints.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import case, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import AdminUser, CompanyUser, CurrentUser, require_roles
from app.db.session import get_db
from app.models.chatbot_settings import ChatbotSettings
from app.models.company import Company
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.escalation import Escalation
from app.models.message import Message, MessageRole
from app.models.user import User, UserRole

router = APIRouter()


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100)
    industry: str | None = Field(default=None, max_length=100)
    description: str | None = None
    website: str | None = Field(default=None, max_length=500)
    subscription_plan: str = Field(default="free", max_length=50)
    logo_url: str | None = Field(default=None, max_length=500)


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=100)
    description: str | None = None
    website: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None
    subscription_plan: str | None = Field(default=None, max_length=50)
    logo_url: str | None = Field(default=None, max_length=500)


class ChatbotSettingsUpdate(BaseModel):
    bot_name: str | None = Field(default=None, max_length=100)
    tone: str | None = Field(default=None, max_length=50)
    response_length: str | None = Field(default=None, max_length=20)
    language: str | None = Field(default=None, max_length=10)
    brand_description: str | None = None
    custom_prompt_addon: str | None = None
    auto_escalate_on_low_confidence: bool | None = None


# ---------------------------------------------------------------------------
# Platform Admin Overview (§5.1)
# ---------------------------------------------------------------------------

@router.get(
    "/platform/overview",
    summary="Get platform-wide overview metrics (SUPER_ADMIN only)",
)
async def get_platform_overview(
    current_user: Annotated[User, Depends(require_roles(UserRole.SUPER_ADMIN))],
    db: AsyncSession = Depends(get_db),
):
    """
    Consolidated platform-wide metrics across all tenants for SUPER_ADMIN.
    All data is computed dynamically via database aggregates.
    """
    # 1. Company metrics
    companies_res = await db.execute(
        select(
            func.count(Company.id).label("total"),
            func.count(case((Company.is_active == True, 1))).label("active"),
            func.count(case((Company.is_active == False, 1))).label("inactive"),
        )
    )
    total_companies, active_companies, inactive_companies = companies_res.one()

    # 2. Total registered users
    users_count_res = await db.execute(select(func.count(User.id)))
    total_users = users_count_res.scalar() or 0

    # 3. Chatbot queries and responses
    msg_res = await db.execute(
        select(
            func.count(case((Message.role == MessageRole.USER, 1))).label("questions"),
            func.count(case((Message.role == MessageRole.ASSISTANT, 1))).label("answers"),
        )
    )
    total_questions, total_answers = msg_res.one()

    # 4. Total documents across all companies
    doc_count_res = await db.execute(select(func.count(Document.id)))
    total_documents = doc_count_res.scalar() or 0

    # 5. Total escalations across all companies
    esc_count_res = await db.execute(select(func.count(Escalation.id)))
    total_escalations = esc_count_res.scalar() or 0

    # 6. Recent companies (last 5)
    recent_companies_res = await db.execute(
        select(Company).order_by(Company.created_at.desc()).limit(5)
    )
    recent_companies = recent_companies_res.scalars().all()

    return {
        "total_companies": total_companies or 0,
        "active_companies": active_companies or 0,
        "inactive_companies": inactive_companies or 0,
        "total_users": total_users,
        "total_user_questions": total_questions or 0,
        "total_assistant_answers": total_answers or 0,
        "total_documents": total_documents,
        "total_escalations": total_escalations,
        "recent_companies": [
            {
                "id": str(c.id),
                "name": c.name,
                "slug": c.slug,
                "industry": c.industry,
                "is_active": c.is_active,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in recent_companies
        ],
    }


# ---------------------------------------------------------------------------
# Current Company Settings (for COMPANY_ADMIN / EMPLOYEE)
# ---------------------------------------------------------------------------

@router.get("/me", summary="Get current company details")
async def get_my_company(
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    return {
        "id": str(company.id),
        "name": company.name,
        "slug": company.slug,
        "industry": company.industry,
        "description": company.description,
        "website": company.website,
        "is_active": company.is_active,
        "subscription_plan": company.subscription_plan,
        "logo_url": company.logo_url,
        "created_at": company.created_at.isoformat() if company.created_at else None,
        "updated_at": company.updated_at.isoformat() if company.updated_at else None,
    }


@router.put("/me", summary="Update current company details (COMPANY_ADMIN)")
async def update_my_company(
    data: CompanyUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    if not current_user.company_id:
        raise HTTPException(status_code=403, detail="Company-scoped account required.")

    result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    if data.name is not None:
        company.name = data.name
    if data.industry is not None:
        company.industry = data.industry
    if data.description is not None:
        company.description = data.description
    if data.website is not None:
        company.website = data.website
    if data.logo_url is not None:
        company.logo_url = data.logo_url

    await db.commit()
    await db.refresh(company)

    return {
        "id": str(company.id),
        "name": company.name,
        "slug": company.slug,
        "industry": company.industry,
        "description": company.description,
        "website": company.website,
        "is_active": company.is_active,
        "subscription_plan": company.subscription_plan,
        "logo_url": company.logo_url,
    }


@router.get("/me/chatbot-settings", summary="Get chatbot settings for current company")
async def get_my_chatbot_settings(
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatbotSettings).where(ChatbotSettings.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()

    if not settings:
        # Create default chatbot settings if none exist
        settings = ChatbotSettings(
            company_id=current_user.company_id,
            bot_name="AI Assistant",
            tone="Professional",
            response_length="Medium",
            language="en",
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return {
        "id": str(settings.id),
        "company_id": str(settings.company_id),
        "bot_name": settings.bot_name,
        "tone": settings.tone,
        "response_length": settings.response_length,
        "language": settings.language,
        "brand_description": settings.brand_description,
        "custom_prompt_addon": settings.custom_prompt_addon,
        "auto_escalate_on_low_confidence": settings.auto_escalate_on_low_confidence,
    }


@router.put("/me/chatbot-settings", summary="Update chatbot settings (COMPANY_ADMIN)")
async def update_my_chatbot_settings(
    data: ChatbotSettingsUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    if not current_user.company_id:
        raise HTTPException(status_code=403, detail="Company-scoped account required.")

    result = await db.execute(
        select(ChatbotSettings).where(ChatbotSettings.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()

    if not settings:
        settings = ChatbotSettings(company_id=current_user.company_id)
        db.add(settings)

    if data.bot_name is not None:
        settings.bot_name = data.bot_name
    if data.tone is not None:
        settings.tone = data.tone
    if data.response_length is not None:
        settings.response_length = data.response_length
    if data.language is not None:
        settings.language = data.language
    if data.brand_description is not None:
        settings.brand_description = data.brand_description
    if data.custom_prompt_addon is not None:
        settings.custom_prompt_addon = data.custom_prompt_addon
    if data.auto_escalate_on_low_confidence is not None:
        settings.auto_escalate_on_low_confidence = data.auto_escalate_on_low_confidence

    await db.commit()
    await db.refresh(settings)

    return {
        "id": str(settings.id),
        "company_id": str(settings.company_id),
        "bot_name": settings.bot_name,
        "tone": settings.tone,
        "response_length": settings.response_length,
        "language": settings.language,
        "brand_description": settings.brand_description,
        "custom_prompt_addon": settings.custom_prompt_addon,
        "auto_escalate_on_low_confidence": settings.auto_escalate_on_low_confidence,
    }


# ---------------------------------------------------------------------------
# List companies (SUPER_ADMIN)
# ---------------------------------------------------------------------------

@router.get("/", summary="List all companies (SUPER_ADMIN)")
async def list_companies(
    current_user: Annotated[User, Depends(require_roles(UserRole.SUPER_ADMIN))],
    search: str | None = Query(None, description="Search by name or slug"),
    status_filter: str | None = Query(None, description="active, inactive, or all"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all companies with user, document, and conversation metrics.
    Only SUPER_ADMIN can view all registered tenant companies.
    """
    query = select(Company).order_by(Company.created_at.desc())

    if search:
        term = f"%{search.strip().lower()}%"
        query = query.where(
            func.lower(Company.name).like(term) | func.lower(Company.slug).like(term)
        )

    if status_filter == "active":
        query = query.where(Company.is_active == True)
    elif status_filter == "inactive":
        query = query.where(Company.is_active == False)

    result = await db.execute(query)
    companies = result.scalars().all()

    company_list = []
    for comp in companies:
        # Retrieve counts for each company
        user_cnt = (
            await db.execute(
                select(func.count(User.id)).where(User.company_id == comp.id)
            )
        ).scalar() or 0

        doc_cnt = (
            await db.execute(
                select(func.count(Document.id)).where(Document.company_id == comp.id)
            )
        ).scalar() or 0

        conv_cnt = (
            await db.execute(
                select(func.count(Conversation.id)).where(Conversation.company_id == comp.id)
            )
        ).scalar() or 0

        company_list.append({
            "id": str(comp.id),
            "name": comp.name,
            "slug": comp.slug,
            "industry": comp.industry,
            "description": comp.description,
            "website": comp.website,
            "is_active": comp.is_active,
            "subscription_plan": comp.subscription_plan,
            "logo_url": comp.logo_url,
            "user_count": user_cnt,
            "document_count": doc_cnt,
            "conversation_count": conv_cnt,
            "created_at": comp.created_at.isoformat() if comp.created_at else None,
            "updated_at": comp.updated_at.isoformat() if comp.updated_at else None,
        })

    return company_list


# ---------------------------------------------------------------------------
# Create company (SUPER_ADMIN)
# ---------------------------------------------------------------------------

@router.post(
    "/",
    summary="Create a new company (SUPER_ADMIN)",
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    data: CompanyCreate,
    current_user: Annotated[User, Depends(require_roles(UserRole.SUPER_ADMIN))],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new client company tenant.
    Only SUPER_ADMIN can create companies.
    """
    slug = data.slug.strip().lower()

    # Check whether the slug already exists.
    result = await db.execute(select(Company).where(Company.slug == slug))
    existing_company = result.scalar_one_or_none()

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A company with slug '{slug}' already exists.",
        )

    company = Company(
        name=data.name.strip(),
        slug=slug,
        industry=data.industry,
        description=data.description,
        website=data.website,
        subscription_plan=data.subscription_plan,
        logo_url=data.logo_url,
        is_active=True,
    )

    db.add(company)

    try:
        await db.commit()
        await db.refresh(company)

        # Create default chatbot settings for the new company
        chatbot_setting = ChatbotSettings(
            company_id=company.id,
            bot_name=f"{company.name} AI Assistant",
            brand_description=f"AI support assistant for {company.name}.",
        )
        db.add(chatbot_setting)
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A company with this slug already exists.",
        )

    return {
        "id": str(company.id),
        "name": company.name,
        "slug": company.slug,
        "industry": company.industry,
        "description": company.description,
        "website": company.website,
        "is_active": company.is_active,
        "subscription_plan": company.subscription_plan,
        "logo_url": company.logo_url,
        "created_at": company.created_at.isoformat() if company.created_at else None,
        "updated_at": company.updated_at.isoformat() if company.updated_at else None,
    }


# ---------------------------------------------------------------------------
# Get company by ID
# ---------------------------------------------------------------------------

@router.get("/{company_id}", summary="Get company by ID")
async def get_company(
    company_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.SUPER_ADMIN and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this company.",
        )

    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    user_cnt = (
        await db.execute(select(func.count(User.id)).where(User.company_id == company.id))
    ).scalar() or 0

    doc_cnt = (
        await db.execute(select(func.count(Document.id)).where(Document.company_id == company.id))
    ).scalar() or 0

    return {
        "id": str(company.id),
        "name": company.name,
        "slug": company.slug,
        "industry": company.industry,
        "description": company.description,
        "website": company.website,
        "is_active": company.is_active,
        "subscription_plan": company.subscription_plan,
        "logo_url": company.logo_url,
        "user_count": user_cnt,
        "document_count": doc_cnt,
        "created_at": company.created_at.isoformat() if company.created_at else None,
        "updated_at": company.updated_at.isoformat() if company.updated_at else None,
    }


# ---------------------------------------------------------------------------
# Update company by ID (SUPER_ADMIN)
# ---------------------------------------------------------------------------

@router.put("/{company_id}", summary="Update company (SUPER_ADMIN)")
async def update_company(
    company_id: uuid.UUID,
    data: CompanyUpdate,
    current_user: Annotated[User, Depends(require_roles(UserRole.SUPER_ADMIN))],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    if data.name is not None:
        company.name = data.name
    if data.industry is not None:
        company.industry = data.industry
    if data.description is not None:
        company.description = data.description
    if data.website is not None:
        company.website = data.website
    if data.is_active is not None:
        company.is_active = data.is_active
    if data.subscription_plan is not None:
        company.subscription_plan = data.subscription_plan
    if data.logo_url is not None:
        company.logo_url = data.logo_url

    await db.commit()
    await db.refresh(company)

    return {
        "id": str(company.id),
        "name": company.name,
        "slug": company.slug,
        "industry": company.industry,
        "description": company.description,
        "website": company.website,
        "is_active": company.is_active,
        "subscription_plan": company.subscription_plan,
        "logo_url": company.logo_url,
    }


# ---------------------------------------------------------------------------
# Toggle company status or deactivate (SUPER_ADMIN)
# ---------------------------------------------------------------------------

@router.delete("/{company_id}", summary="Deactivate company (SUPER_ADMIN)")
async def delete_company(
    company_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_roles(UserRole.SUPER_ADMIN))],
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivates a company rather than hard deletion to preserve historical data.
    """
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    company.is_active = False
    await db.commit()

    return {"detail": f"Company '{company.name}' has been deactivated.", "is_active": False}