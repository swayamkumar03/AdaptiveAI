// src/components/layout/Sidebar.tsx
import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  ThumbsUp,
  Sparkles,
  AlertTriangle,
  BarChart3,
  LogOut,
  Bot,
  User as UserIcon,
  X,
  Building2,
  Users,
  Settings,
  Code,
  ShieldCheck,
  Activity,
} from 'lucide-react';
import { authApi } from '../../api/auth';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const user = authApi.getCurrentUser();

  const handleLogout = async () => {
    await authApi.logout();
    navigate('/login');
  };

  // Build role-specific navigation (§4, §5.3, §6.2)
  const isSuperAdmin = user?.role === 'SUPER_ADMIN';
  const isCompanyAdmin = user?.role === 'COMPANY_ADMIN';

  let navItems = [];
  let sectionLabel = 'Platform';

  if (isSuperAdmin) {
    sectionLabel = 'Platform Administration';
    navItems = [
      { label: 'Platform Overview', path: '/platform/dashboard', icon: LayoutDashboard },
      { label: 'Companies / Clients', path: '/platform/companies', icon: Building2 },
      { label: 'Platform Usage', path: '/platform/usage', icon: Activity },
    ];
  } else if (isCompanyAdmin) {
    sectionLabel = 'Company Management';
    navItems = [
      { label: 'Overview', path: '/dashboard', icon: LayoutDashboard },
      { label: 'Chatbot / Test Chat', path: '/chat', icon: MessageSquare },
      { label: 'Documents', path: '/documents', icon: FileText },
      { label: 'Feedback', path: '/feedback', icon: ThumbsUp },
      { label: 'Experiences', path: '/experiences', icon: Sparkles },
      { label: 'Escalations', path: '/escalations', icon: AlertTriangle },
      { label: 'Analytics', path: '/analytics', icon: BarChart3 },
      { label: 'Company Users', path: '/company/users', icon: Users },
      { label: 'Company Settings', path: '/company/settings', icon: Settings },
      { label: 'Integrate Chatbot', path: '/integrate', icon: Code },
    ];
  } else {
    // EMPLOYEE or CUSTOMER
    sectionLabel = 'Workspace';
    navItems = [
      { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
      { label: 'AI Chat', path: '/chat', icon: MessageSquare },
      { label: 'Documents', path: '/documents', icon: FileText },
      { label: 'Feedback', path: '/feedback', icon: ThumbsUp },
      { label: 'Experiences', path: '/experiences', icon: Sparkles },
      { label: 'Escalations', path: '/escalations', icon: AlertTriangle },
      { label: 'Analytics', path: '/analytics', icon: BarChart3 },
    ];
  }

  return (
    <>
      {/* Mobile/Tablet Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-xs lg:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex w-64 flex-col bg-slate-900 text-slate-300 border-r border-slate-800 transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="flex h-16 items-center justify-between px-6 border-b border-slate-800/80">
          <div className="flex items-center space-x-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-white shadow-sm shadow-blue-500/20">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <span className="font-semibold text-white tracking-tight text-base">AdaptiveAI</span>
              <span className="block text-[10px] uppercase font-bold tracking-widest text-blue-400">
                {isSuperAdmin ? 'Platform Admin' : 'Enterprise'}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            {sectionLabel}
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center space-x-3 rounded-lg px-3 py-2 text-xs font-medium transition ${
                    isActive
                      ? 'bg-blue-600/15 text-blue-400 font-semibold border-l-2 border-blue-500 pl-[10px]'
                      : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                  }`
                }
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* User Footer */}
        <div className="border-t border-slate-800 p-4 bg-slate-950/40">
          <div className="flex items-center space-x-3 mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-800 text-slate-300 font-semibold text-xs border border-slate-700">
              {user?.full_name ? user.full_name.charAt(0).toUpperCase() : <UserIcon className="h-4 w-4" />}
            </div>
            <div className="flex-1 min-w-0">
              <p className="truncate text-xs font-medium text-white">{user?.full_name || 'System User'}</p>
              <div className="flex items-center space-x-1.5">
                <span className="truncate text-[11px] text-slate-400">{user?.email || 'user@example.com'}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs">
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 uppercase">
              {user?.role?.replace('_', ' ') || 'EMPLOYEE'}
            </span>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-1 text-slate-400 hover:text-rose-400 transition cursor-pointer"
              title="Sign Out"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
export default Sidebar;
