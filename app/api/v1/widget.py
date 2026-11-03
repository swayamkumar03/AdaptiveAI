"""
app/api/v1/widget.py
Public Chatbot Widget API for website integration.
Handles tenant resolution from public widget identifier, rate/size validation,
and invokes the existing RAG pipeline with company tenant isolation.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.session import get_db
from app.models.chatbot_settings import ChatbotSettings
from app.models.company import Company
from app.models.conversation import Conversation, ConversationStatus
from app.models.escalation import Escalation, EscalationReason, EscalationStatus
from app.models.feedback import Feedback, FeedbackRating, FeedbackStatus
from app.models.message import Message, MessageRole
from app.models.user import User, UserRole
from app.services.rag_service import generate_rag_answer

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class WidgetChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: uuid.UUID | None = None
    conversation_history: list[dict] | None = None


class WidgetFeedbackRequest(BaseModel):
    message_id: uuid.UUID
    rating: str = Field(..., description="POSITIVE or NEGATIVE")
    comment: str | None = Field(default=None, max_length=1000)


# ---------------------------------------------------------------------------
# Helper: Server-side Tenant Resolution (§12)
# ---------------------------------------------------------------------------

async def resolve_company(widget_id: str, db: AsyncSession) -> Company:
    """
    Resolve company from public widget identifier (slug or UUID).
    Enforces active status. Never trusts a client-supplied company_id.
    """
    clean_id = widget_id.strip()

    is_uuid = False
    parsed_uuid = None
    try:
        parsed_uuid = uuid.UUID(clean_id)
        is_uuid = True
    except ValueError:
        pass

    if is_uuid and parsed_uuid:
        query = select(Company).where(
            or_(Company.id == parsed_uuid, Company.slug == clean_id.lower())
        )
    else:
        query = select(Company).where(Company.slug == clean_id.lower())

    result = await db.execute(query)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot widget not found.",
        )

    if not company.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This company chatbot is currently inactive.",
        )

    return company


async def get_or_create_widget_customer(company: Company, db: AsyncSession) -> User:
    """
    Ensures a customer user exists for the company so foreign keys
    (e.g., Conversation.user_id) are strictly satisfied.
    """
    result = await db.execute(
        select(User).where(
            User.company_id == company.id,
            User.role == UserRole.CUSTOMER,
        ).limit(1)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Create an anonymous/public guest customer user for this tenant
        guest_email = f"guest-{company.slug}@adaptiveai.widget"
        # Check if email exists
        res = await db.execute(select(User).where(User.email == guest_email))
        user = res.scalar_one_or_none()
        if not user:
            user = User(
                company_id=company.id,
                email=guest_email,
                hashed_password=hash_password(str(uuid.uuid4())),
                full_name="Website Customer",
                role=UserRole.CUSTOMER,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

    return user


# ---------------------------------------------------------------------------
# Public Widget Configuration (§12)
# ---------------------------------------------------------------------------

@router.get("/{widget_id}/config", summary="Get public widget configuration")
async def get_widget_config(
    widget_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Public endpoint for web widget to retrieve bot branding and greeting.
    No credentials or sensitive keys are exposed.
    """
    company = await resolve_company(widget_id, db)

    settings_res = await db.execute(
        select(ChatbotSettings).where(ChatbotSettings.company_id == company.id)
    )
    settings = settings_res.scalar_one_or_none()

    bot_name = settings.bot_name if settings and settings.bot_name else f"{company.name} Assistant"
    tone = settings.tone if settings and settings.tone else "Professional"
    brand_description = (
        settings.brand_description
        if settings and settings.brand_description
        else (company.description or f"AI customer support for {company.name}.")
    )

    return {
        "company_id": str(company.id),
        "company_name": company.name,
        "company_slug": company.slug,
        "bot_name": bot_name,
        "tone": tone,
        "brand_description": brand_description,
        "welcome_message": f"Hello! How can I assist you with {company.name} today?",
        "is_active": company.is_active,
    }


# ---------------------------------------------------------------------------
# Public Widget Chat (§12, §13, §15)
# ---------------------------------------------------------------------------

@router.post("/{widget_id}/chat", summary="Send message through public website widget")
async def widget_chat(
    widget_id: str,
    request: WidgetChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Public chat endpoint for embedded website widget.
    - Resolves tenant on server (company isolation)
    - Validates message size
    - Reuses existing RAG pipeline and confidence check
    - Handles escalation safely
    """
    company = await resolve_company(widget_id, db)
    customer_user = await get_or_create_widget_customer(company, db)

    # 1. Resolve or create Conversation
    conversation = None
    if request.session_id:
        conv_res = await db.execute(
            select(Conversation).where(
                Conversation.id == request.session_id,
                Conversation.company_id == company.id,
            )
        )
        conversation = conv_res.scalar_one_or_none()

    if conversation is None:
        conversation = Conversation(
            company_id=company.id,
            user_id=customer_user.id,
            title=request.message[:100],
            status=ConversationStatus.ACTIVE,
        )
        db.add(conversation)
        await db.flush()

    # 2. Save user message
    user_message = Message(
        company_id=company.id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=request.message,
    )
    db.add(user_message)
    await db.commit()

    # 3. Retrieve conversation history
    history_res = await db.execute(
        select(Message)
        .where(
            Message.conversation_id == conversation.id,
            Message.company_id == company.id,
        )
        .order_by(Message.created_at.asc())
        .limit(21)
    )
    history_records = history_res.scalars().all()
    previous_messages = [
        m for m in history_records if m.id != user_message.id
    ][-20:]

    history = [
        {"role": m.role.value.lower(), "content": m.content}
        for m in previous_messages
    ]

    # 4. Generate answer via existing RAG pipeline (§13)
    try:
        rag_result = await generate_rag_answer(
            db=db,
            company_id=company.id,
            question=request.message,
            conversation_history=history,
        )
    except Exception as e:
        return {
            "session_id": str(conversation.id),
            "user_message_id": str(user_message.id),
            "assistant_message_id": None,
            "answer": "I'm temporarily unable to retrieve an answer. Please try again shortly.",
            "sources": [],
            "confidence_score": 0.0,
            "is_escalated": False,
            "error": str(e),
        }

    is_escalated = rag_result.get("is_escalated", False)
    confidence_score = rag_result.get("confidence_score")
    escalation_message = None

    if is_escalated:
        # Mark conversation as escalated (§15)
        conversation.status = ConversationStatus.ESCALATED
        conversation.escalated_at = datetime.now(timezone.utc)

        asst_message = Message(
            company_id=company.id,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=rag_result["answer"],
            confidence_score=confidence_score,
            is_escalated=True,
            sources=[],
            prompt_tokens=rag_result.get("prompt_tokens"),
            completion_tokens=rag_result.get("completion_tokens"),
            message_metadata={
                "model": rag_result.get("model"),
                "source": "website_widget",
                "escalation_reason": EscalationReason.LOW_CONFIDENCE.value,
            },
        )
        db.add(asst_message)
        await db.flush()

        # Check existing open escalation
        esc_res = await db.execute(
            select(Escalation).where(
                Escalation.conversation_id == conversation.id,
                Escalation.company_id == company.id,
                Escalation.status.in_([EscalationStatus.OPEN, EscalationStatus.IN_PROGRESS]),
            )
        )
        escalation = esc_res.scalar_one_or_none()
        if not escalation:
            escalation = Escalation(
                company_id=company.id,
                conversation_id=conversation.id,
                triggering_message_id=asst_message.id,
                reason=EscalationReason.LOW_CONFIDENCE,
                status=EscalationStatus.OPEN,
            )
            db.add(escalation)

        escalation_message = (
            "This query has been referred to our support representatives for follow-up."
        )

    else:
        asst_message = Message(
            company_id=company.id,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=rag_result["answer"],
            confidence_score=confidence_score,
            is_escalated=False,
            sources=rag_result.get("sources", []),
            prompt_tokens=rag_result.get("prompt_tokens"),
            completion_tokens=rag_result.get("completion_tokens"),
            message_metadata={
                "model": rag_result.get("model"),
                "source": "website_widget",
            },
        )
        db.add(asst_message)

    await db.commit()
    await db.refresh(asst_message)

    return {
        "session_id": str(conversation.id),
        "user_message_id": str(user_message.id),
        "assistant_message_id": str(asst_message.id),
        "answer": rag_result["answer"],
        "sources": rag_result.get("sources", []),
        "confidence_score": confidence_score,
        "is_escalated": is_escalated,
        "escalation_message": escalation_message,
    }


# ---------------------------------------------------------------------------
# Public Widget Feedback (§14)
# ---------------------------------------------------------------------------

@router.post("/{widget_id}/feedback", summary="Submit feedback for a widget message")
async def widget_feedback(
    widget_id: str,
    request: WidgetFeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Allows public widget end-users to submit positive or negative feedback.
    Feedback is safely associated with the correct tenant.
    """
    company = await resolve_company(widget_id, db)
    customer_user = await get_or_create_widget_customer(company, db)

    # Verify message exists and belongs to this company
    msg_res = await db.execute(
        select(Message).where(
            Message.id == request.message_id,
            Message.company_id == company.id,
        )
    )
    message = msg_res.scalar_one_or_none()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found.",
        )

    rating_enum = (
        FeedbackRating.POSITIVE
        if request.rating.upper() == "POSITIVE"
        else FeedbackRating.NEGATIVE
    )

    # Check if feedback already exists for this message (one feedback per message)
    fb_res = await db.execute(
        select(Feedback).where(Feedback.message_id == message.id)
    )
    existing_fb = fb_res.scalar_one_or_none()

    if existing_fb:
        existing_fb.rating = rating_enum
        existing_fb.comment = request.comment
    else:
        feedback_record = Feedback(
            company_id=company.id,
            message_id=message.id,
            user_id=customer_user.id,
            rating=rating_enum,
            comment=request.comment,
            status=FeedbackStatus.PENDING,
        )
        db.add(feedback_record)

    await db.commit()

    return {
        "status": "success",
        "message": "Thank you for your feedback!",
    }
