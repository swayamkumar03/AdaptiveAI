// src/api/chat.ts
import apiClient from './client';
import { ChatResponse } from '../types/api';

export const chatApi = {
  sendMessage: async (message: string, conversationId?: string): Promise<ChatResponse> => {
    const payload: { message: string; conversation_id?: string } = { message };
    if (conversationId) {
      payload.conversation_id = conversationId;
    }
    const response = await apiClient.post<ChatResponse>('/chat/', payload);
    return response.data;
  },
};
