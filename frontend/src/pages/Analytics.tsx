// src/pages/Analytics.tsx
import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  HelpCircle,
  ThumbsUp,
  ShieldAlert,
  Activity,
  Layers,
  Sparkles,
  Info,
  Calendar,
  RefreshCw,
  TrendingUp,
} from 'lucide-react';
import { analyticsApi } from '../api/analytics';
import {
  AccuracyAnalyticsResponse,
  AnalyticsOverview,
  FeedbackAnalyticsResponse,
  KnowledgeGapsResponse,
  QuestionsAnalyticsResponse,
} from '../types/api';
import StatCard from '../components/common/StatCard';
import StatusBadge from '../components/common/StatusBadge';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

export const Analytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'questions' | 'feedback' | 'gaps' | 'reliability'>(
    'overview'
  );

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Analytics responses from all 5 endpoints
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [questions, setQuestions] = useState<QuestionsAnalyticsResponse | null>(null);
  const [feedback, setFeedback] = useState<FeedbackAnalyticsResponse | null>(null);
  const [knowledgeGaps, setKnowledgeGaps] = useState<KnowledgeGapsResponse | null>(null);
  const [accuracy, setAccuracy] = useState<AccuracyAnalyticsResponse | null>(null);

  const fetchAllAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const [overviewRes, questionsRes, feedbackRes, gapsRes, accuracyRes] = await Promise.all([
        analyticsApi.getOverview(),
        analyticsApi.getQuestions(30, 0),
        analyticsApi.getFeedback(),
        analyticsApi.getKnowledgeGaps(30, 0),
        analyticsApi.getAccuracy(),
      ]);

      setOverview(overviewRes);
      setQuestions(questionsRes);
      setFeedback(feedbackRes);
      setKnowledgeGaps(gapsRes);
      setAccuracy(accuracyRes);
    } catch (err: any) {
      console.error('Error fetching analytics:', err);
      setError(err.response?.data?.detail || 'Failed to load enterprise analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllAnalytics();
  }, []);

  if (loading) {
    return <Loading message="Computing real-time analytics aggregations..." fullHeight />;
  }

  if (error) {
    return (
      <div className="py-8">
        <ErrorMessage title="Analytics Unavailable" message={error} onRetry={fetchAllAnalytics} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900">
            Analytics & System Intelligence
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            Enterprise observability across conversations, feedback loop velocity, and AI reliability indicators.
          </p>
        </div>

        <button
          onClick={fetchAllAnalytics}
          className="inline-flex items-center space-x-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className="h-3.5 w-3.5 text-slate-500" />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 space-x-2 sm:space-x-6 overflow-x-auto text-xs font-semibold">
        {[
          { key: 'overview', label: 'Overview Metrics', icon: BarChart3 },
          { key: 'questions', label: 'Questions Log', icon: HelpCircle },
          { key: 'feedback', label: 'Feedback & Categories', icon: ThumbsUp },
          { key: 'gaps', label: 'Knowledge Gaps', icon: ShieldAlert },
          { key: 'reliability', label: 'AI Reliability Metrics', icon: Activity },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center space-x-2 pb-3 pt-1 border-b-2 whitespace-nowrap transition cursor-pointer ${
                activeTab === tab.key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* ==================================================================== */}
      {/* TAB 1: OVERVIEW */}
      {/* ==================================================================== */}
      {activeTab === 'overview' && overview && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Conversations"
              value={overview.total_conversations}
              subtitle="Total customer threads"
            />
            <StatCard
              title="Questions Asked"
              value={overview.total_user_questions}
              subtitle="User inputs parsed"
            />
            <StatCard
              title="Answers Delivered"
              value={overview.total_assistant_answers}
              subtitle="AI synthesized outputs"
            />
            <StatCard
              title="Average Confidence"
              value={`${(overview.average_confidence_score * 100).toFixed(1)}%`}
              subtitle="Vector similarity proxy"
              highlight
            />
            <StatCard
              title="Escalated Answers"
              value={overview.total_escalated_answers}
              subtitle={`${(overview.escalation_rate * 100).toFixed(1)}% escalation rate`}
            />
            <StatCard
              title="Positive Feedback"
              value={overview.positive_feedback}
              subtitle="Helpful responses"
            />
            <StatCard
              title="Negative Feedback"
              value={overview.negative_feedback}
              subtitle="Flagged by customers"
            />
            <StatCard
              title="Ingested Documents"
              value={overview.total_documents}
              subtitle="pgvector knowledge base"
            />
          </div>

          {/* Adaptive Learning Progress */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 mb-2">
              Adaptive Feedback Loop Funnel
            </h3>
            <p className="text-xs text-slate-500 mb-6">
              Track how negative user feedback and human support resolutions convert into persistent memory experiences.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
              <div className="rounded-xl border border-amber-200 bg-amber-50/50 p-4">
                <span className="text-2xl font-bold text-amber-700">
                  {overview.pending_experiences}
                </span>
                <span className="block text-xs font-semibold text-slate-700 mt-1">
                  Pending Experiences
                </span>
                <span className="text-[11px] text-slate-500">Awaiting admin sign-off</span>
              </div>

              <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-4">
                <span className="text-2xl font-bold text-emerald-700">
                  {overview.approved_experiences}
                </span>
                <span className="block text-xs font-semibold text-slate-700 mt-1">
                  Approved & Embedded
                </span>
                <span className="text-[11px] text-slate-500">Active in vector retrieval</span>
              </div>

              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <span className="text-2xl font-bold text-slate-600">
                  {overview.rejected_experiences}
                </span>
                <span className="block text-xs font-semibold text-slate-700 mt-1">
                  Rejected Corrections
                </span>
                <span className="text-[11px] text-slate-500">Prevented from model memory</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB 2: QUESTIONS */}
      {/* ==================================================================== */}
      {activeTab === 'questions' && questions && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatCard
              title="Total Questions"
              value={questions.total_questions}
              subtitle="All time logged queries"
            />
            <StatCard
              title="Low Confidence Queries"
              value={questions.low_confidence_count}
              subtitle="Below threshold"
            />
            <StatCard
              title="Escalated to Agent"
              value={questions.escalated_questions}
              subtitle={`${(questions.escalation_rate * 100).toFixed(1)}% of total`}
            />
          </div>

          <div className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-xs">
            <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900">Recent User Queries Table</h3>
              <span className="text-xs text-slate-400">
                Displaying last {questions.recent_questions.length} queries
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="border-b border-slate-200/80 bg-slate-50/70 font-semibold text-slate-600 uppercase tracking-wider text-[11px]">
                  <tr>
                    <th className="py-3 pl-5 pr-3">Question</th>
                    <th className="px-3 py-3">Confidence</th>
                    <th className="px-3 py-3">Escalated</th>
                    <th className="px-3 py-3">Sources</th>
                    <th className="py-3 pl-3 pr-5 text-right">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                  {questions.recent_questions.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-slate-400">
                        No questions recorded in database.
                      </td>
                    </tr>
                  ) : (
                    questions.recent_questions.map((q) => (
                      <tr key={q.message_id} className="hover:bg-slate-50/60 transition">
                        <td className="py-3 pl-5 pr-3 max-w-md">
                          <p className="font-semibold text-slate-900 line-clamp-1">{q.question}</p>
                          {q.answer && (
                            <p className="text-[11px] text-slate-500 line-clamp-1 italic mt-0.5">
                              "{q.answer}"
                            </p>
                          )}
                        </td>
                        <td className="px-3 py-3">
                          {q.confidence_score !== null ? (
                            <span
                              className={`inline-flex px-2 py-0.5 rounded font-semibold text-[11px] ${
                                q.confidence_score >= 0.75
                                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                  : 'bg-amber-50 text-amber-700 border border-amber-200'
                              }`}
                            >
                              {(q.confidence_score * 100).toFixed(0)}%
                            </span>
                          ) : (
                            <span className="text-slate-400">N/A</span>
                          )}
                        </td>
                        <td className="px-3 py-3">
                          {q.is_escalated ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                              YES
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600">
                              NO
                            </span>
                          )}
                        </td>
                        <td className="px-3 py-3 text-slate-600">{q.sources_count} chunks</td>
                        <td className="py-3 pl-3 pr-5 text-right text-slate-400 whitespace-nowrap">
                          {q.created_at ? new Date(q.created_at).toLocaleDateString() : 'N/A'}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB 3: FEEDBACK */}
      {/* ==================================================================== */}
      {activeTab === 'feedback' && feedback && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Positive Rate"
              value={`${(feedback.positive_rate * 100).toFixed(1)}%`}
              subtitle={`${feedback.positive_count} positive ratings`}
              icon={<ThumbsUp className="w-5 h-5 text-emerald-600" />}
            />
            <StatCard
              title="Negative Rate"
              value={`${(feedback.negative_rate * 100).toFixed(1)}%`}
              subtitle={`${feedback.negative_count} negative ratings`}
            />
            <StatCard
              title="Corrections Submitted"
              value={feedback.user_corrections_submitted}
              subtitle={`${(feedback.user_correction_rate * 100).toFixed(0)}% of negative feedback`}
            />
            <StatCard
              title="Reviewed"
              value={feedback.reviewed_count}
              subtitle={`${feedback.pending_count} pending review`}
            />
          </div>

          {/* Category Breakdown */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 mb-1">
              Negative Feedback Categorization
            </h3>
            <p className="text-xs text-slate-500 mb-6">
              Distribution of customer-reported reasons for answer deficiencies.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(feedback.category_breakdown).map(([cat, count]) => (
                <div key={cat} className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-700">
                      {cat.replace('_', ' ')}
                    </span>
                    <span className="text-lg font-bold text-slate-900">{count}</span>
                  </div>
                  <div className="mt-2 w-full bg-slate-200 rounded-full h-1.5">
                    <div
                      className="bg-blue-600 h-1.5 rounded-full"
                      style={{
                        width: `${
                          feedback.total_feedback
                            ? Math.min(100, (count / feedback.total_feedback) * 100)
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB 4: KNOWLEDGE GAPS */}
      {/* ==================================================================== */}
      {activeTab === 'gaps' && knowledgeGaps && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatCard
              title="Total Knowledge Gaps"
              value={knowledgeGaps.total_knowledge_gaps}
              subtitle="Escalated query events"
            />
            <StatCard
              title="Unresolved Gaps"
              value={knowledgeGaps.unresolved_gaps}
              subtitle="Pending agent action"
            />
            <StatCard
              title="Experiences Created"
              value={knowledgeGaps.experiences_created_count}
              subtitle="Linked human resolutions"
              highlight
            />
          </div>

          <div className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-xs">
            <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900">Knowledge Gap Triage Log</h3>
              <span className="text-xs text-slate-400">
                {knowledgeGaps.knowledge_gaps.length} items logged
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="border-b border-slate-200/80 bg-slate-50/70 font-semibold text-slate-600 uppercase tracking-wider text-[11px]">
                  <tr>
                    <th className="py-3 pl-5 pr-3">Query</th>
                    <th className="px-3 py-3">Confidence</th>
                    <th className="px-3 py-3">Escalation Status</th>
                    <th className="px-3 py-3">Resolution</th>
                    <th className="px-3 py-3">Experience</th>
                    <th className="py-3 pl-3 pr-5 text-right">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                  {knowledgeGaps.knowledge_gaps.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-slate-400">
                        No knowledge gaps identified.
                      </td>
                    </tr>
                  ) : (
                    knowledgeGaps.knowledge_gaps.map((gap) => (
                      <tr key={gap.escalation_id} className="hover:bg-slate-50/60 transition">
                        <td className="py-3 pl-5 pr-3 max-w-xs sm:max-w-sm">
                          <p className="font-semibold text-slate-900 truncate">
                            {gap.question || 'Unspecified Query'}
                          </p>
                          <span className="text-[10px] text-slate-400">
                            Reason: {gap.escalation_reason}
                          </span>
                        </td>
                        <td className="px-3 py-3">
                          {gap.confidence_score !== null
                            ? `${(gap.confidence_score * 100).toFixed(0)}%`
                            : 'N/A'}
                        </td>
                        <td className="px-3 py-3">
                          <StatusBadge status={gap.escalation_status} />
                        </td>
                        <td className="px-3 py-3 max-w-xs truncate text-slate-600">
                          {gap.resolution_notes ? (
                            <span className="text-emerald-700 font-medium">
                              "{gap.resolution_notes}"
                            </span>
                          ) : (
                            <span className="text-slate-400 italic">Unresolved</span>
                          )}
                        </td>
                        <td className="px-3 py-3">
                          {gap.experience_created ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                              ✓ {gap.experience_status || 'CREATED'}
                            </span>
                          ) : (
                            <span className="text-slate-400 text-[11px]">—</span>
                          )}
                        </td>
                        <td className="py-3 pl-3 pr-5 text-right text-slate-400 whitespace-nowrap">
                          {gap.created_at ? new Date(gap.created_at).toLocaleDateString() : 'N/A'}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ==================================================================== */}
      {/* TAB 5: AI RELIABILITY METRICS */}
      {/* ==================================================================== */}
      {activeTab === 'reliability' && accuracy && (
        <div className="space-y-6">
          {/* Important Academic & Industry Disclosure Alert */}
          <div className="rounded-2xl border border-blue-200 bg-blue-50/80 p-5 text-xs text-blue-900 shadow-xs">
            <div className="flex items-start space-x-3">
              <Info className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-blue-950 text-sm">
                  AI Reliability Metrics Specification
                </h4>
                <p className="mt-1 leading-relaxed text-blue-800">
                  {accuracy.description}
                </p>
                <p className="mt-1.5 text-blue-700 italic font-medium">
                  Note: Ground-truth model evaluation metrics require a human-annotated benchmark dataset. These live metrics measure production retrieval confidence and operational feedback health.
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Confidence Score (Avg)"
              value={`${(accuracy.average_confidence_score * 100).toFixed(1)}%`}
              subtitle="Vector similarity proxy"
              highlight
            />
            <StatCard
              title="High Confidence Answers"
              value={accuracy.confidence_distribution.high_confidence_count}
              subtitle={`Score ≥ ${(accuracy.confidence_distribution.high_confidence_threshold * 100).toFixed(0)}%`}
            />
            <StatCard
              title="Low Confidence Answers"
              value={accuracy.confidence_distribution.low_confidence_count}
              subtitle={`Score < ${(accuracy.confidence_distribution.low_confidence_threshold * 100).toFixed(0)}%`}
            />
            <StatCard
              title="Production Escalation Rate"
              value={`${(accuracy.escalation_metrics.escalation_rate * 100).toFixed(1)}%`}
              subtitle={`${accuracy.escalation_metrics.escalated_answer_count} escalated answers`}
            />
          </div>

          {/* Operational Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
              <h3 className="text-sm font-bold text-slate-900 mb-3">
                Customer Feedback Sentiment
              </h3>
              <div className="space-y-4 text-xs">
                <div>
                  <div className="flex justify-between font-semibold mb-1">
                    <span className="text-emerald-700">Positive Feedback Satisfaction</span>
                    <span>{(accuracy.feedback_metrics.positive_feedback_rate * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div
                      className="bg-emerald-500 h-2 rounded-full"
                      style={{
                        width: `${accuracy.feedback_metrics.positive_feedback_rate * 100}%`,
                      }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between font-semibold mb-1">
                    <span className="text-rose-700">Negative Feedback Rate</span>
                    <span>{(accuracy.feedback_metrics.negative_feedback_rate * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div
                      className="bg-rose-500 h-2 rounded-full"
                      style={{
                        width: `${accuracy.feedback_metrics.negative_feedback_rate * 100}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
              <h3 className="text-sm font-bold text-slate-900 mb-3">
                Continuous Learning Velocity
              </h3>
              <div className="space-y-3 text-xs">
                <div className="flex items-center justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-600">Reviewed Negative Feedback</span>
                  <span className="font-bold text-slate-900">
                    {accuracy.adaptive_learning_metrics.reviewed_negative_feedback_count}
                  </span>
                </div>
                <div className="flex items-center justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-600">Verified Experience Corrections</span>
                  <span className="font-bold text-emerald-600">
                    {accuracy.adaptive_learning_metrics.verified_correction_count}
                  </span>
                </div>
                <div className="flex items-center justify-between py-1.5">
                  <span className="text-slate-600">Pending Experiences in Review</span>
                  <span className="font-bold text-amber-600">
                    {accuracy.adaptive_learning_metrics.pending_experiences_count}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default Analytics;
