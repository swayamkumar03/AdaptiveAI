from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CompanyUser
from app.db.session import get_db
from app.models.conversation import Conversation, ConversationStatus
from app.models.escalation import Escalation, EscalationReason, EscalationStatus
from app.models.message import Message, MessageRole
from app.services.rag_service import generate_rag_answer


router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: uuid.UUID | None = None


@router.post("/", summary="Send a message and receive an AI response")
async def chat(
    request: ChatRequest,
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    conversation = None

    # ---------------------------------------------------------
    # 1. Get existing conversation or create a new one
    # ---------------------------------------------------------
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.company_id == current_user.company_id,
                Conversation.user_id == current_user.id,
            )
        )

        conversation = result.scalar_one_or_none()

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

    else:
        conversation = Conversation(
            company_id=current_user.company_id,
            user_id=current_user.id,
            title=request.message[:100],
        )

        db.add(conversation)
        await db.flush()

    # ---------------------------------------------------------
    # 2. Save user's message
    # ---------------------------------------------------------
    user_message = Message(
        company_id=current_user.company_id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=request.message,
    )

    db.add(user_message)
    await db.flush()

    # Save the user message before calling Gemini.
    await db.commit()

    # ---------------------------------------------------------
    # 3. Get previous conversation history
    # ---------------------------------------------------------
    history_result = await db.execute(
        select(Message)
        .where(
            Message.conversation_id == conversation.id,
            Message.company_id == current_user.company_id,
        )
        .order_by(Message.created_at.asc())
        .limit(21)
    )

    history = history_result.scalars().all()

    # Remove the current message so it is not duplicated
    # in both history and the current question.
    previous_messages = [
        message
        for message in history
        if message.id != user_message.id
    ]

    # Keep only the latest 20 previous messages.
    previous_messages = previous_messages[-20:]

    conversation_history = [
        {
            "role": message.role.value.lower(),
            "content": message.content,
        }
        for message in previous_messages
    ]

    # ---------------------------------------------------------
    # 4. Generate RAG answer
    # ---------------------------------------------------------
    try:
        result = await generate_rag_answer(
            db=db,
            company_id=current_user.company_id,
            question=request.message,
            conversation_history=conversation_history,
        )

    except Exception as e:
        return {
            "conversation_id": str(conversation.id),
            "user_message_id": str(user_message.id),
            "answer": (
                "I'm temporarily unable to generate a response. "
                "Please try again in a moment."
            ),
            "error": str(e),
        }

    # ---------------------------------------------------------
    # 5. Handle low-confidence escalation or high-confidence answer
    # ---------------------------------------------------------
    is_escalated = result.get("is_escalated", False)
    confidence_score = result.get("confidence_score")
    escalation_record_id = None

    if is_escalated:
        # Mark conversation as ESCALATED (§17)
        conversation.status = ConversationStatus.ESCALATED
        conversation.escalated_at = datetime.now(timezone.utc)

        assistant_message = Message(
            company_id=current_user.company_id,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=result["answer"],
            confidence_score=confidence_score,
            is_escalated=True,
            retrieved_chunk_ids=[],
            sources=[],
            prompt_tokens=result.get("prompt_tokens"),
            completion_tokens=result.get("completion_tokens"),
            message_metadata={
                "model": result.get("model"),
                "retrieved_chunks": result.get("retrieved_chunks", 0),
                "retrieved_experiences": result.get("retrieved_experiences", 0),
                "escalation_reason": EscalationReason.LOW_CONFIDENCE.value,
            },
        )
        db.add(assistant_message)
        await db.flush()

        # Check if an open/in-progress escalation already exists for this conversation
        existing_esc_res = await db.execute(
            select(Escalation).where(
                Escalation.conversation_id == conversation.id,
                Escalation.company_id == current_user.company_id,
                Escalation.status.in_([EscalationStatus.OPEN, EscalationStatus.IN_PROGRESS]),
            )
        )
        escalation = existing_esc_res.scalar_one_or_none()

        if escalation is None:
            escalation = Escalation(
                company_id=current_user.company_id,
                conversation_id=conversation.id,
                triggering_message_id=assistant_message.id,
                reason=EscalationReason.LOW_CONFIDENCE,
                status=EscalationStatus.OPEN,
            )
            db.add(escalation)
            await db.flush()

        escalation_record_id = str(escalation.id)

    else:
        assistant_message = Message(
            company_id=current_user.company_id,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=result["answer"],
            confidence_score=confidence_score,
            is_escalated=False,
            retrieved_chunk_ids=[
                source["chunk_id"]
                for source in result.get("sources", [])
                if source.get("chunk_id") is not None
            ],
            sources=result.get("sources", []),
            prompt_tokens=result.get("prompt_tokens"),
            completion_tokens=result.get("completion_tokens"),
            message_metadata={
                "model": result.get("model"),
                "retrieved_chunks": result.get("retrieved_chunks", 0),
                "retrieved_experiences": result.get("retrieved_experiences", 0),
            },
        )
        db.add(assistant_message)

    await db.commit()
    await db.refresh(assistant_message)

    # ---------------------------------------------------------
    # 6. Return response
    # ---------------------------------------------------------
    response_payload = {
        "conversation_id": str(conversation.id),
        "user_message_id": str(user_message.id),
        "assistant_message_id": str(assistant_message.id),
        "answer": result["answer"],
        "sources": result.get("sources", []),
        "model": result.get("model"),
        "retrieved_chunks": result.get("retrieved_chunks", 0),
        "retrieved_experiences": result.get("retrieved_experiences", 0),
        "confidence_score": confidence_score,
        "is_escalated": is_escalated,
    }

    if escalation_record_id:
        response_payload["escalation_id"] = escalation_record_id

    return response_payload