"""app/api/v1/analytics.py — Analytics dashboard endpoints (§25, §32)."""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.dependencies import CompanyUser
from app.db.session import get_db
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.escalation import Escalation, EscalationStatus
from app.models.experience import Experience, ExperienceVerificationStatus
from app.models.feedback import (
    Feedback,
    FeedbackCategory,
    FeedbackRating,
    FeedbackStatus,
)
from app.models.message import Message, MessageRole
from app.models.user import UserRole

router = APIRouter()


def _verify_employee_or_admin(current_user: CompanyUser) -> None:
    """Ensure user belongs to company and has employee/admin privileges."""
    if current_user.role not in (
        UserRole.COMPANY_ADMIN,
        UserRole.EMPLOYEE,
        UserRole.SUPER_ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company admins and employees can access analytics.",
        )


# =============================================================================
# ENDPOINT 1 — OVERVIEW (§25)
# =============================================================================
@router.get("/overview", summary="Get dashboard overview metrics")
async def get_overview(
    current_user: CompanyUser,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Return a consolidated dashboard summary for the authenticated company.
    All metrics are computed via efficient database-level aggregations.
    """
    _verify_employee_or_admin(current_user)
    cid = current_user.company_id

    # 1. Message metrics: user questions, assistant answers, escalations, avg confidence
    msg_query = select(
        func.count(case((Message.role == MessageRole.USER, 1))).label("user_questions"),
        func.count(case((Message.role == MessageRole.ASSISTANT, 1))).label("assistant_answers"),
        func.count(
            case(
                (
                    (Message.role == MessageRole.ASSISTANT) & (Message.is_escalated == True),
                    1,
                )
            )
        ).label("escalated_answers"),
        func.avg(
            case((Message.role == MessageRole.ASSISTANT, Message.confidence_score))
        ).label("avg_confidence"),
    ).where(Message.company_id == cid)

    if start_date is not None:
        msg_query = msg_query.where(Message.created_at >= start_date)
    if end_date is not None:
        msg_query = msg_query.where(Message.created_at <= end_date)

    msg_res = await db.execute(msg_query)
    user_questions, assistant_answers, escalated_answers, avg_confidence = msg_res.one()

    # 2. Escalation metrics
    esc_query = select(
        func.count(Escalation.id).label("total_escalations"),
        func.count(
            case(
                (
                    Escalation.status.in_(
                        [EscalationStatus.OPEN, EscalationStatus.IN_PROGRESS]
                    ),
                    1,
                )
            )
        ).label("open_escalations"),
        func.count(
            case((Escalation.status == EscalationStatus.RESOLVED, 1))
        ).label("resolved_escalations"),
    ).where(Escalation.company_id == cid)

    if start_date is not None:
        esc_query = esc_query.where(Escalation.created_at >= start_date)
    if end_date is not None:
        esc_query = esc_query.where(Escalation.created_at <= end_date)

    esc_res = await db.execute(esc_query)
    total_escalations, open_escalations, resolved_escalations = esc_res.one()

    # 3. Feedback metrics
    fb_query = select(
        func.count(
            case((Feedback.rating == FeedbackRating.POSITIVE, 1))
        ).label("positive_feedback"),
        func.count(
            case((Feedback.rating == FeedbackRating.NEGATIVE, 1))
        ).label("negative_feedback"),
    ).where(Feedback.company_id == cid)

    if start_date is not None:
        fb_query = fb_query.where(Feedback.created_at >= start_date)
    if end_date is not None:
        fb_query = fb_query.where(Feedback.created_at <= end_date)

    fb_res = await db.execute(fb_query)
    positive_feedback, negative_feedback = fb_res.one()

    # 4. Experience metrics
    exp_query = select(
        func.count(
            case(
                (
                    Experience.verification_status
                    == ExperienceVerificationStatus.PENDING,
                    1,
                )
            )
        ).label("pending_experiences"),
        func.count(
            case(
                (
                    Experience.verification_status
                    == ExperienceVerificationStatus.APPROVED,
                    1,
                )
            )
        ).label("approved_experiences"),
        func.count(
            case(
                (
                    Experience.verification_status
                    == ExperienceVerificationStatus.REJECTED,
                    1,
                )
            )
        ).label("rejected_experiences"),
    ).where(Experience.company_id == cid)

    if start_date is not None:
        exp_query = exp_query.where(Experience.created_at >= start_date)
    if end_date is not None:
        exp_query = exp_query.where(Experience.created_at <= end_date)

    exp_res = await db.execute(exp_query)
    pending_experiences, approved_experiences, rejected_experiences = exp_res.one()

    # 5. Conversations & Documents count
    conv_query = select(func.count(Conversation.id)).where(Conversation.company_id == cid)
    if start_date is not None:
        conv_query = conv_query.where(Conversation.created_at >= start_date)
    if end_date is not None:
        conv_query = conv_query.where(Conversation.created_at <= end_date)
    total_conversations = await db.scalar(conv_query) or 0

    doc_query = select(func.count(Document.id)).where(Document.company_id == cid)
    if start_date is not None:
        doc_query = doc_query.where(Document.created_at >= start_date)
    if end_date is not None:
        doc_query = doc_query.where(Document.created_at <= end_date)
    total_documents = await db.scalar(doc_query) or 0

    escalation_rate = (
        round(escalated_answers / assistant_answers, 4)
        if assistant_answers
        else 0.0
    )

    return {
        "total_conversations": total_conversations,
        "total_user_questions": user_questions or 0,
        "total_assistant_answers": assistant_answers or 0,
        "total_escalated_answers": escalated_answers or 0,
        "total_escalations": total_escalations or 0,
        "open_escalations": open_escalations or 0,
        "resolved_escalations": resolved_escalations or 0,
        "escalation_rate": escalation_rate,
        "average_confidence_score": (
            round(float(avg_confidence), 4) if avg_confidence is not None else 0.0
        ),
        "positive_feedback": positive_feedback or 0,
        "negative_feedback": negative_feedback or 0,
        "pending_experiences": pending_experiences or 0,
        "approved_experiences": approved_experiences or 0,
        "rejected_experiences": rejected_experiences or 0,
        "total_documents": total_documents,
    }


# =============================================================================
# ENDPOINT 2 — QUESTIONS (§25)
# =============================================================================
@router.get("/questions", summary="Get question analytics")
async def get_questions(
    current_user: CompanyUser,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Return question-level analytics, confidence breakdown, and recent questions.
    """
    _verify_employee_or_admin(current_user)
    cid = current_user.company_id

    # Aggregates for questions and answers
    stats_query = select(
        func.count(case((Message.role == MessageRole.USER, 1))).label("total_questions"),
        func.count(case((Message.role == MessageRole.ASSISTANT, 1))).label("answered_questions"),
        func.count(
            case(
                (
                    (Message.role == MessageRole.ASSISTANT) & (Message.is_escalated == True),
                    1,
                )
            )
        ).label("escalated_questions"),
        func.count(
            case(
                (
                    (Message.role == MessageRole.ASSISTANT)
                    & (Message.confidence_score < settings.confidence_low_threshold),
                    1,
                )
            )
        ).label("low_confidence_count"),
        func.avg(
            case((Message.role == MessageRole.ASSISTANT, Message.confidence_score))
        ).label("avg_confidence"),
    ).where(Message.company_id == cid)

    if start_date is not None:
        stats_query = stats_query.where(Message.created_at >= start_date)
    if end_date is not None:
        stats_query = stats_query.where(Message.created_at <= end_date)

    stats_res = await db.execute(stats_query)
    total_q, answered_q, escalated_q, low_conf_q, avg_conf = stats_res.one()

    # Query recent user questions with pagination
    user_q_query = (
        select(Message)
        .where(Message.company_id == cid, Message.role == MessageRole.USER)
        .order_by(Message.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    if start_date is not None:
        user_q_query = user_q_query.where(Message.created_at >= start_date)
    if end_date is not None:
        user_q_query = user_q_query.where(Message.created_at <= end_date)

    user_msgs_res = await db.execute(user_q_query)
    user_msgs = user_msgs_res.scalars().all()

    recent_questions = []
    for q_msg in user_msgs:
        # Find corresponding assistant message in the same conversation
        asst_msg_res = await db.execute(
            select(Message)
            .where(
                Message.conversation_id == q_msg.conversation_id,
                Message.role == MessageRole.ASSISTANT,
                Message.created_at >= q_msg.created_at,
            )
            .order_by(Message.created_at.asc())
            .limit(1)
        )
        asst_msg = asst_msg_res.scalar_one_or_none()

        recent_questions.append(
            {
                "message_id": str(q_msg.id),
                "conversation_id": str(q_msg.conversation_id),
                "question": q_msg.content,
                "created_at": q_msg.created_at.isoformat() if q_msg.created_at else None,
                "answer": asst_msg.content if asst_msg else None,
                "confidence_score": asst_msg.confidence_score if asst_msg else None,
                "is_escalated": asst_msg.is_escalated if asst_msg else False,
                "sources_count": len(asst_msg.sources or []) if asst_msg else 0,
            }
        )

    return {
        "total_questions": total_q or 0,
        "answered_questions": answered_q or 0,
        "escalated_questions": escalated_q or 0,
        "low_confidence_count": low_conf_q or 0,
        "average_confidence": (
            round(float(avg_conf), 4) if avg_conf is not None else 0.0
        ),
        "escalation_rate": (
            round(escalated_q / answered_q, 4) if answered_q else 0.0
        ),
        "pagination": {"limit": limit, "offset": offset, "returned": len(recent_questions)},
        "recent_questions": recent_questions,
    }


# =============================================================================
# ENDPOINT 3 — FEEDBACK ANALYTICS (§19, §25)
# =============================================================================
@router.get("/feedback", summary="Get feedback analytics")
async def get_feedback_analytics(
    current_user: CompanyUser,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Return customer feedback analytics, satisfaction rates, and category distribution.
    """
    _verify_employee_or_admin(current_user)
    cid = current_user.company_id

    # 1. Total, positive, negative, and status counts
    fb_query = select(
        func.count(Feedback.id).label("total_feedback"),
        func.count(case((Feedback.rating == FeedbackRating.POSITIVE, 1))).label("positive_count"),
        func.count(case((Feedback.rating == FeedbackRating.NEGATIVE, 1))).label("negative_count"),
        func.count(case((Feedback.status == FeedbackStatus.PENDING, 1))).label("pending_count"),
        func.count(case((Feedback.status == FeedbackStatus.REVIEWED, 1))).label("reviewed_count"),
        func.count(case((Feedback.status == FeedbackStatus.RESOLVED, 1))).label("resolved_count"),
        func.count(case((Feedback.user_correction.is_not(None), 1))).label("corrections_count"),
    ).where(Feedback.company_id == cid)

    if start_date is not None:
        fb_query = fb_query.where(Feedback.created_at >= start_date)
    if end_date is not None:
        fb_query = fb_query.where(Feedback.created_at <= end_date)

    fb_res = await db.execute(fb_query)
    (
        total_fb,
        pos_count,
        neg_count,
        pend_count,
        rev_count,
        res_count,
        corr_count,
    ) = fb_res.one()

    # 2. Category distribution
    cat_query = select(
        Feedback.feedback_category,
        func.count(Feedback.id).label("cat_count"),
    ).where(Feedback.company_id == cid)

    if start_date is not None:
        cat_query = cat_query.where(Feedback.created_at >= start_date)
    if end_date is not None:
        cat_query = cat_query.where(Feedback.created_at <= end_date)

    cat_query = cat_query.group_by(Feedback.feedback_category)
    cat_res = await db.execute(cat_query)
    cat_rows = cat_res.all()

    category_breakdown = {
        FeedbackCategory.INCORRECT.value: 0,
        FeedbackCategory.INCOMPLETE.value: 0,
        FeedbackCategory.MISUNDERSTOOD.value: 0,
        FeedbackCategory.OTHER.value: 0,
        "UNSPECIFIED": 0,
    }
    for cat, count in cat_rows:
        if cat is not None:
            category_breakdown[cat.value] = count
        else:
            category_breakdown["UNSPECIFIED"] = count

    positive_rate = round(pos_count / total_fb, 4) if total_fb else 0.0
    negative_rate = round(neg_count / total_fb, 4) if total_fb else 0.0
    user_correction_rate = round(corr_count / neg_count, 4) if neg_count else 0.0

    return {
        "total_feedback": total_fb or 0,
        "positive_count": pos_count or 0,
        "negative_count": neg_count or 0,
        "positive_rate": positive_rate,
        "negative_rate": negative_rate,
        "pending_count": pend_count or 0,
        "reviewed_count": rev_count or 0,
        "resolved_count": res_count or 0,
        "user_corrections_submitted": corr_count or 0,
        "user_correction_rate": user_correction_rate,
        "category_breakdown": category_breakdown,
    }


# =============================================================================
# ENDPOINT 4 — KNOWLEDGE GAPS (§24)
# =============================================================================
@router.get("/knowledge-gaps", summary="Get unanswered question knowledge gaps (§24)")
async def get_knowledge_gaps(
    current_user: CompanyUser,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Identify knowledge gaps based on low-confidence queries and escalations.
    Returns gaps ordered newest first, with resolution and Experience linkage.
    """
    _verify_employee_or_admin(current_user)
    cid = current_user.company_id

    # Count summary metrics for escalations / knowledge gaps
    summary_query = select(
        func.count(Escalation.id).label("total_gaps"),
        func.count(
            case(
                (
                    Escalation.status.in_(
                        [EscalationStatus.OPEN, EscalationStatus.IN_PROGRESS]
                    ),
                    1,
                )
            )
        ).label("unresolved_gaps"),
        func.count(
            case((Escalation.status == EscalationStatus.RESOLVED, 1))
        ).label("resolved_gaps"),
    ).where(Escalation.company_id == cid)

    if start_date is not None:
        summary_query = summary_query.where(Escalation.created_at >= start_date)
    if end_date is not None:
        summary_query = summary_query.where(Escalation.created_at <= end_date)

    summary_res = await db.execute(summary_query)
    total_gaps, unresolved_gaps, resolved_gaps = summary_res.one()

    # Query Escalation records as knowledge gap items
    esc_query = (
        select(Escalation)
        .where(Escalation.company_id == cid)
        .order_by(Escalation.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    if start_date is not None:
        esc_query = esc_query.where(Escalation.created_at >= start_date)
    if end_date is not None:
        esc_query = esc_query.where(Escalation.created_at <= end_date)

    esc_res = await db.execute(esc_query)
    escalations = esc_res.scalars().all()

    items = []
    experiences_created_count = 0

    for esc in escalations:
        # Retrieve triggering message
        confidence_score = None
        ai_answer = None
        customer_question = None

        if esc.triggering_message_id:
            msg = await db.get(Message, esc.triggering_message_id)
            if msg:
                confidence_score = msg.confidence_score
                if msg.role == MessageRole.ASSISTANT:
                    ai_answer = msg.content
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

        # Check if an Experience was created from this gap resolution
        exp_res = await db.execute(
            select(Experience).where(
                Experience.source_message_id == esc.triggering_message_id,
                Experience.company_id == cid,
            )
        )
        exp = exp_res.scalar_one_or_none()
        if exp:
            experiences_created_count += 1

        items.append(
            {
                "escalation_id": str(esc.id),
                "conversation_id": str(esc.conversation_id),
                "triggering_message_id": (
                    str(esc.triggering_message_id) if esc.triggering_message_id else None
                ),
                "question": customer_question,
                "ai_answer": ai_answer,
                "confidence_score": confidence_score,
                "escalation_reason": esc.reason.value,
                "escalation_status": esc.status.value,
                "resolution_notes": esc.resolution_notes,
                "resolved_at": (
                    esc.resolved_at.isoformat() if esc.resolved_at else None
                ),
                "has_resolution": bool(
                    esc.resolution_notes or esc.status == EscalationStatus.RESOLVED
                ),
                "experience_created": exp is not None,
                "experience_id": str(exp.id) if exp else None,
                "experience_status": exp.verification_status.value if exp else None,
                "created_at": (
                    esc.created_at.isoformat() if esc.created_at else None
                ),
            }
        )

    return {
        "total_knowledge_gaps": total_gaps or 0,
        "unresolved_gaps": unresolved_gaps or 0,
        "resolved_gaps": resolved_gaps or 0,
        "experiences_created_count": experiences_created_count,
        "pagination": {"limit": limit, "offset": offset, "returned": len(items)},
        "knowledge_gaps": items,
    }


# =============================================================================
# ENDPOINT 5 — ACCURACY & RELIABILITY PROXY (§44, §45)
# =============================================================================
@router.get("/accuracy", summary="Get accuracy metrics (§44, §45)")
async def get_accuracy(
    current_user: CompanyUser,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Return operational reliability and feedback-grounded accuracy proxy metrics.

    Note: These represent operational feedback, confidence estimations, and
    resolution performance rather than benchmark ground-truth test accuracy.
    """
    _verify_employee_or_admin(current_user)
    cid = current_user.company_id

    # 1. Assistant message confidence & escalation stats
    msg_query = select(
        func.count(case((Message.role == MessageRole.ASSISTANT, 1))).label("total_answers"),
        func.count(
            case(
                (
                    (Message.role == MessageRole.ASSISTANT) & (Message.is_escalated == True),
                    1,
                )
            )
        ).label("escalated_answers"),
        func.count(
            case(
                (
                    (Message.role == MessageRole.ASSISTANT)
                    & (Message.confidence_score >= settings.confidence_high_threshold),
                    1,
                )
            )
        ).label("high_confidence_answers"),
        func.count(
            case(
                (
                    (Message.role == MessageRole.ASSISTANT)
                    & (Message.confidence_score < settings.confidence_low_threshold),
                    1,
                )
            )
        ).label("low_confidence_answers"),
        func.avg(
            case((Message.role == MessageRole.ASSISTANT, Message.confidence_score))
        ).label("avg_confidence"),
    ).where(Message.company_id == cid)

    if start_date is not None:
        msg_query = msg_query.where(Message.created_at >= start_date)
    if end_date is not None:
        msg_query = msg_query.where(Message.created_at <= end_date)

    msg_res = await db.execute(msg_query)
    (
        total_answers,
        escalated_answers,
        high_conf_answers,
        low_conf_answers,
        avg_confidence,
    ) = msg_res.one()

    # 2. Feedback stats
    fb_query = select(
        func.count(Feedback.id).label("total_feedback"),
        func.count(case((Feedback.rating == FeedbackRating.POSITIVE, 1))).label("positive_count"),
        func.count(case((Feedback.rating == FeedbackRating.NEGATIVE, 1))).label("negative_count"),
        func.count(
            case(
                (
                    (Feedback.rating == FeedbackRating.NEGATIVE)
                    & (Feedback.status.in_([FeedbackStatus.REVIEWED, FeedbackStatus.RESOLVED])),
                    1,
                )
            )
        ).label("reviewed_negative_count"),
    ).where(Feedback.company_id == cid)

    if start_date is not None:
        fb_query = fb_query.where(Feedback.created_at >= start_date)
    if end_date is not None:
        fb_query = fb_query.where(Feedback.created_at <= end_date)

    fb_res = await db.execute(fb_query)
    total_feedback, positive_feedback, negative_feedback, reviewed_neg_feedback = fb_res.one()

    # 3. Verified Experience stats (Human corrections approved into knowledge base)
    exp_query = select(
        func.count(
            case(
                (
                    Experience.verification_status
                    == ExperienceVerificationStatus.APPROVED,
                    1,
                )
            )
        ).label("approved_experiences"),
        func.count(
            case(
                (
                    Experience.verification_status
                    == ExperienceVerificationStatus.PENDING,
                    1,
                )
            )
        ).label("pending_experiences"),
    ).where(Experience.company_id == cid)

    if start_date is not None:
        exp_query = exp_query.where(Experience.created_at >= start_date)
    if end_date is not None:
        exp_query = exp_query.where(Experience.created_at <= end_date)

    exp_res = await db.execute(exp_query)
    approved_experiences, pending_experiences = exp_res.one()

    # Calculate rates
    positive_feedback_rate = (
        round(positive_feedback / total_feedback, 4) if total_feedback else 0.0
    )
    negative_feedback_rate = (
        round(negative_feedback / total_feedback, 4) if total_feedback else 0.0
    )
    escalation_rate = (
        round(escalated_answers / total_answers, 4) if total_answers else 0.0
    )

    return {
        "metric_type": "proxy_reliability_metrics",
        "description": (
            "Operational reliability and user-satisfaction proxy metrics. "
            "Real ground-truth evaluation requires an annotated benchmark dataset."
        ),
        "total_assistant_answers": total_answers or 0,
        "average_confidence_score": (
            round(float(avg_confidence), 4) if avg_confidence is not None else 0.0
        ),
        "confidence_distribution": {
            "high_confidence_count": high_conf_answers or 0,
            "low_confidence_count": low_conf_answers or 0,
            "high_confidence_threshold": settings.confidence_high_threshold,
            "low_confidence_threshold": settings.confidence_low_threshold,
        },
        "feedback_metrics": {
            "total_feedback": total_feedback or 0,
            "positive_feedback_count": positive_feedback or 0,
            "negative_feedback_count": negative_feedback or 0,
            "positive_feedback_rate": positive_feedback_rate,
            "negative_feedback_rate": negative_feedback_rate,
        },
        "escalation_metrics": {
            "escalated_answer_count": escalated_answers or 0,
            "escalation_rate": escalation_rate,
        },
        "adaptive_learning_metrics": {
            "reviewed_negative_feedback_count": reviewed_neg_feedback or 0,
            "verified_correction_count": approved_experiences or 0,
            "pending_experiences_count": pending_experiences or 0,
        },
    }
