// src/pages/Chat.tsx
import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  User,
  AlertTriangle,
  FileText,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
  PlusCircle,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Check,
} from 'lucide-react';
import { chatApi } from '../api/chat';
import { feedbackApi } from '../api/feedback';
import { ChatMessage } from '../types/api';

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});

  // Feedback modal / dialog state
  const [feedbackDialog, setFeedbackDialog] = useState<{
    messageId: string;
    rating: 'POSITIVE' | 'NEGATIVE';
  } | null>(null);
  const [feedbackCategory, setFeedbackCategory] = useState<
    'INCORRECT' | 'INCOMPLETE' | 'MISUNDERSTOOD' | 'OTHER'
  >('INCORRECT');
  const [userCorrection, setUserCorrection] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState<Record<string, 'POSITIVE' | 'NEGATIVE'>>({});
  const [feedbackLoading, setFeedbackLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleStartNewChat = () => {
    setConversationId(undefined);
    setMessages([]);
    setExpandedSources({});
  };

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = input.trim();
    if (!query || loading) return;

    const tempUserMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: query,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatApi.sendMessage(query, conversationId);

      // Save conversation ID for thread continuity
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const assistantMsg: ChatMessage = {
        id: response.assistant_message_id,
        role: 'assistant',
        content: response.answer,
        confidence_score: response.confidence_score,
        is_escalated: response.is_escalated,
        sources: response.sources,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.error('Chat error:', err);
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        role: 'system',
        content:
          err.response?.data?.detail ||
          'Unable to connect to AI server. Please verify the backend is running.',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const toggleSource = (msgId: string) => {
    setExpandedSources((prev) => ({
      ...prev,
      [msgId]: !prev[msgId],
    }));
  };

  const openFeedback = (messageId: string, rating: 'POSITIVE' | 'NEGATIVE') => {
    if (rating === 'POSITIVE') {
      // Direct positive feedback submission
      submitQuickFeedback(messageId, 'POSITIVE');
    } else {
      // Open dialog for negative feedback with correction
      setFeedbackDialog({ messageId, rating: 'NEGATIVE' });
    }
  };

  const submitQuickFeedback = async (messageId: string, rating: 'POSITIVE') => {
    try {
      await feedbackApi.submitFeedback({
        message_id: messageId,
        rating,
      });
      setFeedbackSubmitted((prev) => ({ ...prev, [messageId]: rating }));
    } catch (err) {
      console.error('Feedback submission error:', err);
    }
  };

  const submitNegativeFeedback = async () => {
    if (!feedbackDialog) return;
    try {
      setFeedbackLoading(true);
      await feedbackApi.submitFeedback({
        message_id: feedbackDialog.messageId,
        rating: 'NEGATIVE',
        feedback_category: feedbackCategory,
        user_correction: userCorrection || undefined,
      });
      setFeedbackSubmitted((prev) => ({
        ...prev,
        [feedbackDialog.messageId]: 'NEGATIVE',
      }));
      setFeedbackDialog(null);
      setUserCorrection('');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to submit feedback.');
    } finally {
      setFeedbackLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8.5rem)] rounded-2xl border border-slate-200/90 bg-white shadow-xs overflow-hidden">
      {/* Left Chat Sidebar: Thread Status */}
      <div className="hidden md:flex w-72 flex-col border-r border-slate-200/80 bg-slate-50/70 p-4">
        <button
          onClick={handleStartNewChat}
          className="flex w-full items-center justify-center space-x-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-blue-500 transition cursor-pointer"
        >
          <PlusCircle className="h-4 w-4" />
          <span>New Conversation</span>
        </button>

        <div className="mt-6 flex-1 overflow-y-auto">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
            Active Session
          </span>

          <div className="mt-2 rounded-xl border border-slate-200/80 bg-white p-3 shadow-xs">
            <div className="flex items-center space-x-2">
              <Bot className="h-4 w-4 text-blue-600" />
              <span className="text-xs font-semibold text-slate-800">
                Adaptive RAG Agent
              </span>
            </div>
            <p className="mt-1 text-[11px] text-slate-500 line-clamp-2">
              {conversationId
                ? `Thread: ${conversationId.substring(0, 16)}...`
                : 'Fresh conversation ready.'}
            </p>
            {conversationId && (
              <div className="mt-2 text-[10px] font-medium text-emerald-600 flex items-center space-x-1">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span>Session in progress</span>
              </div>
            )}
          </div>

          <div className="mt-6 rounded-xl border border-blue-100 bg-blue-50/60 p-3 text-xs text-blue-900">
            <span className="font-semibold block mb-1">Human-in-the-Loop Loop</span>
            <p className="text-[11px] text-blue-700 leading-relaxed">
              If confidence drops below threshold, questions are automatically escalated to company representatives. Negative feedback with corrections creates Verified Experiences.
            </p>
          </div>
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="flex flex-1 flex-col bg-white">
        {/* Messages Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center text-center max-w-md mx-auto py-12">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 border border-blue-100 mb-4 shadow-xs">
                <Bot className="h-8 w-8" />
              </div>
              <h3 className="text-base font-bold text-slate-900">
                AdaptiveAI Enterprise Assistant
              </h3>
              <p className="mt-1.5 text-xs text-slate-500 leading-relaxed">
                Ask questions against company documents and verified experiences. Responses include source citations and confidence scores.
              </p>

              <div className="mt-6 grid w-full gap-2 text-left">
                <button
                  onClick={() => setInput('What does AdaptiveAI do?')}
                  className="rounded-xl border border-slate-200/80 p-3 text-xs text-slate-700 hover:border-blue-400 hover:bg-blue-50/30 transition text-left cursor-pointer"
                >
                  "What does AdaptiveAI do?"
                </button>
                <button
                  onClick={() => setInput('What is the return or refund policy?')}
                  className="rounded-xl border border-slate-200/80 p-3 text-xs text-slate-700 hover:border-blue-400 hover:bg-blue-50/30 transition text-left cursor-pointer"
                >
                  "What is the return or refund policy?"
                </button>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-3xl ${
                  msg.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
                }`}
              >
                {/* Avatar */}
                <div
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
                    msg.role === 'user'
                      ? 'bg-slate-900 text-white'
                      : msg.role === 'assistant'
                      ? 'bg-blue-600 text-white'
                      : 'bg-rose-500 text-white'
                  }`}
                >
                  {msg.role === 'user' ? (
                    <User className="h-4 w-4" />
                  ) : msg.role === 'assistant' ? (
                    <Bot className="h-4 w-4" />
                  ) : (
                    <AlertTriangle className="h-4 w-4" />
                  )}
                </div>

                {/* Message Bubble */}
                <div
                  className={`flex flex-col space-y-2 rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-xs ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-tr-xs'
                      : msg.role === 'assistant'
                      ? 'bg-slate-50 border border-slate-200/80 text-slate-900 rounded-tl-xs'
                      : 'bg-rose-50 border border-rose-200 text-rose-800'
                  }`}
                >
                  {/* Content */}
                  <div className="whitespace-pre-wrap">{msg.content}</div>

                  {/* Escalation notice if applicable */}
                  {msg.is_escalated && (
                    <div className="mt-2 flex items-center space-x-2 rounded-lg border border-amber-300/80 bg-amber-50 px-3 py-2 text-xs font-medium text-amber-900">
                      <ShieldAlert className="h-4 w-4 text-amber-600 shrink-0" />
                      <span>
                        This question has been escalated to a company representative.
                      </span>
                    </div>
                  )}

                  {/* Confidence & Sources Footer (Assistant only) */}
                  {msg.role === 'assistant' && (
                    <div className="pt-2 border-t border-slate-200/60 mt-1 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
                      <div className="flex items-center space-x-2">
                        {msg.confidence_score !== undefined && msg.confidence_score !== null && (
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold ${
                              msg.confidence_score >= 0.75
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : 'bg-amber-50 text-amber-700 border border-amber-200'
                            }`}
                          >
                            Confidence: {(msg.confidence_score * 100).toFixed(0)}%
                          </span>
                        )}

                        {msg.sources && msg.sources.length > 0 && (
                          <button
                            onClick={() => toggleSource(msg.id)}
                            className="inline-flex items-center space-x-1 text-slate-600 hover:text-blue-600 font-medium transition cursor-pointer"
                          >
                            <FileText className="w-3.5 h-3.5 text-blue-500" />
                            <span>{msg.sources.length} Sources</span>
                            {expandedSources[msg.id] ? (
                              <ChevronUp className="w-3.5 h-3.5" />
                            ) : (
                              <ChevronDown className="w-3.5 h-3.5" />
                            )}
                          </button>
                        )}
                      </div>

                      {/* Feedback buttons */}
                      <div className="flex items-center space-x-1">
                        {feedbackSubmitted[msg.id] ? (
                          <span className="text-[11px] text-emerald-600 flex items-center space-x-1">
                            <Check className="w-3 h-3" />
                            <span>Feedback recorded</span>
                          </span>
                        ) : (
                          <>
                            <button
                              onClick={() => openFeedback(msg.id, 'POSITIVE')}
                              className="p-1 rounded text-slate-400 hover:text-emerald-600 hover:bg-slate-200/60 transition cursor-pointer"
                              title="Helpful response"
                            >
                              <ThumbsUp className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => openFeedback(msg.id, 'NEGATIVE')}
                              className="p-1 rounded text-slate-400 hover:text-rose-600 hover:bg-slate-200/60 transition cursor-pointer"
                              title="Report inaccurate or incomplete answer"
                            >
                              <ThumbsDown className="w-3.5 h-3.5" />
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Expandable Sources Drawer */}
                  {expandedSources[msg.id] && msg.sources && (
                    <div className="mt-2 pt-2 border-t border-slate-200 space-y-2">
                      <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                        Citations & Retrieved Chunks
                      </span>
                      {msg.sources.map((s, idx) => (
                        <div
                          key={idx}
                          className="rounded-lg border border-slate-200 bg-white p-2.5 text-xs text-slate-700 shadow-2xs"
                        >
                          <div className="flex items-center justify-between font-semibold text-slate-800">
                            <span className="truncate">
                              {s.filename || s.title || `Source ${idx + 1}`}
                            </span>
                            {s.similarity_score !== undefined && (
                              <span className="text-[10px] text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">
                                Score: {(s.similarity_score * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                          {(s.text || s.content_preview) && (
                            <p className="mt-1 text-[11px] text-slate-500 line-clamp-3 italic">
                              "{s.text || s.content_preview}"
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {loading && (
            <div className="flex items-center space-x-3 text-slate-500 mr-auto max-w-sm rounded-2xl bg-slate-50 border border-slate-200/80 px-4 py-3">
              <Bot className="h-4 w-4 animate-spin text-blue-600" />
              <span className="text-xs font-medium">
                Searching documents & synthesizing answer...
              </span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="border-t border-slate-200/80 p-4 bg-white">
          <form onSubmit={handleSend} className="flex items-center space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about enterprise documents or verified policies..."
              disabled={loading}
              className="flex-1 rounded-xl border border-slate-300 bg-slate-50/60 px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-hidden transition"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-xs hover:bg-blue-500 disabled:opacity-40 transition cursor-pointer"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>

      {/* Negative Feedback Modal Dialog */}
      {feedbackDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center space-x-2 text-rose-600 mb-2">
              <Sparkles className="w-5 h-5" />
              <h3 className="text-base font-bold text-slate-900">
                Help AdaptiveAI Learn
              </h3>
            </div>
            <p className="text-xs text-slate-500 mb-4 leading-relaxed">
              Your correction is queued as a <b>Pending Experience</b>. Once reviewed by an administrator, the AI incorporates it immediately.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Feedback Category
                </label>
                <select
                  value={feedbackCategory}
                  onChange={(e) => setFeedbackCategory(e.target.value as any)}
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-blue-500 focus:outline-hidden"
                >
                  <option value="INCORRECT">Incorrect Answer</option>
                  <option value="INCOMPLETE">Incomplete Answer</option>
                  <option value="MISUNDERSTOOD">Misunderstood Query</option>
                  <option value="OTHER">Other Issue</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Correct Answer (Optional)
                </label>
                <textarea
                  rows={3}
                  value={userCorrection}
                  onChange={(e) => setUserCorrection(e.target.value)}
                  placeholder="What is the correct factual answer?"
                  className="w-full rounded-lg border border-slate-300 p-2.5 text-xs placeholder-slate-400 focus:border-blue-500 focus:outline-hidden"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setFeedbackDialog(null)}
                  disabled={feedbackLoading}
                  className="rounded-lg border border-slate-300 px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={submitNegativeFeedback}
                  disabled={feedbackLoading}
                  className="rounded-lg bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-blue-500 cursor-pointer"
                >
                  {feedbackLoading ? 'Submitting...' : 'Submit Correction'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default Chat;
