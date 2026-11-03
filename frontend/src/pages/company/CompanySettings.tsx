// src/pages/company/CompanySettings.tsx
import React, { useEffect, useState } from 'react';
import {
  Settings,
  Building,
  Bot,
  Globe,
  Save,
  CheckCircle,
  AlertCircle,
  Sparkles,
} from 'lucide-react';
import { companiesApi } from '../../api/companies';
import { CompanyItem, ChatbotSettingsItem } from '../../types/api';
import Loading from '../../components/common/Loading';
import ErrorMessage from '../../components/common/ErrorMessage';

export const CompanySettings: React.FC = () => {
  const [company, setCompany] = useState<CompanyItem | null>(null);
  const [botSettings, setBotSettings] = useState<ChatbotSettingsItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Form states - Company
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('');
  const [website, setWebsite] = useState('');
  const [description, setDescription] = useState('');

  // Form states - Bot Settings
  const [botName, setBotName] = useState('');
  const [tone, setTone] = useState('Professional');
  const [responseLength, setResponseLength] = useState('Medium');
  const [brandDescription, setBrandDescription] = useState('');
  const [autoEscalate, setAutoEscalate] = useState(true);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const [compData, botData] = await Promise.all([
        companiesApi.getMyCompany(),
        companiesApi.getMyChatbotSettings(),
      ]);

      setCompany(compData);
      setBotSettings(botData);

      setCompanyName(compData.name || '');
      setIndustry(compData.industry || '');
      setWebsite(compData.website || '');
      setDescription(compData.description || '');

      setBotName(botData.bot_name || 'AI Assistant');
      setTone(botData.tone || 'Professional');
      setResponseLength(botData.response_length || 'Medium');
      setBrandDescription(botData.brand_description || '');
      setAutoEscalate(botData.auto_escalate_on_low_confidence ?? true);
    } catch (err: any) {
      console.error('Error fetching settings:', err);
      setError(err.response?.data?.detail || 'Failed to load company settings.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSaveCompany = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      setError(null);
      await companiesApi.updateMyCompany({
        name: companyName,
        industry,
        website,
        description,
      });

      await companiesApi.updateMyChatbotSettings({
        bot_name: botName,
        tone,
        response_length: responseLength,
        brand_description: brandDescription,
        auto_escalate_on_low_confidence: autoEscalate,
      });

      setSaveSuccess('Company profile and AI assistant settings updated successfully.');
      setTimeout(() => setSaveSuccess(null), 4000);
    } catch (err: any) {
      console.error('Save error:', err);
      setError(err.response?.data?.detail || 'Failed to save settings.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <Loading message="Loading company settings..." fullHeight />;
  }

  if (error && !company) {
    return <ErrorMessage title="Settings Unavailable" message={error} onRetry={fetchSettings} />;
  }

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 flex items-center space-x-2">
          <Settings className="w-6 h-6 text-blue-600" />
          <span>Company & Chatbot Settings</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Customize organization identity, tenant branding, and conversational assistant parameters
        </p>
      </div>

      {saveSuccess && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2.5">
          <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
          <span className="font-medium">{saveSuccess}</span>
        </div>
      )}

      {error && (
        <div className="p-3.5 bg-rose-50 border border-rose-200 text-rose-800 text-xs rounded-xl flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSaveCompany} className="space-y-6">
        {/* Company Profile Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
          <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-100">
            <Building className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-bold text-slate-900">Organization Profile</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Company Name *</label>
              <input
                type="text"
                required
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-hidden focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Tenant Slug (Read-only)</label>
              <input
                type="text"
                disabled
                value={company?.slug || ''}
                className="w-full px-3 py-2 font-mono bg-slate-100 border border-slate-200 rounded-lg text-slate-500 cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Industry</label>
              <input
                type="text"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="e.g. Retail / Apparel"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-hidden focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Corporate Website</label>
              <div className="relative">
                <Globe className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={website}
                  onChange={(e) => setWebsite(e.target.value)}
                  placeholder="https://example.com"
                  className="w-full pl-8 pr-3 py-2 border border-slate-300 rounded-lg focus:outline-hidden focus:border-blue-500"
                />
              </div>
            </div>

            <div className="sm:col-span-2">
              <label className="block font-semibold text-slate-700 mb-1">Company Description</label>
              <textarea
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief summary of your products and services..."
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-hidden focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* AI Assistant Personality Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
          <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-100">
            <Bot className="w-4 h-4 text-indigo-600" />
            <h2 className="text-sm font-bold text-slate-900">Chatbot Assistant Personality</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Assistant Display Name *</label>
              <input
                type="text"
                required
                value={botName}
                onChange={(e) => setBotName(e.target.value)}
                placeholder="e.g. Support Assistant"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-hidden focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Conversational Tone</label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-hidden focus:border-blue-500 bg-white"
              >
                <option value="Professional">Professional (Clear, formal, authoritative)</option>
                <option value="Friendly">Friendly (Warm, welcoming, polite)</option>
                <option value="Casual">Casual (Concise, conversational)</option>
                <option value="Technical">Technical (Detailed, direct)</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Response Length</label>
              <select
                value={responseLength}
                onChange={(e) => setResponseLength(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-hidden focus:border-blue-500 bg-white"
              >
                <option value="Concise">Concise (1-2 sentences)</option>
                <option value="Medium">Medium (Standard paragraph with bullets)</option>
                <option value="Detailed">Detailed (Full explanation with context)</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Auto-Escalation on Low Confidence</label>
              <div className="flex items-center space-x-2 pt-2">
                <input
                  type="checkbox"
                  id="autoEsc"
                  checked={autoEscalate}
                  onChange={(e) => setAutoEscalate(e.target.checked)}
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="autoEsc" className="text-slate-700 font-medium cursor-pointer">
                  Automatically escalate low-confidence queries
                </label>
              </div>
            </div>

            <div className="sm:col-span-2">
              <label className="block font-semibold text-slate-700 mb-1">Brand Description for RAG</label>
              <textarea
                rows={2}
                value={brandDescription}
                onChange={(e) => setBrandDescription(e.target.value)}
                placeholder="Background context supplied to the AI when generating responses..."
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-hidden focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center space-x-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold text-xs shadow-md disabled:opacity-50 transition cursor-pointer"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving Changes...' : 'Save All Settings'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
export default CompanySettings;
