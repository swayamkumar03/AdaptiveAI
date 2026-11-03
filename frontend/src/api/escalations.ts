// src/api/escalations.ts
import apiClient from './client';
import { EscalationItem } from '../types/api';

export const escalationsApi = {
  listEscalations: async (status?: string, reason?: string): Promise<EscalationItem[]> => {
    const params: Record<string, string> = {};
    if (status) params.status = status;
    if (reason) params.reason = reason;

    const response = await apiClient.get<EscalationItem[]>('/escalations/', { params });
    return response.data;
  },

  getEscalation: async (escalationId: string): Promise<EscalationItem> => {
    const response = await apiClient.get<EscalationItem>(`/escalations/${escalationId}`);
    return response.data;
  },

  assignEscalation: async (escalationId: string, agentId?: string): Promise<EscalationItem> => {
    const payload = agentId ? { agent_id: agentId } : {};
    const response = await apiClient.put<EscalationItem>(`/escalations/${escalationId}/assign`, payload);
    return response.data;
  },

  resolveEscalation: async (
    escalationId: string,
    resolutionNotes: string,
    createExperience: boolean = true
  ): Promise<any> => {
    const response = await apiClient.put(`/escalations/${escalationId}/resolve`, {
      resolution_notes: resolutionNotes,
      create_experience: createExperience,
    });
    return response.data;
  },
};
