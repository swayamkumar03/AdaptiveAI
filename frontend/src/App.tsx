// src/App.tsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './routes/ProtectedRoute';
import AppLayout from './components/layout/AppLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Documents from './pages/Documents';
import Feedback from './pages/Feedback';
import Experiences from './pages/Experiences';
import Escalations from './pages/Escalations';
import Analytics from './pages/Analytics';

// New Role-Based Pages
import PlatformDashboard from './pages/platform/PlatformDashboard';
import CompaniesManagement from './pages/platform/CompaniesManagement';
import PlatformUsage from './pages/platform/PlatformUsage';
import CompanyUsers from './pages/company/CompanyUsers';
import CompanySettings from './pages/company/CompanySettings';
import IntegrateChatbot from './pages/company/IntegrateChatbot';
import CustomerChat from './pages/customer/CustomerChat';

import { authApi } from './api/auth';

const RoleBasedHomeRedirect: React.FC = () => {
  const user = authApi.getCurrentUser();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role === 'SUPER_ADMIN') return <Navigate to="/platform/dashboard" replace />;
  if (user.role === 'CUSTOMER') return <Navigate to="/customer/chat" replace />;
  return <Navigate to="/dashboard" replace />;
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Login Route */}
        <Route path="/login" element={<Login />} />

        {/* Customer Standalone Chat Experience */}
        <Route element={<ProtectedRoute allowedRoles={['CUSTOMER']} />}>
          <Route path="/customer/chat" element={<CustomerChat />} />
        </Route>

        {/* Platform Administrator Routes (SUPER_ADMIN only) */}
        <Route element={<ProtectedRoute allowedRoles={['SUPER_ADMIN']} />}>
          <Route element={<AppLayout />}>
            <Route path="/platform/dashboard" element={<PlatformDashboard />} />
            <Route path="/platform/companies" element={<CompaniesManagement />} />
            <Route path="/platform/usage" element={<PlatformUsage />} />
          </Route>
        </Route>

        {/* Company Workspace Routes (COMPANY_ADMIN & EMPLOYEE) */}
        <Route
          element={<ProtectedRoute allowedRoles={['COMPANY_ADMIN', 'EMPLOYEE']} />}
        >
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/feedback" element={<Feedback />} />
            <Route path="/experiences" element={<Experiences />} />
            <Route path="/escalations" element={<Escalations />} />
            <Route path="/analytics" element={<Analytics />} />

            {/* Admin-only company pages */}
            <Route path="/company/users" element={<CompanyUsers />} />
            <Route path="/company/settings" element={<CompanySettings />} />
            <Route path="/integrate" element={<IntegrateChatbot />} />
          </Route>
        </Route>

        {/* Role-Based Root and Catch-all */}
        <Route path="/" element={<RoleBasedHomeRedirect />} />
        <Route path="*" element={<RoleBasedHomeRedirect />} />
      </Routes>
    </BrowserRouter>
  );
};
export default App;
