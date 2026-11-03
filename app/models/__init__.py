"""
app/models/__init__.py
Import all models here so Alembic's autogenerate can discover them.
Order matters for FK resolution — parent tables first.
"""
from app.models.audit_log import AuditLog
from app.models.chatbot_settings import ChatbotSettings
from app.models.company import Company
from app.models.conversation import Conversation, ConversationStatus
from app.models.document import Document, DocumentStatus, FileType
from app.models.document_chunk import DocumentChunk
from app.models.escalation import Escalation, EscalationReason, EscalationStatus
from app.models.experience import Experience, ExperienceVerificationStatus
from app.models.feedback import Feedback, FeedbackCategory, FeedbackRating, FeedbackStatus
from app.models.knowledge_item import (
    ConfidenceStatus,
    KnowledgeItem,
    KnowledgeSourceType,
)
from app.models.message import Message, MessageRole
from app.models.user import User, UserRole

__all__ = [
    "Company",
    "User", "UserRole",
    "Document", "DocumentStatus", "FileType",
    "DocumentChunk",
    "KnowledgeItem", "KnowledgeSourceType", "ConfidenceStatus",
    "Conversation", "ConversationStatus",
    "Message", "MessageRole",
    "Feedback", "FeedbackRating", "FeedbackCategory", "FeedbackStatus",
    "Experience", "ExperienceVerificationStatus",
    "Escalation", "EscalationReason", "EscalationStatus",
    "ChatbotSettings",
    "AuditLog",
]
