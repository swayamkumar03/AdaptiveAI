// src/pages/Experiences.tsx
import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  CheckCircle,
  XCircle,
  ShieldCheck,
  Plus,
  HelpCircle,
  Layers,
  Calendar,
  AlertCircle,
} from 'lucide-react';
import { experiencesApi } from '../api/experiences';
import { ExperienceItem } from '../types/api';
import StatusBadge from '../components/common/StatusBadge';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

export const Experiences: React.FC = () => {
  const [experiences, setExperiences] = useState<ExperienceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Status Filter
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  // Action states
  const [processingId, setProcessingId] = useState<string | null>(null);

  // Reject modal state
  const [rejectModal, setRejectModal] = useState<{ id: string } | null>(null);
  const [rejectReason, setRejectReason] = useState('');

  // Manual create modal state
  const [createModal, setCreateModal] = useState(false);
  const [newQuestion, setNewQuestion] = useState('');
  const [newOriginalAnswer, setNewOriginalAnswer] = useState('');
  const [newCorrectedAnswer, setNewCorrectedAnswer] = useState('');
  const [createLoading, setCreateLoading] = useState(false);

  const fetchExperiences = async () => {
    try {
      setLoading(true);
      setError(null);
      const filter = statusFilter === 'ALL' ? undefined : statusFilter;
      const data = await experiencesApi.listExperiences(filter);
      setExperiences(data);
    } catch (err: any) {
      console.error('Error fetching experiences:', err);
      setError(err.response?.data?.detail || 'Failed to retrieve verified experiences.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExperiences();
  }, [statusFilter]);

  const handleApprove = async (id: string) => {
    try {
      setProcessingId(id);
      await experiencesApi.approveExperience(id);
      await fetchExperiences();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to approve experience.');
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async () => {
    if (!rejectModal) return;
    try {
      setProcessingId(rejectModal.id);
      await experiencesApi.rejectExperience(rejectModal.id, rejectReason || undefined);
      setRejectModal(null);
      setRejectReason('');
      await fetchExperiences();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to reject experience.');
    } finally {
      setProcessingId(null);
    }
  };

  const handleManualCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newQuestion || !newCorrectedAnswer) return;

    try {
      setCreateLoading(true);
      await experiencesApi.createExperience({
        question: newQuestion,
        original_answer: newOriginalAnswer || 'N/A',
        corrected_answer: newCorrectedAnswer,
      });
      setCreateModal(false);
      setNewQuestion('');
      setNewOriginalAnswer('');
      setNewCorrectedAnswer('');
      await fetchExperiences();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to manually create experience.');
    } finally {
      setCreateLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-xl font-bold tracking-tight text-slate-900">
              Verified Experiences
            </h2>
            <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-bold text-blue-700 uppercase">
              Adaptive Memory
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Human-in-the-Loop knowledge corrections. Approved experiences override static document chunks and inject high-confidence memory into RAG.
          </p>
        </div>

        <button
          onClick={() => setCreateModal(true)}
          className="inline-flex items-center space-x-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-blue-500 transition cursor-pointer self-start sm:self-auto"
        >
          <Plus className="h-4 w-4" />
          <span>Add Custom Experience</span>
        </button>
      </div>

      {/* Status Filter Tabs */}
      <div className="flex border-b border-slate-200 space-x-6 text-xs font-semibold">
        {['ALL', 'PENDING', 'APPROVED', 'REJECTED'].map((status) => (
          <button
            key={status}
            onClick={() => setStatusFilter(status)}
            className={`pb-3 border-b-2 transition cursor-pointer ${
              statusFilter === status
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            {status}
          </button>
        ))}
      </div>

      {/* Main List */}
      {loading ? (
        <Loading message="Loading verified experience memory store..." />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchExperiences} />
      ) : experiences.length === 0 ? (
        <div className="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-xs">
          <Sparkles className="mx-auto h-12 w-12 text-slate-300 mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No experiences in this category</h3>
          <p className="mt-1 text-xs text-slate-500 max-w-sm mx-auto">
            When users submit corrections or human agents resolve low-confidence escalations, experiences are generated here for administrative review.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {experiences.map((exp) => (
            <div
              key={exp.id}
              className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs transition hover:border-slate-300"
            >
              {/* Header */}
              <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
                <div className="flex items-center space-x-2">
                  <StatusBadge status={exp.verification_status} />
                  {exp.has_embedding && (
                    <span className="inline-flex items-center space-x-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 border border-emerald-200">
                      <Layers className="w-3 h-3" />
                      <span>pgvector Indexed</span>
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-3 text-xs text-slate-400">
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>
                      {exp.created_at
                        ? new Date(exp.created_at).toLocaleDateString()
                        : 'Unknown'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Question */}
              <div className="mt-3">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Target Question
                </span>
                <p className="mt-1 text-xs sm:text-sm font-semibold text-slate-900 leading-snug">
                  {exp.question}
                </p>
              </div>

              {/* Comparison Grid: Original Answer vs Corrected Answer */}
              <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                {/* Original Answer */}
                <div className="rounded-xl border border-rose-100 bg-rose-50/40 p-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-rose-700">
                    Original AI Answer
                  </span>
                  <p className="mt-1 text-slate-700 leading-relaxed italic line-clamp-4">
                    "{exp.original_answer}"
                  </p>
                </div>

                {/* Corrected Verified Answer */}
                <div className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-3">
                  <div className="flex items-center space-x-1 text-emerald-800">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-[10px] font-bold uppercase tracking-wider">
                      Verified Human Truth
                    </span>
                  </div>
                  <p className="mt-1 text-emerald-950 font-medium leading-relaxed">
                    {exp.corrected_answer}
                  </p>
                </div>
              </div>

              {/* Rejection Reason if any */}
              {exp.rejection_reason && (
                <div className="mt-2.5 rounded-lg border border-rose-200 bg-rose-50 p-2.5 text-xs text-rose-800">
                  <span className="font-semibold">Rejection Reason:</span>{' '}
                  {exp.rejection_reason}
                </div>
              )}

              {/* Actions Footer */}
              {exp.verification_status === 'PENDING' && (
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                  <button
                    onClick={() => setRejectModal({ id: exp.id })}
                    disabled={processingId === exp.id}
                    className="inline-flex items-center space-x-1.5 rounded-lg border border-slate-300 px-3.5 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition cursor-pointer"
                  >
                    <XCircle className="w-3.5 h-3.5 text-rose-500" />
                    <span>Reject</span>
                  </button>

                  <button
                    onClick={() => handleApprove(exp.id)}
                    disabled={processingId === exp.id}
                    className="inline-flex items-center space-x-1.5 rounded-lg bg-emerald-600 px-4 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-emerald-500 transition cursor-pointer"
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>{processingId === exp.id ? 'Approving...' : 'Approve & Embed'}</span>
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Reject Modal */}
      {rejectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl border border-slate-200">
            <h3 className="text-base font-bold text-slate-900">
              Reject Experience
            </h3>
            <p className="mt-1 text-xs text-slate-500 leading-relaxed">
              State the reason this proposed correction should not be incorporated into the AI memory.
            </p>

            <div className="mt-4">
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Rejection Reason (Optional)
              </label>
              <textarea
                rows={3}
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="e.g. Incompatible with company policy..."
                className="w-full rounded-lg border border-slate-300 p-2.5 text-xs focus:border-blue-500 focus:outline-hidden"
              />
            </div>

            <div className="mt-5 flex justify-end space-x-2">
              <button
                onClick={() => setRejectModal(null)}
                className="rounded-lg border border-slate-300 px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                className="rounded-lg bg-rose-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-rose-500 cursor-pointer"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Manual Create Modal */}
      {createModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center space-x-2 text-blue-600 mb-1">
              <Sparkles className="w-5 h-5" />
              <h3 className="text-base font-bold text-slate-900">
                Author Custom Experience
              </h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Preemptively teach the AI how to answer specific company questions. Created as PENDING for verification.
            </p>

            <form onSubmit={handleManualCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Customer Question *
                </label>
                <input
                  type="text"
                  required
                  value={newQuestion}
                  onChange={(e) => setNewQuestion(e.target.value)}
                  placeholder="e.g. Can we issue partial refunds?"
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-blue-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Original / Misconception Answer (Optional)
                </label>
                <textarea
                  rows={2}
                  value={newOriginalAnswer}
                  onChange={(e) => setNewOriginalAnswer(e.target.value)}
                  placeholder="What was incorrectly answered or assumed before?"
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-blue-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Corrected Verified Answer *
                </label>
                <textarea
                  rows={3}
                  required
                  value={newCorrectedAnswer}
                  onChange={(e) => setNewCorrectedAnswer(e.target.value)}
                  placeholder="The factual truth to teach the assistant..."
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-blue-500 focus:outline-hidden"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setCreateModal(false)}
                  disabled={createLoading}
                  className="rounded-lg border border-slate-300 px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createLoading}
                  className="rounded-lg bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-blue-500 cursor-pointer"
                >
                  {createLoading ? 'Creating...' : 'Create Experience'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default Experiences;
