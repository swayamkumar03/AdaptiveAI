"""
app/api/v1/router.py
Aggregates all v1 API routes (§32 — full API surface).
"""
from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    auth,
    chat,
    companies,
    documents,
    escalations,
    experiences,
    feedback,
    knowledge,
    users,
    widget,
)

api_router = APIRouter()

api_router.include_router(auth.router,        prefix="/auth",        tags=["Authentication"])
api_router.include_router(companies.router,   prefix="/companies",   tags=["Companies"])
api_router.include_router(users.router,       prefix="/users",       tags=["Users"])
api_router.include_router(documents.router,   prefix="/documents",   tags=["Documents"])
api_router.include_router(knowledge.router,   prefix="/knowledge",   tags=["Knowledge"])
api_router.include_router(chat.router,        prefix="/chat",        tags=["Chat"])
api_router.include_router(feedback.router,    prefix="/feedback",    tags=["Feedback"])
api_router.include_router(experiences.router, prefix="/experiences", tags=["Experiences"])
api_router.include_router(escalations.router, prefix="/escalations", tags=["Escalations"])
api_router.include_router(analytics.router,   prefix="/analytics",   tags=["Analytics"])
api_router.include_router(widget.router,      prefix="/widget",      tags=["Widget"])
