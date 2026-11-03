// src/api/companies.ts
import apiClient from './client';
import { CompanyItem, PlatformOverview, ChatbotSettingsItem } from '../types/api';

export const companiesApi = {
  // Platform Admin (SUPER_ADMIN)
  getPlatformOverview: async (): Promise<PlatformOverview> => {
    const response = await apiClient.get<PlatformOverview>('/companies/platform/overview');
    return response.data;
  },

  listCompanies: async (search?: string, statusFilter?: string): Promise<CompanyItem[]> => {
    const params: Record<string, string> = {};
    if (search) params.search = search;
    if (statusFilter && statusFilter !== 'all') params.status_filter = statusFilter;
    const response = await apiClient.get<CompanyItem[]>('/companies/', { params });
    return response.data;
  },

  createCompany: async (data: {
    name: string;
    slug: string;
    industry?: string;
    description?: string;
    website?: string;
    subscription_plan?: string;
  }): Promise<CompanyItem> => {
    const response = await apiClient.post<CompanyItem>('/companies/', data);
    return response.data;
  },

  getCompany: async (companyId: string): Promise<CompanyItem> => {
    const response = await apiClient.get<CompanyItem>(`/companies/${companyId}`);
    return response.data;
  },

  updateCompany: async (
    companyId: string,
    data: Partial<CompanyItem>
  ): Promise<CompanyItem> => {
    const response = await apiClient.put<CompanyItem>(`/companies/${companyId}`, data);
    return response.data;
  },

  deleteCompany: async (companyId: string): Promise<{ detail: string; is_active: boolean }> => {
    const response = await apiClient.delete(`/companies/${companyId}`);
    return response.data;
  },

  // Company Settings (for Company Admins)
  getMyCompany: async (): Promise<CompanyItem> => {
    const response = await apiClient.get<CompanyItem>('/companies/me');
    return response.data;
  },

  updateMyCompany: async (data: {
    name?: string;
    industry?: string;
    description?: string;
    website?: string;
    logo_url?: string;
  }): Promise<CompanyItem> => {
    const response = await apiClient.put<CompanyItem>('/companies/me', data);
    return response.data;
  },

  getMyChatbotSettings: async (): Promise<ChatbotSettingsItem> => {
    const response = await apiClient.get<ChatbotSettingsItem>('/companies/me/chatbot-settings');
    return response.data;
  },

  updateMyChatbotSettings: async (
    data: Partial<ChatbotSettingsItem>
  ): Promise<ChatbotSettingsItem> => {
    const response = await apiClient.put<ChatbotSettingsItem>(
      '/companies/me/chatbot-settings',
      data
    );
    return response.data;
  },
};
