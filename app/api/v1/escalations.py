"""app/api/v1/escalations.py — Escalation management endpoints (§32)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import CompanyUser
from app.db.session import get_db
from app.models.conversation import Conversation, ConversationStatus
from app.models.escalation import Escalation, EscalationReason, EscalationStatus
from app.models.experience import Experience, ExperienceVerificationStatus
from app.models.message import Message, MessageRole
from app.models.user import User, UserRole

router = APIRouter()


class AssignEscalationRequest(BaseModel):
    agent_id: uuid.UUID | None = None  # None = assign to current user


class ResolveEscalationRequest(BaseModel):
    resolution_notes: str = Field(..., min_length=1, max_length=5000)
    create_experience: bool = True  # Step 8: Optional Experience created as PENDING


class CreateManualEscalationRequest(BaseModel):
    conversation_id: uuid.UUID
    reason: EscalationReason = EscalationReason.MANUAL
    triggering_message_id: uuid.UUID | None = None


def _verify_employee_or_admin(current_user: CompanyUser) -> None:
    if current_user.role not in (
        UserRole.COMPANY_ADMIN,
        UserRole.EMPLOYEE,
        UserRole.SUPER_ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company admins and employees can access escalations.",
        )


async def _get_escalation_messages(
    db: AsyncSession, esc: Escalation
) -> tuple[str | None, str | None]:
    """Retrieve customer question and AI response for an escalation."""
    customer_question = None
    ai_answer = None

    if esc.triggering_message_id:
        msg = await db.get(Message, esc.triggering_message_id)
        if msg:
            if msg.role == MessageRole.ASSISTANT:
                ai_answer = msg.content
                # Find the user question that preceded this assistant response
                user_msg_res = await db.execute(
                    select(Message.content)
                    .where(
                        Message.conversation_id == esc.conversation_id,
                        Message.role == MessageRole.USER,
                        Message.created_at <= msg.created_at,
                    )
                    .order_by(Message.created_at.desc())
                    .limit(1)
                )
                customer_question = user_msg_res.scalar_one_or_none()
            else:
                customer_question = msg.content

    if not customer_question:
        # Fallback to the latest user message in the conversation
        latest_user_res = await db.execute(
            select(Message.content)
            .where(
                Message.conversation_id == esc.conversation_id,
                Message.role == MessageRole.USER,
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        customer_question = latest_user_res.scalar_one_or_none()

    return customer_question, ai_answer


def _serialize_escalation(
    esc: Escalation,
    customer_question: str | None = None,
    ai_answer: str | None = None,
) -> dict:
    return {
        "id": str(esc.id),
        "company_id": str(esc.company_id),
        "conversation_id": str(esc.conversation_id),
        "triggering_message_id": (
            str(esc.triggering_message_id) if esc.triggering_message_id else None
        ),
        "assigned_agent_id": (
            str(esc.assigned_agent_id) if esc.assigned_agent_id else None
        ),
        "assigned_agent_name": (
            esc.assigned_agent.full_name if esc.assigned_agent else None
        ),
        "reason": esc.reason.value,
        "status": esc.status.value,
        "resolution_notes": esc.resolution_notes,
        "resolved_at": esc.resolved_at.isoformat() if esc.resolved_at else None,
        "created_at": esc.created_at.isoformat() if esc.created_at else None,
        "updated_at": esc.updated_at.isoformat() if esc.updated_at else None,
        "customer_question": customer_question,
        "ai_answer": ai_answer,
    }


@router.get("/", summary="List escalations (Admin/Employee)")
async def list_escalations(
    current_user: CompanyUser,
    status: EscalationStatus | None = None,
    reason: EscalationReason | None = None,
    assigned_agent_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List company escalations with optional filters (§32)."""
    _verify_employee_or_admin(current_user)

    query = (
        select(Escalation)
        .options(selectinload(Escalation.assigned_agent))
        .where(Escalation.company_id == current_user.company_id)
        .order_by(Escalation.created_at.desc())
    )

    if status is not None:
        query = query.where(Escalation.status == status)
    if reason is not None:
        query = query.where(Escalation.reason == reason)
    if assigned_agent_id is not None:
        query = query.where(Escalation.assigned_agent_id == assigned_agent_id)

    result = await db.execute(query)
    escalations = result.scalars().all()

    items = []
    for esc in escalations:
        q, a = await _get_escalation_messages(db, esc)
        items.append(_serialize_escalation(esc, customer_question=q, ai_answer=a))

    return items


@router.get("/{escalation_id}", summary="Get escalation details")
async def get_escalation(
    escalation_id: uuid.UUID,
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    """Get complete details and conversation history for an escalation (§32)."""
    _verify_employee_or_admin(current_user)

    result = await db.execute(
        select(Escalation)
        .options(selectinload(Escalation.assigned_agent))
        .where(
            Escalation.id == escalation_id,
            Escalation.company_id == current_user.company_id,
        )
    )
    esc = result.scalar_one_or_none()

    if esc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found",
        )

    # Fetch conversation history so the human support agent has full context (§17)
    history_res = await db.execute(
        select(Message)
        .where(
            Message.conversation_id == esc.conversation_id,
            Message.company_id == current_user.company_id,
        )
        .order_by(Message.created_at.asc())
    )
    history_messages = history_res.scalars().all()

    q, a = await _get_escalation_messages(db, esc)
    serialized = _serialize_escalation(esc, customer_question=q, ai_answer=a)
    serialized["conversation_history"] = [
        {
            "id": str(msg.id),
            "role": msg.role.value,
            "content": msg.content,
            "confidence_score": msg.confidence_score,
            "is_escalated": msg.is_escalated,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
        }
        for msg in history_messages
    ]

    return serialized


@router.put("/{escalation_id}/assign", summary="Assign escalation to an agent")
async def assign_escalation(
    escalation_id: uuid.UUID,
    current_user: CompanyUser,
    request: AssignEscalationRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Assign an escalation to an agent (§32)."""
    _verify_employee_or_admin(current_user)

    result = await db.execute(
        select(Escalation)
        .options(selectinload(Escalation.assigned_agent))
        .where(
            Escalation.id == escalation_id,
            Escalation.company_id == current_user.company_id,
        )
    )
    esc = result.scalar_one_or_none()

    if esc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found",
        )

    target_agent_id = (
        request.agent_id
        if request and request.agent_id is not None
        else current_user.id
    )

    # Verify target agent belongs to same company and has employee/admin role
    agent_res = await db.execute(
        select(User).where(
            User.id == target_agent_id,
            User.company_id == current_user.company_id,
            User.is_active.is_(True),
        )
    )
    agent = agent_res.scalar_one_or_none()
    if agent is None or agent.role not in (
        UserRole.COMPANY_ADMIN,
        UserRole.EMPLOYEE,
        UserRole.SUPER_ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target agent not found or does not have support privileges.",
        )

    esc.assigned_agent_id = agent.id
    esc.assigned_agent = agent
    if esc.status == EscalationStatus.OPEN:
        esc.status = EscalationStatus.IN_PROGRESS

    # Update conversation assigned agent as well
    conv = await db.get(Conversation, esc.conversation_id)
    if conv and conv.company_id == current_user.company_id:
        conv.assigned_agent_id = agent.id

    await db.commit()
    await db.refresh(esc)

    q, a = await _get_escalation_messages(db, esc)
    return _serialize_escalation(esc, customer_question=q, ai_answer=a)


@router.put("/{escalation_id}/resolve", summary="Resolve an escalation")
async def resolve_escalation(
    escalation_id: uuid.UUID,
    request: ResolveEscalationRequest,
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Resolve an escalation with human notes (§17, §32).
    Optionally creates a PENDING Experience for admin verification (§18, Step 8).
    """
    _verify_employee_or_admin(current_user)

    result = await db.execute(
        select(Escalation)
        .options(selectinload(Escalation.assigned_agent))
        .where(
            Escalation.id == escalation_id,
            Escalation.company_id == current_user.company_id,
        )
    )
    esc = result.scalar_one_or_none()

    if esc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found",
        )

    esc.status = EscalationStatus.RESOLVED
    esc.resolution_notes = request.resolution_notes
    esc.resolved_at = datetime.now(timezone.utc)
    if esc.assigned_agent_id is None:
        esc.assigned_agent_id = current_user.id
        esc.assigned_agent = current_user

    # Close conversation session
    conv = await db.get(Conversation, esc.conversation_id)
    if conv and conv.company_id == current_user.company_id:
        conv.status = ConversationStatus.CLOSED

    # Optional: create a PENDING Experience from human resolution (§18, Step 8)
    created_experience_id = None
    if request.create_experience:
        q, a = await _get_escalation_messages(db, esc)
        question_text = q or "Customer escalation question"
        original_answer_text = a or "Escalated to human support"

        # Check if an experience already exists for this triggering message
        exp_exists = False
        if esc.triggering_message_id:
            check_exp = await db.execute(
                select(Experience).where(
                    Experience.source_message_id == esc.triggering_message_id,
                    Experience.company_id == current_user.company_id,
                )
            )
            if check_exp.scalar_one_or_none():
                exp_exists = True

        if not exp_exists:
            experience = Experience(
                company_id=current_user.company_id,
                source_message_id=esc.triggering_message_id,
                question=question_text,
                original_answer=original_answer_text,
                corrected_answer=request.resolution_notes,
                verification_status=ExperienceVerificationStatus.PENDING,
            )
            db.add(experience)
            await db.flush()
            created_experience_id = str(experience.id)

    await db.commit()
    await db.refresh(esc)

    q, a = await _get_escalation_messages(db, esc)
    resp = _serialize_escalation(esc, customer_question=q, ai_answer=a)
    resp["experience_created"] = created_experience_id is not None
    resp["experience_id"] = created_experience_id
    return resp


@router.post("/", summary="Create manual escalation")
async def create_escalation(
    request: CreateManualEscalationRequest,
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    """Manually escalate a conversation to a human support agent (§17)."""
    # Verify conversation exists and belongs to user's company
    conv_result = await db.execute(
        select(Conversation).where(
            Conversation.id == request.conversation_id,
            Conversation.company_id == current_user.company_id,
        )
    )
    conv = conv_result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Check for existing open/in-progress escalation
    existing_esc_res = await db.execute(
        select(Escalation).where(
            Escalation.conversation_id == conv.id,
            Escalation.company_id == current_user.company_id,
            Escalation.status.in_([EscalationStatus.OPEN, EscalationStatus.IN_PROGRESS]),
        )
    )
    existing_esc = existing_esc_res.scalar_one_or_none()
    if existing_esc:
        q, a = await _get_escalation_messages(db, existing_esc)
        return _serialize_escalation(existing_esc, customer_question=q, ai_answer=a)

    conv.status = ConversationStatus.ESCALATED
    conv.escalated_at = datetime.now(timezone.utc)

    esc = Escalation(
        company_id=current_user.company_id,
        conversation_id=conv.id,
        triggering_message_id=request.triggering_message_id,
        reason=request.reason,
        status=EscalationStatus.OPEN,
    )
    db.add(esc)
    await db.commit()
    await db.refresh(esc)

    q, a = await _get_escalation_messages(db, esc)
    return _serialize_escalation(esc, customer_question=q, ai_answer=a)
