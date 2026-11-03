// src/api/documents.ts
import apiClient from './client';
import { DocumentItem } from '../types/api';

export const documentsApi = {
  listDocuments: async (): Promise<DocumentItem[]> => {
    const response = await apiClient.get<DocumentItem[]>('/documents/');
    return response.data;
  },

  uploadDocument: async (file: File, onUploadProgress?: (percent: number) => void): Promise<DocumentItem> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<DocumentItem>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onUploadProgress) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onUploadProgress(percent);
        }
      },
    });
    return response.data;
  },

  deleteDocument: async (documentId: string): Promise<void> => {
    await apiClient.delete(`/documents/${documentId}`);
  },
};
