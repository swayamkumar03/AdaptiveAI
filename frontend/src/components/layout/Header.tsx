// src/components/layout/Header.tsx
import React from 'react';
import { useLocation } from 'react-router-dom';
import { Menu, Server, ShieldCheck } from 'lucide-react';
import { authApi } from '../../api/auth';

interface HeaderProps {
  onToggleSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const location = useLocation();
  const user = authApi.getCurrentUser();

  const getPageTitle = (pathname: string) => {
    switch (pathname) {
      case '/platform/dashboard':
        return 'Platform Administrator Overview';
      case '/platform/companies':
        return 'Client Companies & Tenant Management';
      case '/platform/usage':
        return 'Platform Infrastructure & Usage';
      case '/dashboard':
        return 'Company Overview & Dashboard';
      case '/chat':
        return 'Chatbot / Knowledge Testing';
      case '/documents':
        return 'Document Knowledge Base';
      case '/feedback':
        return 'Feedback & Review';
      case '/experiences':
        return 'Verified Experiences';
      case '/escalations':
        return 'Human Escalations Queue';
      case '/analytics':
        return 'Analytics & Reliability Metrics';
      case '/company/users':
        return 'Company Team & User Management';
      case '/company/settings':
        return 'Company & Chatbot Settings';
      case '/integrate':
        return 'Website Chatbot Integration';
      default:
        return 'AdaptiveAI Management Console';
    }
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200/80 bg-white/95 px-4 backdrop-blur-xs sm:px-6 lg:px-8 shadow-xs">
      <div className="flex items-center space-x-3">
        <button
          onClick={onToggleSidebar}
          className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800 lg:hidden"
          aria-label="Open sidebar"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div>
          <h1 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight">
            {getPageTitle(location.pathname)}
          </h1>
          <p className="hidden sm:block text-xs text-slate-500 font-medium">
            Continuous Self-Improving RAG Architecture
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* Backend Connected Indicator */}
        <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200">
          <Server className="w-3.5 h-3.5 text-blue-600" />
          <span>API 8000</span>
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse ml-1" />
        </div>

        {/* Super Admin Badge or Tenant Isolation Badge */}
        {user?.role === 'SUPER_ADMIN' ? (
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-purple-50 text-purple-800 text-xs font-semibold border border-purple-200">
            <ShieldCheck className="w-3.5 h-3.5 text-purple-600" />
            <span>Platform Root Admin</span>
          </div>
        ) : user?.company_id ? (
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-blue-50 text-blue-800 text-xs font-medium border border-blue-200">
            <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
            <span className="truncate max-w-[130px]" title={`Tenant: ${user.company_id}`}>
              Tenant: {user.company_id.substring(0, 8)}...
            </span>
          </div>
        ) : null}
      </div>
    </header>
  );
};
export default Header;
