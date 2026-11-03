// src/pages/company/IntegrateChatbot.tsx
import React, { useEffect, useState } from 'react';
import {
  Code,
  Copy,
  Check,
  ExternalLink,
  Bot,
  Sparkles,
  ShieldCheck,
  Globe,
  Layers,
  Terminal,
  CheckCircle2,
} from 'lucide-react';
import { companiesApi } from '../../api/companies';
import { CompanyItem } from '../../types/api';
import Loading from '../../components/common/Loading';

export const IntegrateChatbot: React.FC = () => {
  const [company, setCompany] = useState<CompanyItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchCompany = async () => {
      try {
        setLoading(true);
        const data = await companiesApi.getMyCompany();
        setCompany(data);
      } catch (err) {
        console.error('Error fetching company:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCompany();
  }, []);

  const chatbotId = company?.slug || 'adaptiveai-demo';
  const localWidgetUrl = `${window.location.origin}/widget.js`;
  const demoUrl = `${window.location.origin}/demo.html?tenant=${encodeURIComponent(chatbotId)}`;

  const embedSnippet = `<script
  src="${localWidgetUrl}"
  data-chatbot-id="${chatbotId}"
  data-api-base="http://127.0.0.1:8000/api/v1">
</script>`;

  const handleCopy = () => {
    navigator.clipboard.writeText(embedSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  if (loading) {
    return <Loading message="Loading integration parameters..." fullHeight />;
  }

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Page Header */}
      <div>
        <div className="inline-flex items-center space-x-2 rounded-full bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-600 border border-blue-500/20 mb-2">
          <Code className="w-3.5 h-3.5" />
          <span>Website Widget Integration</span>
        </div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
          Embed Chatbot on Your Website
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Deploy your company-trained AdaptiveAI conversational widget to any web page using a single lightweight script tag.
        </p>
      </div>

      {/* Integration Overview Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
            Public Chatbot Identifier
          </span>
          <div className="flex items-center space-x-1.5">
            <span className="font-mono font-bold text-sm text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
              {chatbotId}
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1.5">Tenant identifier for server-side resolution</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
            Widget Status
          </span>
          <div className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span className="font-semibold text-xs text-emerald-700">Active & Ready</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1.5">RAG retrieval and vector index operational</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
            Tenant Isolation
          </span>
          <div className="flex items-center space-x-1.5 text-slate-700 font-semibold text-xs">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Strict Company Isolation</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1.5">Zero cross-tenant data leakage</p>
        </div>
      </div>

      {/* Embed Code Snippet Box */}
      <div className="bg-slate-900 rounded-2xl border border-slate-800 shadow-xl overflow-hidden">
        <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-blue-400" />
            <span className="font-mono text-xs font-semibold text-slate-200">
              HTML Embed Snippet
            </span>
          </div>
          <button
            onClick={handleCopy}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition cursor-pointer"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5" />
                <span>Copied to Clipboard!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy Code</span>
              </>
            )}
          </button>
        </div>

        <div className="p-5 font-mono text-xs text-slate-200 leading-relaxed overflow-x-auto bg-slate-900">
          <pre>
            <span className="text-slate-500">&lt;!-- AdaptiveAI Embedded Chatbot Widget --&gt;</span>
            <br />
            {embedSnippet}
          </pre>
        </div>

        <div className="px-5 py-3 bg-slate-950/40 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between text-xs text-slate-400 gap-2">
          <span>Environment: <strong className="text-slate-300">Local Development</strong></span>
          <span>Script Source: <code className="text-blue-400">{localWidgetUrl}</code></span>
        </div>
      </div>

      {/* Local Demo Website Preview Card */}
      <div className="bg-gradient-to-r from-blue-900/20 via-indigo-900/10 to-slate-900/40 border border-blue-500/30 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-blue-600 mb-1">
            <Sparkles className="w-4 h-4" />
            <h3 className="font-bold text-sm text-slate-900">Interactive Demo Website</h3>
          </div>
          <p className="text-xs text-slate-600 max-w-xl">
            See how your chatbot operates on an external commercial storefront with full document grounding, source citations, thumbs up/down feedback, and low-confidence escalations.
          </p>
        </div>
        <a
          href={demoUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-md transition cursor-pointer shrink-0"
        >
          <span>Launch Local Demo Website</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      {/* Step-by-Step Integration Guide */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
        <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2 pb-3 border-b border-slate-100">
          <Globe className="w-4 h-4 text-blue-600" />
          <span>Integration Steps for Your Website</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70 space-y-2">
            <div className="w-6 h-6 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center text-xs">
              1
            </div>
            <h4 className="font-semibold text-slate-900">Paste Script Tag</h4>
            <p className="text-slate-500 leading-relaxed">
              Add the generated snippet just before the closing <code>&lt;/body&gt;</code> tag on your website pages.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70 space-y-2">
            <div className="w-6 h-6 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center text-xs">
              2
            </div>
            <h4 className="font-semibold text-slate-900">Verify Chatbot ID</h4>
            <p className="text-slate-500 leading-relaxed">
              Ensure <code>data-chatbot-id="{chatbotId}"</code> matches your organization slug.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70 space-y-2">
            <div className="w-6 h-6 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center text-xs">
              3
            </div>
            <h4 className="font-semibold text-slate-900">Test Live AI Responses</h4>
            <p className="text-slate-500 leading-relaxed">
              Open your website. The floating AdaptiveAI widget launcher will appear and query your knowledge base immediately.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
export default IntegrateChatbot;
