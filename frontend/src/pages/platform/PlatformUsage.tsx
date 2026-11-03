// src/pages/platform/PlatformUsage.tsx
import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  Server,
  Database,
  Cpu,
  Activity,
  Layers,
  Building2,
  CheckCircle2,
} from 'lucide-react';
import { companiesApi } from '../../api/companies';
import { PlatformOverview, CompanyItem } from '../../types/api';
import StatCard from '../../components/common/StatCard';
import Loading from '../../components/common/Loading';

export const PlatformUsage: React.FC = () => {
  const [overview, setOverview] = useState<PlatformOverview | null>(null);
  const [companies, setCompanies] = useState<CompanyItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [ovData, comps] = await Promise.all([
          companiesApi.getPlatformOverview(),
          companiesApi.listCompanies(),
        ]);
        setOverview(ovData);
        setCompanies(comps);
      } catch (err) {
        console.error('Error fetching usage data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <Loading message="Loading platform system usage metrics..." fullHeight />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 flex items-center space-x-2">
          <Activity className="w-6 h-6 text-blue-600" />
          <span>Platform Infrastructure & Usage</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Real-time service telemetry, multi-tenant distribution, and RAG knowledge utilization
        </p>
      </div>

      {/* System Health Indicators */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="RAG Inference Engine"
          value="Healthy"
          subtitle="Google Gemini 3.8 Flash active"
          highlight
          icon={<Cpu className="w-5 h-5 text-emerald-600" />}
        />
        <StatCard
          title="Vector Store"
          value="pgvector"
          subtitle="PostgreSQL vector similarity active"
          icon={<Database className="w-5 h-5 text-blue-600" />}
        />
        <StatCard
          title="Tenant Isolation"
          value="Enforced"
          subtitle="Server-side row-level filtering"
          icon={<Layers className="w-5 h-5 text-indigo-600" />}
        />
        <StatCard
          title="Embedding Dimension"
          value="1536 dims"
          subtitle="Cosine distance metric"
          icon={<Server className="w-5 h-5 text-purple-600" />}
        />
      </div>

      {/* Tenant Usage Breakdown Table */}
      <div className="rounded-xl border border-slate-200/80 bg-white shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Tenant Workload Distribution</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Knowledge items and conversation throughput by client organization
            </p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-blue-50 text-blue-700 rounded-full border border-blue-200">
            {companies.length} Registered Tenants
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200/80 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <th className="py-3 px-5">Client Company</th>
                <th className="py-3 px-5">Slug</th>
                <th className="py-3 px-5">Status</th>
                <th className="py-3 px-5 text-center">Assigned Users</th>
                <th className="py-3 px-5 text-center">Ingested Documents</th>
                <th className="py-3 px-5 text-center">Chat Sessions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {companies.map((comp) => (
                <tr key={comp.id} className="hover:bg-slate-50/60 transition">
                  <td className="py-3.5 px-5 font-semibold text-slate-900 flex items-center gap-2">
                    <Building2 className="w-3.5 h-3.5 text-slate-400" />
                    <span>{comp.name}</span>
                  </td>
                  <td className="py-3.5 px-5 font-mono text-slate-500">
                    {comp.slug}
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
                  <td className="py-3.5 px-5 text-center font-medium">
                    {comp.user_count || 0}
                  </td>
                  <td className="py-3.5 px-5 text-center font-medium">
                    {comp.document_count || 0}
                  </td>
                  <td className="py-3.5 px-5 text-center font-medium">
                    {comp.conversation_count || 0}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default PlatformUsage;
