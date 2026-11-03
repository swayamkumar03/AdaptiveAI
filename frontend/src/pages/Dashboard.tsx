// src/pages/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  MessageSquare,
  HelpCircle,
  CheckCircle2,
  TrendingUp,
  AlertTriangle,
  ThumbsUp,
  ThumbsDown,
  FileText,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  BrainCircuit,
} from 'lucide-react';
import { analyticsApi } from '../api/analytics';
import { AnalyticsOverview, KnowledgeGapItem, QuestionAnalyticsItem } from '../types/api';
import StatCard from '../components/common/StatCard';
import StatusBadge from '../components/common/StatusBadge';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

export const Dashboard: React.FC = () => {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [recentGaps, setRecentGaps] = useState<KnowledgeGapItem[]>([]);
  const [recentQuestions, setRecentQuestions] = useState<QuestionAnalyticsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [overviewData, gapsData, questionsData] = await Promise.all([
        analyticsApi.getOverview(),
        analyticsApi.getKnowledgeGaps(5, 0),
        analyticsApi.getQuestions(5, 0),
      ]);

      setOverview(overviewData);
      setRecentGaps(gapsData.knowledge_gaps);
      setRecentQuestions(questionsData.recent_questions);
    } catch (err: any) {
      console.error('Error fetching dashboard metrics:', err);
      setError(err.response?.data?.detail || 'Failed to fetch dashboard analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return <Loading message="Loading enterprise analytics overview..." fullHeight />;
  }

  if (error) {
    return (
      <div className="py-8">
        <ErrorMessage
          title="Dashboard Unavailable"
          message={error}
          onRetry={fetchDashboardData}
        />
      </div>
    );
  }

  if (!overview) {
    return null;
  }

  const confidencePct = (overview.average_confidence_score * 100).toFixed(1);
  const escalationPct = (overview.escalation_rate * 100).toFixed(1);

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 p-6 sm:p-8 text-white shadow-lg border border-slate-700/60">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center space-x-2 rounded-full bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-400 border border-blue-500/20 mb-3">
            <BrainCircuit className="w-3.5 h-3.5" />
            <span>Continuous Learning Engine Active</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">
            Adaptive Knowledge Intelligence
          </h2>
          <p className="mt-2 text-sm text-slate-300 leading-relaxed">
            Monitor real-time RAG accuracy, low-confidence escalations, customer feedback, and human-verified experiences that refine the AI model's accuracy.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link
              to="/chat"
              className="inline-flex items-center space-x-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-blue-500 transition"
            >
              <MessageSquare className="w-4 h-4" />
              <span>Open AI Chat</span>
            </Link>
            <Link
              to="/experiences"
              className="inline-flex items-center space-x-2 rounded-lg bg-white/10 px-4 py-2 text-xs font-semibold text-white hover:bg-white/15 transition border border-white/10"
            >
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>Review Pending Experiences ({overview.pending_experiences})</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <StatCard
          title="Total Conversations"
          value={overview.total_conversations}
          subtitle="Customer chat sessions"
          icon={<MessageSquare className="h-5 w-5 text-blue-600" />}
        />
        <StatCard
          title="User Questions"
          value={overview.total_user_questions}
          subtitle="Queries processed by RAG"
          icon={<HelpCircle className="h-5 w-5 text-indigo-600" />}
        />
        <StatCard
          title="Assistant Answers"
          value={overview.total_assistant_answers}
          subtitle="AI generated responses"
          icon={<CheckCircle2 className="h-5 w-5 text-emerald-600" />}
        />
        <StatCard
          title="Average Confidence"
          value={`${confidencePct}%`}
          subtitle="Vector retrieval confidence"
          highlight
          icon={<TrendingUp className="h-5 w-5 text-blue-600" />}
        />
        <StatCard
          title="Escalations"
          value={overview.total_escalations}
          subtitle={`${overview.open_escalations} open / in-progress`}
          icon={<AlertTriangle className="h-5 w-5 text-amber-600" />}
        />
        <StatCard
          title="Escalation Rate"
          value={`${escalationPct}%`}
          subtitle="Low-confidence queries"
          icon={<ShieldAlert className="h-5 w-5 text-rose-600" />}
        />
        <StatCard
          title="Positive Feedback"
          value={overview.positive_feedback}
          subtitle="Customer confirmed helpful"
          icon={<ThumbsUp className="h-5 w-5 text-emerald-600" />}
        />
        <StatCard
          title="Negative Feedback"
          value={overview.negative_feedback}
          subtitle="Flags requiring review"
          icon={<ThumbsDown className="h-5 w-5 text-rose-600" />}
        />
        <StatCard
          title="Knowledge Documents"
          value={overview.total_documents}
          subtitle="Ingested vector knowledge"
          icon={<FileText className="h-5 w-5 text-slate-700" />}
        />
        <StatCard
          title="Pending Experiences"
          value={overview.pending_experiences}
          subtitle="Awaiting admin approval"
          highlight={overview.pending_experiences > 0}
          icon={<Sparkles className="h-5 w-5 text-amber-500" />}
        />
        <StatCard
          title="Approved Experiences"
          value={overview.approved_experiences}
          subtitle="Active in vector knowledge"
          icon={<Sparkles className="h-5 w-5 text-emerald-600" />}
        />
        <StatCard
          title="Rejected Experiences"
          value={overview.rejected_experiences}
          subtitle="Discarded corrections"
          icon={<Sparkles className="h-5 w-5 text-slate-400" />}
        />
      </div>

      {/* Two Column Layout: Knowledge Gaps & Recent Questions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Knowledge Gaps Card */}
        <div className="rounded-xl border border-slate-200/80 bg-white p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <ShieldAlert className="w-4 h-4 text-amber-600" />
                <h3 className="text-sm font-bold text-slate-900">Knowledge Gaps (Escalations)</h3>
              </div>
              <Link
                to="/escalations"
                className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center space-x-1"
              >
                <span>View All</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="mt-4 divide-y divide-slate-100">
              {recentGaps.length === 0 ? (
                <p className="text-xs text-slate-500 py-6 text-center">
                  No knowledge gaps or open escalations found.
                </p>
              ) : (
                recentGaps.map((gap) => (
                  <div key={gap.escalation_id} className="py-3 first:pt-0 last:pb-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-xs font-medium text-slate-800 line-clamp-1">
                        {gap.question || 'Customer query'}
                      </p>
                      <StatusBadge status={gap.escalation_status} size="sm" />
                    </div>
                    <div className="mt-1 flex items-center space-x-3 text-[11px] text-slate-500">
                      <span>Reason: {gap.escalation_reason.replace('_', ' ')}</span>
                      {gap.confidence_score !== null && (
                        <span>Confidence: {(gap.confidence_score * 100).toFixed(0)}%</span>
                      )}
                      {gap.experience_created && (
                        <span className="text-emerald-600 font-medium">✓ Experience Linked</span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 mt-4 text-right">
            <Link
              to="/analytics"
              className="text-xs font-medium text-slate-500 hover:text-slate-800 transition"
            >
              Analyze in Depth →
            </Link>
          </div>
        </div>

        {/* Recent Questions Activity */}
        <div className="rounded-xl border border-slate-200/80 bg-white p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <MessageSquare className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900">Recent User Queries</h3>
              </div>
              <Link
                to="/analytics"
                className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center space-x-1"
              >
                <span>Analytics Table</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="mt-4 divide-y divide-slate-100">
              {recentQuestions.length === 0 ? (
                <p className="text-xs text-slate-500 py-6 text-center">
                  No user questions logged yet.
                </p>
              ) : (
                recentQuestions.map((q) => (
                  <div key={q.message_id} className="py-3 first:pt-0 last:pb-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-xs font-medium text-slate-800 line-clamp-1">
                        {q.question}
                      </p>
                      {q.is_escalated ? (
                        <span className="px-2 py-0.5 text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 rounded-full">
                          Escalated
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full">
                          {q.confidence_score !== null
                            ? `${(q.confidence_score * 100).toFixed(0)}%`
                            : 'Answered'}
                        </span>
                      )}
                    </div>
                    {q.answer && (
                      <p className="mt-1 text-[11px] text-slate-500 line-clamp-1 italic">
                        "{q.answer}"
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 mt-4 text-right">
            <Link
              to="/chat"
              className="text-xs font-medium text-blue-600 hover:text-blue-700 font-semibold"
            >
              Start New Chat Conversation →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
export default Dashboard;
