// src/pages/Escalations.tsx
import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  UserCheck,
  CheckCircle2,
  Clock,
  MessageSquare,
  Sparkles,
  HelpCircle,
  FileCheck,
  X,
  History,
} from 'lucide-react';
import { escalationsApi } from '../api/escalations';
import { EscalationItem } from '../types/api';
import StatusBadge from '../components/common/StatusBadge';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

export const Escalations: React.FC = () => {
  const [escalations, setEscalations] = useState<EscalationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter
  const [statusFilter, setStatusFilter] = useState<string>('');

  // Action states
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  // Resolve Modal state
  const [resolveModal, setResolveModal] = useState<{ id: string; question: string } | null>(null);
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [createExperience, setCreateExperience] = useState(true);
  const [resolveLoading, setResolveLoading] = useState(false);

  // Details & History Modal
  const [selectedDetails, setSelectedDetails] = useState<EscalationItem | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  const fetchEscalations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await escalationsApi.listEscalations(statusFilter || undefined);
      setEscalations(data);
    } catch (err: any) {
      console.error('Error fetching escalations:', err);
      setError(err.response?.data?.detail || 'Failed to retrieve escalations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEscalations();
  }, [statusFilter]);

  const handleAssignToMe = async (escalationId: string) => {
    try {
      setActionLoadingId(escalationId);
      await escalationsApi.assignEscalation(escalationId);
      await fetchEscalations();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to assign escalation.');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleOpenResolve = (esc: EscalationItem) => {
    setResolveModal({
      id: esc.id,
      question: esc.customer_question || 'Customer query',
    });
    setResolutionNotes('');
    setCreateExperience(true);
  };

  const handleResolveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resolveModal || !resolutionNotes.trim()) return;

    try {
      setResolveLoading(true);
      await escalationsApi.resolveEscalation(
        resolveModal.id,
        resolutionNotes,
        createExperience
      );
      setResolveModal(null);
      setResolutionNotes('');
      await fetchEscalations();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to resolve escalation.');
    } finally {
      setResolveLoading(false);
    }
  };

  const handleViewHistory = async (id: string) => {
    try {
      setDetailsLoading(true);
      const details = await escalationsApi.getEscalation(id);
      setSelectedDetails(details);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to fetch conversation history.');
    } finally {
      setDetailsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-xl font-bold tracking-tight text-slate-900">
              Human Escalations Queue
            </h2>
            <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-[10px] font-bold text-amber-800 uppercase">
              Triage & Support
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Queries with low retrieval confidence are automatically escalated for human resolution. Resolving escalations creates Verified Experiences.
          </p>
        </div>

        {/* Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:outline-hidden self-start sm:self-auto"
        >
          <option value="">All Statuses</option>
          <option value="OPEN">Open</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="RESOLVED">Resolved</option>
        </select>
      </div>

      {/* Main List */}
      {loading ? (
        <Loading message="Fetching escalations queue..." />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchEscalations} />
      ) : escalations.length === 0 ? (
        <div className="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-xs">
          <CheckCircle2 className="mx-auto h-12 w-12 text-emerald-400 mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No escalations in queue</h3>
          <p className="mt-1 text-xs text-slate-500 max-w-sm mx-auto">
            All customer inquiries were answered with high confidence. New low-confidence queries will automatically populate here.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {escalations.map((esc) => (
            <div
              key={esc.id}
              className={`rounded-2xl border bg-white p-5 shadow-xs transition hover:border-slate-300 ${
                esc.status === 'OPEN'
                  ? 'border-amber-300/80 bg-amber-50/15'
                  : 'border-slate-200/80'
              }`}
            >
              {/* Header Row */}
              <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
                <div className="flex items-center space-x-2">
                  <StatusBadge status={esc.status} />
                  <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-600">
                    Reason: {esc.reason.replace('_', ' ')}
                  </span>
                </div>

                <div className="flex items-center space-x-3 text-xs text-slate-400">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-3.5 h-3.5" />
                    <span>
                      {esc.created_at
                        ? new Date(esc.created_at).toLocaleString()
                        : 'Unknown date'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Inquiry & AI Response */}
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                {/* Customer Question */}
                <div className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5">
                  <div className="flex items-center space-x-1.5 font-semibold text-slate-700 mb-1">
                    <HelpCircle className="w-3.5 h-3.5 text-blue-500" />
                    <span>Customer Query</span>
                  </div>
                  <p className="text-slate-900 font-semibold leading-relaxed">
                    {esc.customer_question || 'No question text available.'}
                  </p>
                </div>

                {/* AI Response before escalation */}
                <div className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5">
                  <div className="flex items-center space-x-1.5 font-semibold text-slate-700 mb-1">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                    <span>AI Low-Confidence Response</span>
                  </div>
                  <p className="text-slate-600 leading-relaxed italic line-clamp-3">
                    {esc.ai_answer || 'Response was triggered for human intervention.'}
                  </p>
                </div>
              </div>

              {/* Assignment & Resolution metadata */}
              <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500 pt-2 border-t border-slate-100">
                <div className="flex items-center space-x-2">
                  <UserCheck className="w-4 h-4 text-slate-400" />
                  <span>
                    Assigned Agent:{' '}
                    <strong className="text-slate-700 font-semibold">
                      {esc.assigned_agent_name || 'Unassigned'}
                    </strong>
                  </span>
                </div>

                {esc.resolved_at && (
                  <div className="flex items-center space-x-1 text-emerald-600 font-medium">
                    <FileCheck className="w-3.5 h-3.5" />
                    <span>
                      Resolved on {new Date(esc.resolved_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>

              {/* Resolution Notes Display if already resolved */}
              {esc.resolution_notes && (
                <div className="mt-3 rounded-xl border border-emerald-200 bg-emerald-50/60 p-3.5 text-xs text-emerald-950">
                  <span className="font-bold block text-emerald-800 mb-1">
                    Human Resolution Notes:
                  </span>
                  <p className="leading-relaxed">{esc.resolution_notes}</p>
                </div>
              )}

              {/* Actions Toolbar */}
              <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
                <button
                  onClick={() => handleViewHistory(esc.id)}
                  disabled={detailsLoading}
                  className="inline-flex items-center space-x-1.5 text-xs font-semibold text-blue-600 hover:text-blue-700 transition cursor-pointer"
                >
                  <History className="w-3.5 h-3.5" />
                  <span>View Full Thread Context</span>
                </button>

                <div className="flex items-center space-x-2">
                  {esc.status === 'OPEN' && (
                    <button
                      onClick={() => handleAssignToMe(esc.id)}
                      disabled={actionLoadingId === esc.id}
                      className="inline-flex items-center space-x-1.5 rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition cursor-pointer"
                    >
                      <UserCheck className="w-3.5 h-3.5" />
                      <span>{actionLoadingId === esc.id ? 'Assigning...' : 'Assign to Me'}</span>
                    </button>
                  )}

                  {esc.status !== 'RESOLVED' && (
                    <button
                      onClick={() => handleOpenResolve(esc)}
                      className="inline-flex items-center space-x-1.5 rounded-lg bg-emerald-600 px-4 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-emerald-500 transition cursor-pointer"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Resolve Escalation</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Resolution Modal */}
      {resolveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl border border-slate-200">
            <h3 className="text-base font-bold text-slate-900">
              Resolve Customer Escalation
            </h3>
            <p className="mt-1 text-xs text-slate-500 leading-relaxed">
              Provide factual resolution notes. This will mark the conversation as resolved and optionally teach AdaptiveAI via a new Verified Experience.
            </p>

            <form onSubmit={handleResolveSubmit} className="mt-4 space-y-4">
              <div className="rounded-lg bg-slate-50 border border-slate-200 p-3 text-xs">
                <span className="font-semibold text-slate-600 block mb-1">Customer Query:</span>
                <p className="text-slate-800 font-medium">{resolveModal.question}</p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Resolution Notes / Ground Truth *
                </label>
                <textarea
                  rows={4}
                  required
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  placeholder="Explain the verified resolution or policy detail..."
                  className="w-full rounded-lg border border-slate-300 p-2.5 text-xs focus:border-blue-500 focus:outline-hidden"
                />
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="create-exp-toggle"
                  checked={createExperience}
                  onChange={(e) => setCreateExperience(e.target.checked)}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 h-4 w-4"
                />
                <label htmlFor="create-exp-toggle" className="text-xs font-medium text-slate-700 cursor-pointer">
                  Automatically create a <b>Pending Experience</b> for admin verification
                </label>
              </div>

              <div className="flex justify-end space-x-2 pt-3">
                <button
                  type="button"
                  onClick={() => setResolveModal(null)}
                  disabled={resolveLoading}
                  className="rounded-lg border border-slate-300 px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={resolveLoading}
                  className="rounded-lg bg-emerald-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-emerald-500 cursor-pointer"
                >
                  {resolveLoading ? 'Resolving...' : 'Confirm Resolution'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Conversation History Modal */}
      {selectedDetails && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="w-full max-w-2xl max-h-[85vh] rounded-2xl bg-white p-6 shadow-2xl border border-slate-200 flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <div className="flex items-center space-x-2">
                <History className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  Escalation Conversation Thread
                </h3>
              </div>
              <button
                onClick={() => setSelectedDetails(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto py-4 space-y-3">
              {selectedDetails.conversation_history &&
              selectedDetails.conversation_history.length > 0 ? (
                selectedDetails.conversation_history.map((msg) => (
                  <div
                    key={msg.id}
                    className={`p-3.5 rounded-xl text-xs ${
                      msg.role.toUpperCase() === 'USER'
                        ? 'bg-blue-50 border border-blue-100 text-blue-950 ml-6'
                        : 'bg-slate-50 border border-slate-200 text-slate-800 mr-6'
                    }`}
                  >
                    <div className="flex items-center justify-between font-semibold mb-1 text-[11px] text-slate-500 uppercase">
                      <span>{msg.role}</span>
                      {msg.confidence_score !== null && msg.confidence_score !== undefined && (
                        <span>Confidence: {(msg.confidence_score * 100).toFixed(0)}%</span>
                      )}
                    </div>
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                ))
              ) : (
                <p className="text-center py-8 text-xs text-slate-500">
                  No additional conversation messages logged.
                </p>
              )}
            </div>

            <div className="pt-3 border-t border-slate-200 text-right">
              <button
                onClick={() => setSelectedDetails(null)}
                className="rounded-lg bg-slate-900 px-4 py-1.5 text-xs font-semibold text-white hover:bg-slate-800"
              >
                Close Thread
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default Escalations;
