"""app/api/v1/feedback.py — Feedback endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CompanyUser
from app.db.session import get_db
from app.models.experience import Experience, ExperienceVerificationStatus
from app.models.feedback import (
    Feedback,
    FeedbackCategory,
    FeedbackRating,
    FeedbackStatus,
)
from app.models.message import Message, MessageRole
from app.models.user import UserRole
from sqlalchemy.orm import selectinload


router = APIRouter()


class FeedbackRequest(BaseModel):
    message_id: uuid.UUID
    rating: FeedbackRating
    feedback_category: FeedbackCategory | None = None
    user_correction: str | None = Field(
        default=None,
        max_length=5000,
    )
    comment: str | None = Field(
        default=None,
        max_length=5000,
    )


@router.post("/", summary="Submit feedback on a message")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    # ---------------------------------------------------------
    # 1. Find the message
    # ---------------------------------------------------------
    result = await db.execute(
        select(Message).where(
            Message.id == request.message_id,
            Message.company_id == current_user.company_id,
        )
    )

    message = result.scalar_one_or_none()

    if message is None:
        raise HTTPException(
            status_code=404,
            detail="Message not found",
        )

    # ---------------------------------------------------------
    # 2. Feedback can only be submitted on AI responses
    # ---------------------------------------------------------
    if message.role != MessageRole.ASSISTANT:
        raise HTTPException(
            status_code=400,
            detail="Feedback can only be submitted on assistant messages",
        )

    # ---------------------------------------------------------
    # 3. Check whether feedback already exists
    # ---------------------------------------------------------
    existing_result = await db.execute(
        select(Feedback).where(
            Feedback.message_id == request.message_id,
        )
    )

    existing_feedback = existing_result.scalar_one_or_none()

    if existing_feedback is not None:
        raise HTTPException(
            status_code=409,
            detail="Feedback has already been submitted for this message",
        )

    # ---------------------------------------------------------
    # 4. Validate negative feedback category
    # ---------------------------------------------------------
    if (
        request.rating == FeedbackRating.NEGATIVE
        and request.feedback_category is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Feedback category is required for negative feedback",
        )

    # ---------------------------------------------------------
    # 5. Create feedback
    # ---------------------------------------------------------
    feedback = Feedback(
        company_id=current_user.company_id,
        message_id=request.message_id,
        user_id=current_user.id,
        rating=request.rating,
        feedback_category=request.feedback_category,
        user_correction=request.user_correction,
        comment=request.comment,
    )

    db.add(feedback)

    await db.commit()
    await db.refresh(feedback)

    return {
        "feedback_id": str(feedback.id),
        "message_id": str(feedback.message_id),
        "rating": feedback.rating.value,
        "feedback_category": (
            feedback.feedback_category.value
            if feedback.feedback_category
            else None
        ),
        "status": feedback.status.value,
    }


@router.get("/", summary="List feedback (Admin/Employee)")
async def list_feedback(
    current_user: CompanyUser,
    status: FeedbackStatus | None = None,
    rating: FeedbackRating | None = None,
    feedback_category: FeedbackCategory | None = None,
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in (
        UserRole.COMPANY_ADMIN,
        UserRole.EMPLOYEE,
        UserRole.SUPER_ADMIN,
    ):
        raise HTTPException(
            status_code=403,
            detail="Only company admins and employees can view feedback.",
        )

    query = (
        select(Feedback)
        .options(selectinload(Feedback.message))
        .where(Feedback.company_id == current_user.company_id)
        .order_by(Feedback.created_at.desc())
    )

    if status is not None:
        query = query.where(Feedback.status == status)
    if rating is not None:
        query = query.where(Feedback.rating == rating)
    if feedback_category is not None:
        query = query.where(Feedback.feedback_category == feedback_category)

    result = await db.execute(query)
    feedbacks = result.scalars().all()

    items = []
    for fb in feedbacks:
        user_question = None
        if fb.message and fb.message.conversation_id:
            user_msg_result = await db.execute(
                select(Message.content)
                .where(
                    Message.conversation_id == fb.message.conversation_id,
                    Message.role == MessageRole.USER,
                    Message.created_at <= fb.message.created_at,
                )
                .order_by(Message.created_at.desc())
                .limit(1)
            )
            user_question = user_msg_result.scalar_one_or_none()

        items.append(
            {
                "feedback_id": str(fb.id),
                "message_id": str(fb.message_id),
                "conversation_id": (
                    str(fb.message.conversation_id) if fb.message else None
                ),
                "rating": fb.rating.value,
                "feedback_category": (
                    fb.feedback_category.value
                    if fb.feedback_category
                    else None
                ),
                "user_correction": fb.user_correction,
                "comment": fb.comment,
                "status": fb.status.value,
                "user_id": str(fb.user_id),
                "reviewed_by": str(fb.reviewed_by) if fb.reviewed_by else None,
                "created_at": (
                    fb.created_at.isoformat() if fb.created_at else None
                ),
                "message_content": fb.message.content if fb.message else None,
                "ai_answer": fb.message.content if fb.message else None,
                "user_question": user_question,
            }
        )

    return items


@router.put("/{feedback_id}/review", summary="Mark feedback as reviewed")
async def review_feedback(
    feedback_id: uuid.UUID,
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in (
        UserRole.COMPANY_ADMIN,
        UserRole.EMPLOYEE,
        UserRole.SUPER_ADMIN,
    ):
        raise HTTPException(
            status_code=403,
            detail="Only company admins and employees can review feedback.",
        )

    result = await db.execute(
        select(Feedback)
        .options(selectinload(Feedback.message))
        .where(
            Feedback.id == feedback_id,
            Feedback.company_id == current_user.company_id,
        )
    )
    feedback = result.scalar_one_or_none()

    if feedback is None:
        raise HTTPException(
            status_code=404,
            detail="Feedback not found",
        )

    if feedback.status in (FeedbackStatus.REVIEWED, FeedbackStatus.RESOLVED):
        raise HTTPException(
            status_code=400,
            detail="Feedback has already been reviewed",
        )

    feedback.status = FeedbackStatus.REVIEWED
    feedback.reviewed_by = current_user.id

    experience_created = False
    experience_id = None

    if feedback.rating == FeedbackRating.NEGATIVE and feedback.user_correction:
        # Check if an experience already exists for this message
        existing_exp_result = await db.execute(
            select(Experience).where(
                Experience.source_message_id == feedback.message_id,
                Experience.company_id == current_user.company_id,
            )
        )
        existing_exp = existing_exp_result.scalar_one_or_none()

        if existing_exp:
            experience_created = False
            experience_id = str(existing_exp.id)
        else:
            msg = feedback.message
            original_answer = msg.content if msg else "Unknown answer"
            user_question = "Unknown question"
            if msg and msg.conversation_id:
                user_msg_result = await db.execute(
                    select(Message.content)
                    .where(
                        Message.conversation_id == msg.conversation_id,
                        Message.role == MessageRole.USER,
                        Message.created_at <= msg.created_at,
                    )
                    .order_by(Message.created_at.desc())
                    .limit(1)
                )
                q_val = user_msg_result.scalar_one_or_none()
                if q_val:
                    user_question = q_val

            experience = Experience(
                company_id=current_user.company_id,
                source_message_id=feedback.message_id,
                question=user_question,
                original_answer=original_answer,
                corrected_answer=feedback.user_correction,
                verification_status=ExperienceVerificationStatus.PENDING,
            )
            db.add(experience)
            await db.flush()
            experience_created = True
            experience_id = str(experience.id)

    await db.commit()
    await db.refresh(feedback)

    return {
        "feedback_id": str(feedback.id),
        "status": feedback.status.value,
        "reviewed_by": str(feedback.reviewed_by),
        "reviewed_at": (
            feedback.updated_at.isoformat() if feedback.updated_at else None
        ),
        "experience_created": experience_created,
        "experience_id": experience_id,
    }