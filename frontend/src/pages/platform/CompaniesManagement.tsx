// src/pages/platform/CompaniesManagement.tsx
import React, { useEffect, useState } from 'react';
import {
  Building2,
  Search,
  Plus,
  Edit2,
  CheckCircle,
  XCircle,
  Users,
  FileText,
  MessageSquare,
  Globe,
  Clock,
  AlertCircle,
  X,
  ExternalLink,
} from 'lucide-react';
import { companiesApi } from '../../api/companies';
import { CompanyItem } from '../../types/api';
import Loading from '../../components/common/Loading';
import ErrorMessage from '../../components/common/ErrorMessage';

export const CompaniesManagement: React.FC = () => {
  const [companies, setCompanies] = useState<CompanyItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  // Modal States
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingCompany, setEditingCompany] = useState<CompanyItem | null>(null);

  // Form States for Create
  const [newName, setNewName] = useState('');
  const [newSlug, setNewSlug] = useState('');
  const [newIndustry, setNewIndustry] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newWebsite, setNewWebsite] = useState('');
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await companiesApi.listCompanies(search, statusFilter);
      setCompanies(data);
    } catch (err: any) {
      console.error('Error fetching companies:', err);
      setError(err.response?.data?.detail || 'Failed to fetch companies list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, [statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCompanies();
  };

  const handleAutoSlug = (nameVal: string) => {
    setNewName(nameVal);
    // Auto-generate a clean url-friendly slug if user hasn't typed custom slug yet
    const generated = nameVal
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-');
    setNewSlug(generated);
  };

  const handleCreateCompany = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName || !newSlug) {
      setFormError('Company name and slug are required.');
      return;
    }

    try {
      setFormSubmitting(true);
      setFormError(null);
      await companiesApi.createCompany({
        name: newName,
        slug: newSlug,
        industry: newIndustry || undefined,
        description: newDescription || undefined,
        website: newWebsite || undefined,
      });

      setShowCreateModal(false);
      setNewName('');
      setNewSlug('');
      setNewIndustry('');
      setNewDescription('');
      setNewWebsite('');
      await fetchCompanies();
    } catch (err: any) {
      console.error('Create company error:', err);
      setFormError(err.response?.data?.detail || 'Failed to create company.');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleUpdateCompany = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingCompany) return;

    try {
      setFormSubmitting(true);
      setFormError(null);
      await companiesApi.updateCompany(editingCompany.id, {
        name: editingCompany.name,
        industry: editingCompany.industry,
        description: editingCompany.description,
        website: editingCompany.website,
        is_active: editingCompany.is_active,
      });

      setEditingCompany(null);
      await fetchCompanies();
    } catch (err: any) {
      console.error('Update company error:', err);
      setFormError(err.response?.data?.detail || 'Failed to update company.');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleToggleStatus = async (comp: CompanyItem) => {
    try {
      const updatedStatus = !comp.is_active;
      await companiesApi.updateCompany(comp.id, { is_active: updatedStatus });
      setCompanies((prev) =>
        prev.map((c) => (c.id === comp.id ? { ...c, is_active: updatedStatus } : c))
      );
    } catch (err: any) {
      console.error('Toggle status error:', err);
      alert(err.response?.data?.detail || 'Failed to update company status.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 flex items-center space-x-2">
            <Building2 className="w-6 h-6 text-blue-600" />
            <span>Client Companies Management</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Configure registered tenant client organizations and monitor cross-tenant activity
          </p>
        </div>
        <button
          onClick={() => {
            setFormError(null);
            setShowCreateModal(true);
          }}
          className="inline-flex items-center space-x-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-blue-500 transition cursor-pointer self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Register New Company</span>
        </button>
      </div>

      {/* Search and Filters Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs flex flex-col sm:flex-row gap-3 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="flex-1 w-full sm:max-w-md relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by company name or slug..."
            className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:outline-hidden focus:border-blue-500 bg-slate-50/50"
          />
        </form>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <label className="text-xs text-slate-500 font-medium">Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg px-3 py-1.5 bg-white text-slate-700 focus:outline-hidden focus:border-blue-500"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active Only</option>
            <option value="inactive">Inactive Only</option>
          </select>
        </div>
      </div>

      {/* Companies Table */}
      {loading ? (
        <Loading message="Fetching registered client companies..." />
      ) : error ? (
        <ErrorMessage title="Error loading companies" message={error} onRetry={fetchCompanies} />
      ) : (
        <div className="rounded-xl border border-slate-200/80 bg-white shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200/80 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  <th className="py-3 px-4">Company</th>
                  <th className="py-3 px-4">Slug (Widget ID)</th>
                  <th className="py-3 px-4">Industry / Details</th>
                  <th className="py-3 px-4 text-center">Users</th>
                  <th className="py-3 px-4 text-center">Docs</th>
                  <th className="py-3 px-4 text-center">Chats</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {companies.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-slate-500">
                      No companies match your query.
                    </td>
                  </tr>
                ) : (
                  companies.map((comp) => (
                    <tr key={comp.id} className="hover:bg-slate-50/70 transition">
                      <td className="py-3.5 px-4 font-semibold text-slate-900">
                        <div>{comp.name}</div>
                        {comp.website && (
                          <a
                            href={comp.website.startsWith('http') ? comp.website : `https://${comp.website}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[11px] text-blue-600 hover:underline flex items-center gap-1 font-normal"
                          >
                            <Globe className="w-2.5 h-2.5" />
                            <span>{comp.website.replace(/^https?:\/\//, '')}</span>
                          </a>
                        )}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-[11px] text-slate-600">
                        <span className="px-1.5 py-0.5 bg-slate-100 rounded border border-slate-200">
                          {comp.slug}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-600">
                        <div className="font-medium text-slate-800">{comp.industry || 'General'}</div>
                        <div className="text-[11px] text-slate-400 line-clamp-1">
                          {comp.description || 'No description provided.'}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-center font-medium text-slate-800">
                        {comp.user_count || 0}
                      </td>
                      <td className="py-3.5 px-4 text-center font-medium text-slate-800">
                        {comp.document_count || 0}
                      </td>
                      <td className="py-3.5 px-4 text-center font-medium text-slate-800">
                        {comp.conversation_count || 0}
                      </td>
                      <td className="py-3.5 px-4">
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
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => {
                              setFormError(null);
                              setEditingCompany(comp);
                            }}
                            className="p-1 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded transition cursor-pointer"
                            title="Edit Details"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleToggleStatus(comp)}
                            className={`p-1 rounded transition cursor-pointer ${
                              comp.is_active
                                ? 'text-rose-500 hover:bg-rose-50'
                                : 'text-emerald-600 hover:bg-emerald-50'
                            }`}
                            title={comp.is_active ? 'Deactivate Company' : 'Activate Company'}
                          >
                            {comp.is_active ? (
                              <XCircle className="w-3.5 h-3.5" />
                            ) : (
                              <CheckCircle className="w-3.5 h-3.5" />
                            )}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Company Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden">
            <div className="flex items-center justify-between p-5 border-b border-slate-100 bg-slate-50/50">
              <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <Building2 className="w-4 h-4 text-blue-600" />
                <span>Register New Client Company</span>
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateCompany} className="p-5 space-y-4 text-xs">
              {formError && (
                <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{formError}</span>
                </div>
              )}

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Company Name *</label>
                <input
                  type="text"
                  required
                  value={newName}
                  onChange={(e) => handleAutoSlug(e.target.value)}
                  placeholder="e.g. Acme Corporation"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-hidden focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Public Slug / Widget ID *
                </label>
                <input
                  type="text"
                  required
                  value={newSlug}
                  onChange={(e) => setNewSlug(e.target.value)}
                  placeholder="e.g. acme-corp"
                  className="w-full px-3 py-2 font-mono border border-slate-300 rounded-lg text-xs focus:outline-hidden focus:border-blue-500"
                />
                <p className="text-[10px] text-slate-400 mt-1">
                  Unique identifier used in website embed snippet <code>data-chatbot-id</code>.
                </p>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Industry</label>
                <input
                  type="text"
                  value={newIndustry}
                  onChange={(e) => setNewIndustry(e.target.value)}
                  placeholder="e.g. Retail, Healthcare, SaaS"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-hidden focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Website URL</label>
                <input
                  type="url"
                  value={newWebsite}
                  onChange={(e) => setNewWebsite(e.target.value)}
                  placeholder="https://example.com"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-hidden focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  rows={2}
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Short summary of company operations..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-hidden focus:border-blue-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 cursor-pointer font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={formSubmitting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold shadow-xs disabled:opacity-50 cursor-pointer"
                >
                  {formSubmitting ? 'Registering...' : 'Register Company'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Company Modal */}
      {editingCompany && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden">
            <div className="flex items-center justify-between p-5 border-b border-slate-100 bg-slate-50/50">
              <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <Edit2 className="w-4 h-4 text-blue-600" />
                <span>Edit Company: {editingCompany.name}</span>
              </h3>
              <button
                onClick={() => setEditingCompany(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleUpdateCompany} className="p-5 space-y-4 text-xs">
              {formError && (
                <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{formError}</span>
                </div>
              )}

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  value={editingCompany.name}
                  onChange={(e) =>
                    setEditingCompany({ ...editingCompany, name: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-hidden focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Industry</label>
                <input
                  type="text"
                  value={editingCompany.industry || ''}
                  onChange={(e) =>
                    setEditingCompany({ ...editingCompany, industry: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-hidden focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Website URL</label>
                <input
                  type="text"
                  value={editingCompany.website || ''}
                  onChange={(e) =>
                    setEditingCompany({ ...editingCompany, website: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-hidden focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  rows={3}
                  value={editingCompany.description || ''}
                  onChange={(e) =>
                    setEditingCompany({ ...editingCompany, description: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-hidden focus:border-blue-500"
                />
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="activeCheck"
                  checked={editingCompany.is_active}
                  onChange={(e) =>
                    setEditingCompany({ ...editingCompany, is_active: e.target.checked })
                  }
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="activeCheck" className="text-xs font-medium text-slate-700">
                  Company is active (authorized to serve chatbot queries)
                </label>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setEditingCompany(null)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 cursor-pointer font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={formSubmitting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold shadow-xs disabled:opacity-50 cursor-pointer"
                >
                  {formSubmitting ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default CompaniesManagement;
