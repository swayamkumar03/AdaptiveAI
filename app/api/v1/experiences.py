"""app/api/v1/experiences.py — Experience / knowledge correction endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.gemini_provider import GeminiEmbeddingProvider
from app.core.dependencies import CompanyUser
from app.db.session import get_db
from app.models.experience import Experience, ExperienceVerificationStatus
from app.models.user import UserRole


router = APIRouter()


class CreateExperienceRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000)
    original_answer: str = Field(..., min_length=1, max_length=5000)
    corrected_answer: str = Field(..., min_length=1, max_length=5000)


class RejectExperienceRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)


def _serialize_experience(exp: Experience) -> dict:
    return {
        "id": str(exp.id),
        "company_id": str(exp.company_id),
        "source_message_id": (
            str(exp.source_message_id) if exp.source_message_id else None
        ),
        "question": exp.question,
        "original_answer": exp.original_answer,
        "corrected_answer": exp.corrected_answer,
        "verification_status": exp.verification_status.value,
        "verified_by": str(exp.verified_by) if exp.verified_by else None,
        "verified_at": (
            exp.verified_at.isoformat() if exp.verified_at else None
        ),
        "has_embedding": exp.embedding is not None,
        "rejection_reason": exp.rejection_reason,
        "created_at": (
            exp.created_at.isoformat() if exp.created_at else None
        ),
        "updated_at": (
            exp.updated_at.isoformat() if exp.updated_at else None
        ),
    }


def _verify_role(current_user: CompanyUser) -> None:
    if current_user.role not in (
        UserRole.COMPANY_ADMIN,
        UserRole.EMPLOYEE,
        UserRole.SUPER_ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company admins and employees can manage experiences.",
        )


@router.get("/", summary="List experiences (Admin/Employee)")
async def list_experiences(
    current_user: CompanyUser,
    verification_status: ExperienceVerificationStatus | None = None,
    db: AsyncSession = Depends(get_db),
):
    _verify_role(current_user)

    query = (
        select(Experience)
        .where(Experience.company_id == current_user.company_id)
        .order_by(Experience.created_at.desc())
    )

    if verification_status is not None:
        query = query.where(
            Experience.verification_status == verification_status
        )

    result = await db.execute(query)
    experiences = result.scalars().all()

    return [_serialize_experience(exp) for exp in experiences]


@router.get("/{experience_id}", summary="Get experience details")
async def get_experience(
    experience_id: uuid.UUID,
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    _verify_role(current_user)

    result = await db.execute(
        select(Experience).where(
            Experience.id == experience_id,
            Experience.company_id == current_user.company_id,
        )
    )
    experience = result.scalar_one_or_none()

    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    return _serialize_experience(experience)


@router.post("/", summary="Create an experience manually (Admin/Employee)")
async def create_experience(
    request: CreateExperienceRequest,
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    _verify_role(current_user)

    experience = Experience(
        company_id=current_user.company_id,
        source_message_id=None,
        question=request.question,
        original_answer=request.original_answer,
        corrected_answer=request.corrected_answer,
        verification_status=ExperienceVerificationStatus.PENDING,
    )

    db.add(experience)
    await db.commit()
    await db.refresh(experience)

    return _serialize_experience(experience)


@router.put("/{experience_id}/approve", summary="Approve an experience")
async def approve_experience(
    experience_id: uuid.UUID,
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    _verify_role(current_user)

    result = await db.execute(
        select(Experience).where(
            Experience.id == experience_id,
            Experience.company_id == current_user.company_id,
        )
    )
    experience = result.scalar_one_or_none()

    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    if (
        experience.verification_status
        == ExperienceVerificationStatus.REJECTED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot approve a rejected experience",
        )

    experience.verification_status = ExperienceVerificationStatus.APPROVED
    experience.verified_by = current_user.id
    experience.verified_at = datetime.now(timezone.utc)
    experience.rejection_reason = None

    # Generate embedding for the approved experience
    knowledge_text = (
        f"Question: {experience.question}\n"
        f"Verified answer: {experience.corrected_answer or experience.original_answer}"
    )

    embedding_provider = GeminiEmbeddingProvider()
    try:
        emb_res = await embedding_provider.generate_embedding(knowledge_text)
        experience.embedding = emb_res.embedding
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embedding for experience: {exc}",
        ) from exc

    await db.commit()
    await db.refresh(experience)

    return _serialize_experience(experience)


@router.put("/{experience_id}/reject", summary="Reject an experience")
async def reject_experience(
    experience_id: uuid.UUID,
    current_user: CompanyUser,
    request: RejectExperienceRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    _verify_role(current_user)

    result = await db.execute(
        select(Experience).where(
            Experience.id == experience_id,
            Experience.company_id == current_user.company_id,
        )
    )
    experience = result.scalar_one_or_none()

    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    reason = request.reason if request else None

    experience.verification_status = ExperienceVerificationStatus.REJECTED
    experience.verified_by = current_user.id
    experience.verified_at = datetime.now(timezone.utc)
    experience.rejection_reason = reason
    experience.embedding = None

    await db.commit()
    await db.refresh(experience)

    return _serialize_experience(experience)
