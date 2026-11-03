// src/pages/Feedback.tsx
import React, { useEffect, useState } from 'react';
import {
  ThumbsUp,
  ThumbsDown,
  CheckCircle,
  Clock,
  Sparkles,
  HelpCircle,
  Bot,
} from 'lucide-react';
import { feedbackApi } from '../api/feedback';
import { FeedbackItem } from '../types/api';
import StatusBadge from '../components/common/StatusBadge';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

export const Feedback: React.FC = () => {
  const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [ratingFilter, setRatingFilter] = useState<string>('');
  const [reviewingId, setReviewingId] = useState<string | null>(null);

  const fetchFeedback = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await feedbackApi.listFeedback(
        statusFilter || undefined,
        ratingFilter || undefined
      );
      setFeedbackList(data);
    } catch (err: any) {
      console.error('Error fetching feedback:', err);
      setError(err.response?.data?.detail || 'Failed to load feedback records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeedback();
  }, [statusFilter, ratingFilter]);

  const handleReview = async (feedbackId: string) => {
    try {
      setReviewingId(feedbackId);
      await feedbackApi.reviewFeedback(feedbackId);
      await fetchFeedback();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to review feedback.');
    } finally {
      setReviewingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900">
            User Feedback & Reviews
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            Inspect customer ratings, review flagged inaccuracies, and approve human corrections into the continuous learning pipeline.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 focus:border-blue-500 focus:outline-hidden"
          >
            <option value="">All Statuses</option>
            <option value="PENDING">Pending Review</option>
            <option value="REVIEWED">Reviewed</option>
          </select>

          <select
            value={ratingFilter}
            onChange={(e) => setRatingFilter(e.target.value)}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 focus:border-blue-500 focus:outline-hidden"
          >
            <option value="">All Ratings</option>
            <option value="NEGATIVE">Negative Feedback</option>
            <option value="POSITIVE">Positive Feedback</option>
          </select>
        </div>
      </div>

      {/* Main Content */}
      {loading ? (
        <Loading message="Fetching feedback records..." />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchFeedback} />
      ) : feedbackList.length === 0 ? (
        <div className="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-xs">
          <ThumbsUp className="mx-auto h-12 w-12 text-slate-300 mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No feedback submissions found</h3>
          <p className="mt-1 text-xs text-slate-500 max-w-sm mx-auto">
            When users rate chatbot responses in the chat interface, submissions appear here for administrative verification.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {feedbackList.map((item) => (
            <div
              key={item.feedback_id}
              className={`rounded-2xl border bg-white p-5 shadow-xs transition ${
                item.rating === 'NEGATIVE' && item.status === 'PENDING'
                  ? 'border-amber-300/80 bg-amber-50/10'
                  : 'border-slate-200/80'
              }`}
            >
              {/* Header Row */}
              <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
                <div className="flex items-center space-x-2">
                  <span
                    className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold ${
                      item.rating === 'POSITIVE'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-rose-50 text-rose-700 border border-rose-200'
                    }`}
                  >
                    {item.rating === 'POSITIVE' ? (
                      <ThumbsUp className="w-3.5 h-3.5" />
                    ) : (
                      <ThumbsDown className="w-3.5 h-3.5" />
                    )}
                    <span>{item.rating}</span>
                  </span>

                  {item.feedback_category && (
                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                      {item.feedback_category.replace('_', ' ')}
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-3 text-xs">
                  <div className="flex items-center space-x-1 text-slate-400">
                    <Clock className="w-3.5 h-3.5" />
                    <span>
                      {item.created_at
                        ? new Date(item.created_at).toLocaleString()
                        : 'Unknown date'}
                    </span>
                  </div>
                  <StatusBadge status={item.status} />
                </div>
              </div>

              {/* Context: Question & AI Answer */}
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                {/* Question */}
                <div className="rounded-xl border border-slate-200/70 bg-slate-50/70 p-3.5">
                  <div className="flex items-center space-x-1.5 font-semibold text-slate-700 mb-1">
                    <HelpCircle className="w-3.5 h-3.5 text-blue-500" />
                    <span>User Question</span>
                  </div>
                  <p className="text-slate-800 leading-relaxed font-medium">
                    {item.user_question || 'No question recorded for this message.'}
                  </p>
                </div>

                {/* AI Answer */}
                <div className="rounded-xl border border-slate-200/70 bg-slate-50/70 p-3.5">
                  <div className="flex items-center space-x-1.5 font-semibold text-slate-700 mb-1">
                    <Bot className="w-3.5 h-3.5 text-indigo-500" />
                    <span>AI Assistant Response</span>
                  </div>
                  <p className="text-slate-600 leading-relaxed line-clamp-3">
                    {item.ai_answer || item.message_content || 'Content unavailable.'}
                  </p>
                </div>
              </div>

              {/* User Correction Banner if present */}
              {item.user_correction && (
                <div className="mt-3 rounded-xl border border-blue-200 bg-blue-50/70 p-3.5 text-xs">
                  <div className="flex items-center space-x-1.5 font-semibold text-blue-900 mb-1">
                    <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                    <span>User Provided Correction (Pending Experience Trigger)</span>
                  </div>
                  <p className="text-blue-950 font-medium leading-relaxed">
                    {item.user_correction}
                  </p>
                </div>
              )}

              {item.comment && (
                <div className="mt-2 text-xs text-slate-500 italic">
                  Note: "{item.comment}"
                </div>
              )}

              {/* Review Action */}
              {item.status === 'PENDING' && (
                <div className="mt-4 pt-3 border-t border-slate-100 flex justify-end">
                  <button
                    onClick={() => handleReview(item.feedback_id)}
                    disabled={reviewingId === item.feedback_id}
                    className="inline-flex items-center space-x-1.5 rounded-lg bg-blue-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-blue-500 disabled:opacity-50 transition cursor-pointer shadow-2xs"
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>
                      {reviewingId === item.feedback_id
                        ? 'Reviewing...'
                        : 'Mark as Reviewed'}
                    </span>
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
export default Feedback;
