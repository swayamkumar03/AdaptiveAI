// src/api/experiences.ts
import apiClient from './client';
import { ExperienceItem } from '../types/api';

export const experiencesApi = {
  listExperiences: async (verificationStatus?: string): Promise<ExperienceItem[]> => {
    const params: Record<string, string> = {};
    if (verificationStatus) {
      params.verification_status = verificationStatus;
    }
    const response = await apiClient.get<ExperienceItem[]>('/experiences/', { params });
    return response.data;
  },

  approveExperience: async (experienceId: string): Promise<ExperienceItem> => {
    const response = await apiClient.put<ExperienceItem>(`/experiences/${experienceId}/approve`);
    return response.data;
  },

  rejectExperience: async (experienceId: string, reason?: string): Promise<ExperienceItem> => {
    const response = await apiClient.put<ExperienceItem>(`/experiences/${experienceId}/reject`, {
      reason: reason || undefined,
    });
    return response.data;
  },

  createExperience: async (payload: { question: string; original_answer: string; corrected_answer: string }): Promise<ExperienceItem> => {
    const response = await apiClient.post<ExperienceItem>('/experiences/', payload);
    return response.data;
  },
};
