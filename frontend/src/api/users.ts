// src/api/users.ts
import apiClient from './client';
import { UserManagementItem } from '../types/api';

export const usersApi = {
  listUsers: async (companyId?: string): Promise<UserManagementItem[]> => {
    const params: Record<string, string> = {};
    if (companyId) params.company_id = companyId;
    const response = await apiClient.get<UserManagementItem[]>('/users/', { params });
    return response.data;
  },

  inviteUser: async (data: {
    email: string;
    password: string;
    full_name: string;
    role: 'EMPLOYEE' | 'COMPANY_ADMIN' | 'CUSTOMER';
    company_id?: string;
  }): Promise<UserManagementItem> => {
    const response = await apiClient.post<UserManagementItem>('/users/invite', data);
    return response.data;
  },

  updateUser: async (
    userId: string,
    data: {
      full_name?: string;
      role?: string;
      is_active?: boolean;
    }
  ): Promise<UserManagementItem> => {
    const response = await apiClient.put<UserManagementItem>(`/users/${userId}`, data);
    return response.data;
  },

  deleteUser: async (userId: string): Promise<{ detail: string; is_active: boolean }> => {
    const response = await apiClient.delete(`/users/${userId}`);
    return response.data;
  },
};
