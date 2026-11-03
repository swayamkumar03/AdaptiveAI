// src/pages/platform/PlatformDashboard.tsx
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Building2,
  Users,
  MessageSquare,
  FileText,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  ArrowRight,
  ShieldCheck,
  Plus,
  RefreshCw,
  Clock,
} from 'lucide-react';
import { companiesApi } from '../../api/companies';
import { PlatformOverview } from '../../types/api';
import StatCard from '../../components/common/StatCard';
import Loading from '../../components/common/Loading';
import ErrorMessage from '../../components/common/ErrorMessage';

export const PlatformDashboard: React.FC = () => {
  const [overview, setOverview] = useState<PlatformOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPlatformData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await companiesApi.getPlatformOverview();
      setOverview(data);
    } catch (err: any) {
      console.error('Error fetching platform metrics:', err);
      setError(
        err.response?.data?.detail || 'Failed to fetch platform administrator overview.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlatformData();
  }, []);

  if (loading) {
    return <Loading message="Loading platform overview metrics..." fullHeight />;
  }

  if (error) {
    return (
      <div className="py-8">
        <ErrorMessage
          title="Platform Dashboard Error"
          message={error}
          onRetry={fetchPlatformData}
        />
      </div>
    );
  }

  if (!overview) return null;

  return (
    <div className="space-y-8">
      {/* Platform Admin Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 p-6 sm:p-8 text-white shadow-xl border border-slate-800">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center space-x-2 rounded-full bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-400 border border-blue-500/20 mb-3">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Platform Administration • Multi-Tenant Root</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            AdaptiveAI Service Console
          </h1>
          <p className="mt-2 text-sm text-slate-300 leading-relaxed">
            Global management portal for client companies, tenant isolation, cross-platform usage monitoring, and platform infrastructure health.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link
              to="/platform/companies"
              className="inline-flex items-center space-x-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-md hover:bg-blue-500 transition cursor-pointer"
            >
              <Building2 className="w-4 h-4" />
              <span>Manage Client Companies ({overview.total_companies})</span>
            </Link>
            <button
              onClick={fetchPlatformData}
              className="inline-flex items-center space-x-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 px-3.5 py-2 text-xs font-medium text-slate-300 border border-slate-700 transition cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh Metrics</span>
            </button>
          </div>
        </div>
      </div>

      {/* Primary Platform Metrics Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Client Companies"
          value={overview.total_companies}
          subtitle={`${overview.active_companies} active • ${overview.inactive_companies} inactive`}
          highlight
          icon={<Building2 className="h-5 w-5 text-blue-600" />}
        />
        <StatCard
          title="Total Platform Users"
          value={overview.total_users}
          subtitle="Administrators, employees & customers"
          icon={<Users className="h-5 w-5 text-indigo-600" />}
        />
        <StatCard
          title="User Questions Handled"
          value={overview.total_user_questions}
          subtitle="Processed via RAG across all tenants"
          icon={<MessageSquare className="h-5 w-5 text-emerald-600" />}
        />
        <StatCard
          title="Total Assistant Answers"
          value={overview.total_assistant_answers}
          subtitle="AI responses delivered"
          icon={<CheckCircle2 className="h-5 w-5 text-blue-600" />}
        />
        <StatCard
          title="Knowledge Documents"
          value={overview.total_documents}
          subtitle="Stored across all client repositories"
          icon={<FileText className="h-5 w-5 text-slate-700" />}
        />
        <StatCard
          title="Global Escalations"
          value={overview.total_escalations}
          subtitle="Low-confidence support referrals"
          icon={<AlertTriangle className="h-5 w-5 text-amber-600" />}
        />
        <StatCard
          title="Active Tenants"
          value={overview.active_companies}
          subtitle="Currently permitted to serve chat"
          icon={<TrendingUp className="h-5 w-5 text-emerald-600" />}
        />
        <StatCard
          title="Platform Version"
          value="v0.1.0"
          subtitle="Self-improving RAG pipeline active"
          icon={<ShieldCheck className="h-5 w-5 text-purple-600" />}
        />
      </div>

      {/* Recent Companies Registrations */}
      <div className="rounded-xl border border-slate-200/80 bg-white shadow-xs overflow-hidden">
        <div className="flex items-center justify-between p-5 border-b border-slate-100">
          <div>
            <h2 className="text-base font-bold text-slate-900">Recent Company Registrations</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Newly registered client tenants on the AdaptiveAI network
            </p>
          </div>
          <Link
            to="/platform/companies"
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center space-x-1"
          >
            <span>View All Companies</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50/75 border-b border-slate-100 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <th className="py-3 px-5">Company Name</th>
                <th className="py-3 px-5">Slug</th>
                <th className="py-3 px-5">Industry</th>
                <th className="py-3 px-5">Status</th>
                <th className="py-3 px-5">Registered At</th>
                <th className="py-3 px-5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {overview.recent_companies.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-slate-500">
                    No companies registered yet.
                  </td>
                </tr>
              ) : (
                overview.recent_companies.map((comp) => (
                  <tr key={comp.id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3.5 px-5 font-semibold text-slate-900">
                      {comp.name}
                    </td>
                    <td className="py-3.5 px-5 font-mono text-slate-500">
                      {comp.slug}
                    </td>
                    <td className="py-3.5 px-5 text-slate-600">
                      {comp.industry || 'General / Unspecified'}
                    </td>
                    <td className="py-3.5 px-5">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          comp.is_active
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : 'bg-rose-50 text-rose-700 border border-rose-200'
                        }`}
                      >
                        {comp.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="py-3.5 px-5 text-slate-500">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-3 h-3 text-slate-400" />
                        <span>
                          {comp.created_at
                            ? new Date(comp.created_at).toLocaleDateString()
                            : 'Recently'}
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      <Link
                        to="/platform/companies"
                        className="text-xs font-semibold text-blue-600 hover:text-blue-700"
                      >
                        Manage
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default PlatformDashboard;
