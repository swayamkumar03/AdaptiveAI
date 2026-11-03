// src/types/api.ts
// Comprehensive TypeScript interfaces for AdaptiveAI Frontend

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'SUPER_ADMIN' | 'COMPANY_ADMIN' | 'EMPLOYEE' | 'CUSTOMER';
  company_id: string | null;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  confidence_score?: number | null;
  is_escalated?: boolean;
  sources?: Array<{
    title?: string;
    filename?: string;
    source_type?: string;
    chunk_id?: string;
    similarity_score?: number;
    score?: number;
    chunk_index?: number;
    content_preview?: string;
    text?: string;
    experience_id?: string;
    question?: string;
  }>;
  created_at?: string;
}

export interface ChatResponse {
  conversation_id: string;
  user_message_id: string;
  assistant_message_id: string;
  answer: string;
  sources: Array<{
    title?: string;
    filename?: string;
    source_type?: string;
    chunk_id?: string;
    similarity_score?: number;
    score?: number;
    chunk_index?: number;
    content_preview?: string;
    text?: string;
    experience_id?: string;
    question?: string;
  }>;
  model?: string;
  retrieved_chunks?: number;
  retrieved_experiences?: number;
  confidence_score?: number;
  is_escalated: boolean;
  escalation_id?: string;
  error?: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: 'pdf' | 'docx' | 'txt' | 'csv' | 'md';
  status: 'PENDING' | 'PROCESSING' | 'READY' | 'FAILED';
  chunk_count: number;
  file_size_bytes: number;
  created_at: string;
  title?: string;
  description?: string;
  error_message?: string;
}

export interface FeedbackItem {
  feedback_id: string;
  message_id: string;
  conversation_id: string | null;
  rating: 'POSITIVE' | 'NEGATIVE';
  feedback_category: 'INCORRECT' | 'INCOMPLETE' | 'MISUNDERSTOOD' | 'OTHER' | 'UNSPECIFIED' | null;
  user_correction: string | null;
  comment: string | null;
  status: 'PENDING' | 'REVIEWED' | 'RESOLVED' | 'DISMISSED';
  user_id: string;
  reviewed_by: string | null;
  created_at: string | null;
  user_question: string | null;
  ai_answer: string | null;
  message_content?: string | null;
}

export interface ExperienceItem {
  id: string;
  company_id: string;
  source_message_id: string | null;
  question: string;
  original_answer: string;
  corrected_answer: string;
  verification_status: 'PENDING' | 'APPROVED' | 'REJECTED';
  verified_by: string | null;
  verified_at: string | null;
  has_embedding: boolean;
  rejection_reason: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface EscalationItem {
  id: string;
  company_id: string;
  conversation_id: string;
  triggering_message_id: string | null;
  assigned_agent_id: string | null;
  assigned_agent_name: string | null;
  reason: 'LOW_CONFIDENCE' | 'USER_REQUESTED' | 'NEGATIVE_FEEDBACK' | 'MANUAL';
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED';
  resolution_notes: string | null;
  resolved_at: string | null;
  created_at: string | null;
  updated_at: string | null;
  customer_question: string | null;
  ai_answer: string | null;
  conversation_history?: Array<{
    id: string;
    role: string;
    content: string;
    confidence_score?: number | null;
    is_escalated?: boolean;
    created_at?: string | null;
  }>;
}

export interface AnalyticsOverview {
  total_conversations: number;
  total_user_questions: number;
  total_assistant_answers: number;
  total_escalated_answers: number;
  total_escalations: number;
  open_escalations: number;
  resolved_escalations: number;
  escalation_rate: number;
  average_confidence_score: number;
  positive_feedback: number;
  negative_feedback: number;
  pending_experiences: number;
  approved_experiences: number;
  rejected_experiences: number;
  total_documents: number;
}

export interface QuestionAnalyticsItem {
  message_id: string;
  conversation_id: string;
  question: string;
  created_at: string | null;
  answer: string | null;
  confidence_score: number | null;
  is_escalated: boolean;
  sources_count: number;
}

export interface QuestionsAnalyticsResponse {
  total_questions: number;
  answered_questions: number;
  escalated_questions: number;
  low_confidence_count: number;
  average_confidence: number;
  escalation_rate: number;
  pagination: { limit: number; offset: number; returned: number };
  recent_questions: QuestionAnalyticsItem[];
}

export interface FeedbackAnalyticsResponse {
  total_feedback: number;
  positive_count: number;
  negative_count: number;
  positive_rate: number;
  negative_rate: number;
  pending_count: number;
  reviewed_count: number;
  resolved_count: number;
  user_corrections_submitted: number;
  user_correction_rate: number;
  category_breakdown: Record<string, number>;
}

export interface KnowledgeGapItem {
  escalation_id: string;
  conversation_id: string;
  triggering_message_id: string | null;
  question: string | null;
  ai_answer: string | null;
  confidence_score: number | null;
  escalation_reason: string;
  escalation_status: string;
  resolution_notes: string | null;
  resolved_at: string | null;
  has_resolution: boolean;
  experience_created: boolean;
  experience_id: string | null;
  experience_status: string | null;
  created_at: string | null;
}

export interface KnowledgeGapsResponse {
  total_knowledge_gaps: number;
  unresolved_gaps: number;
  resolved_gaps: number;
  experiences_created_count: number;
  pagination: { limit: number; offset: number; returned: number };
  knowledge_gaps: KnowledgeGapItem[];
}

export interface AccuracyAnalyticsResponse {
  metric_type: string;
  description: string;
  total_assistant_answers: number;
  average_confidence_score: number;
  confidence_distribution: {
    high_confidence_count: number;
    low_confidence_count: number;
    high_confidence_threshold: number;
    low_confidence_threshold: number;
  };
  feedback_metrics: {
    total_feedback: number;
    positive_feedback_count: number;
    negative_feedback_count: number;
    positive_feedback_rate: number;
    negative_feedback_rate: number;
  };
  escalation_metrics: {
    escalated_answer_count: number;
    escalation_rate: number;
  };
  adaptive_learning_metrics: {
    reviewed_negative_feedback_count: number;
    verified_correction_count: number;
    pending_experiences_count: number;
  };
}

export interface CompanyItem {
  id: string;
  name: string;
  slug: string;
  industry?: string | null;
  description?: string | null;
  website?: string | null;
  is_active: boolean;
  subscription_plan: string;
  logo_url?: string | null;
  user_count?: number;
  document_count?: number;
  conversation_count?: number;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface PlatformOverview {
  total_companies: number;
  active_companies: number;
  inactive_companies: number;
  total_users: number;
  total_user_questions: number;
  total_assistant_answers: number;
  total_documents: number;
  total_escalations: number;
  recent_companies: Array<{
    id: string;
    name: string;
    slug: string;
    industry?: string | null;
    is_active: boolean;
    created_at?: string | null;
  }>;
}

export interface ChatbotSettingsItem {
  id: string;
  company_id: string;
  bot_name: string;
  tone: string;
  response_length: string;
  language: string;
  brand_description?: string | null;
  custom_prompt_addon?: string | null;
  auto_escalate_on_low_confidence: boolean;
}

export interface UserManagementItem {
  id: string;
  email: string;
  full_name: string;
  role: 'SUPER_ADMIN' | 'COMPANY_ADMIN' | 'EMPLOYEE' | 'CUSTOMER';
  company_id: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at?: string | null;
}
