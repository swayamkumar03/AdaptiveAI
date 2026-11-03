// src/pages/Login.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, Lock, Mail, ArrowRight, AlertCircle, Sparkles } from 'lucide-react';
import { authApi } from '../api/auth';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please provide both email and password.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const authRes = await authApi.login(email, password);
      const role = authRes.user?.role;

      if (role === 'SUPER_ADMIN') {
        navigate('/platform/dashboard');
      } else if (role === 'CUSTOMER') {
        navigate('/customer/chat');
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to authenticate. Please check server connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDemoFill = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-blue-600/10 blur-[120px] pointer-events-none rounded-full" />
      <div className="absolute bottom-0 right-10 w-[400px] h-[300px] bg-purple-600/10 blur-[100px] pointer-events-none rounded-full" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="flex justify-center">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/25">
            <Bot className="h-7 w-7" />
          </div>
        </div>
        <h2 className="mt-4 text-center text-2xl font-bold tracking-tight text-white">
          AdaptiveAI Knowledge Portal
        </h2>
        <p className="mt-1 text-center text-xs text-slate-400 font-medium">
          Self-Improving RAG Architecture with Human-in-the-Loop
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10 px-4 sm:px-0">
        <div className="bg-slate-800/90 backdrop-blur-md py-8 px-6 sm:px-10 shadow-2xl rounded-2xl border border-slate-700/80">
          {error && (
            <div className="mb-6 flex items-start space-x-3 rounded-lg border border-rose-500/40 bg-rose-500/10 p-3.5 text-xs text-rose-300">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-400 mt-0.5" />
              <div className="leading-relaxed">{error}</div>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                Corporate Email
              </label>
              <div className="relative rounded-lg shadow-xs">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  <Mail className="h-4 w-4" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@adaptiveai-demo.com"
                  required
                  className="block w-full rounded-lg border border-slate-600 bg-slate-900/80 pl-10 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-hidden transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                Password
              </label>
              <div className="relative rounded-lg shadow-xs">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="block w-full rounded-lg border border-slate-600 bg-slate-900/80 pl-10 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-hidden transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex w-full justify-center items-center space-x-2 rounded-lg bg-blue-600 py-2.5 px-4 text-sm font-semibold text-white shadow-md hover:bg-blue-500 focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-800 disabled:opacity-50 transition cursor-pointer"
            >
              <span>{loading ? 'Authenticating...' : 'Sign in to Console'}</span>
              {!loading && <ArrowRight className="h-4 w-4" />}
            </button>
          </form>

          {/* Quick Demo Credentials for Evaluation */}
          <div className="mt-6 pt-6 border-t border-slate-700/80">
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-400 mb-2.5">
              <Sparkles className="w-3.5 h-3.5 text-blue-400" />
              <span>Demo Quick-Fill by Role:</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
              <button
                type="button"
                onClick={() => handleDemoFill('superadmin@adaptiveai.dev', 'AdaptiveAI123')}
                className="py-1.5 px-2 bg-slate-700/60 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-600/80 text-left transition cursor-pointer"
              >
                <span className="font-semibold block text-purple-300 text-[11px]">Platform Admin</span>
                <span className="text-[10px] text-slate-400 truncate block">SUPER_ADMIN</span>
              </button>
              <button
                type="button"
                onClick={() => handleDemoFill('admin@adaptiveai-demo.com', 'DemoAdmin123!')}
                className="py-1.5 px-2 bg-slate-700/60 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-600/80 text-left transition cursor-pointer"
              >
                <span className="font-semibold block text-blue-300 text-[11px]">Company Admin</span>
                <span className="text-[10px] text-slate-400 truncate block">COMPANY_ADMIN</span>
              </button>
              <button
                type="button"
                onClick={() => handleDemoFill('customer@adaptiveai-demo.com', 'Customer123!')}
                className="py-1.5 px-2 bg-slate-700/60 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-600/80 text-left transition cursor-pointer"
              >
                <span className="font-semibold block text-emerald-300 text-[11px]">Customer User</span>
                <span className="text-[10px] text-slate-400 truncate block">CUSTOMER</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
export default Login;
