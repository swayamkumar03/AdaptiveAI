// src/routes/ProtectedRoute.tsx
import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { authApi } from '../api/auth';

interface ProtectedRouteProps {
  allowedRoles?: Array<'SUPER_ADMIN' | 'COMPANY_ADMIN' | 'EMPLOYEE' | 'CUSTOMER'>;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles }) => {
  const isAuth = authApi.isAuthenticated();
  const location = useLocation();
  const user = authApi.getCurrentUser();

  if (!isAuth) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Role validation if allowedRoles is specified
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    if (user.role === 'SUPER_ADMIN') {
      return <Navigate to="/platform/dashboard" replace />;
    } else if (user.role === 'CUSTOMER') {
      return <Navigate to="/customer/chat" replace />;
    } else {
      return <Navigate to="/dashboard" replace />;
    }
  }

  return <Outlet />;
};
export default ProtectedRoute;
