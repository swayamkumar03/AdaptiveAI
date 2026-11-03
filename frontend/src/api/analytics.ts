// src/api/analytics.ts
import apiClient from './client';
import {
  AccuracyAnalyticsResponse,
  AnalyticsOverview,
  FeedbackAnalyticsResponse,
  KnowledgeGapsResponse,
  QuestionsAnalyticsResponse,
} from '../types/api';

export const analyticsApi = {
  getOverview: async (startDate?: string, endDate?: string): Promise<AnalyticsOverview> => {
    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await apiClient.get<AnalyticsOverview>('/analytics/overview', { params });
    return response.data;
  },

  getQuestions: async (
    limit: number = 20,
    offset: number = 0,
    startDate?: string,
    endDate?: string
  ): Promise<QuestionsAnalyticsResponse> => {
    const params: Record<string, any> = { limit, offset };
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await apiClient.get<QuestionsAnalyticsResponse>('/analytics/questions', { params });
    return response.data;
  },

  getFeedback: async (startDate?: string, endDate?: string): Promise<FeedbackAnalyticsResponse> => {
    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await apiClient.get<FeedbackAnalyticsResponse>('/analytics/feedback', { params });
    return response.data;
  },

  getKnowledgeGaps: async (
    limit: number = 20,
    offset: number = 0,
    startDate?: string,
    endDate?: string
  ): Promise<KnowledgeGapsResponse> => {
    const params: Record<string, any> = { limit, offset };
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await apiClient.get<KnowledgeGapsResponse>('/analytics/knowledge-gaps', { params });
    return response.data;
  },

  getAccuracy: async (startDate?: string, endDate?: string): Promise<AccuracyAnalyticsResponse> => {
    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await apiClient.get<AccuracyAnalyticsResponse>('/analytics/accuracy', { params });
    return response.data;
  },
};
