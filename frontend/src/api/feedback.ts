// src/api/feedback.ts
import apiClient from './client';
import { FeedbackItem } from '../types/api';

export interface SubmitFeedbackPayload {
  message_id: string;
  rating: 'POSITIVE' | 'NEGATIVE';
  feedback_category?: 'INCORRECT' | 'INCOMPLETE' | 'MISUNDERSTOOD' | 'OTHER' | null;
  user_correction?: string | null;
  comment?: string | null;
}

export const feedbackApi = {
  listFeedback: async (status?: string, rating?: string): Promise<FeedbackItem[]> => {
    const params: Record<string, string> = {};
    if (status) params.status = status;
    if (rating) params.rating = rating;

    const response = await apiClient.get<FeedbackItem[]>('/feedback/', { params });
    return response.data;
  },

  submitFeedback: async (payload: SubmitFeedbackPayload): Promise<{ feedback_id: string; status: string }> => {
    const response = await apiClient.post('/feedback/', payload);
    return response.data;
  },

  reviewFeedback: async (feedbackId: string): Promise<any> => {
    const response = await apiClient.put(`/feedback/${feedbackId}/review`);
    return response.data;
  },
};
