import apiClient from './client';
import type { Search, SearchCreate, SearchUpdate } from '@/lib/types';

export const searchesApi = {
  /**
   * Get all searches for current user
   */
  getAll: async (): Promise<Search[]> => {
    const response = await apiClient.axios.get<Search[]>('/searches');
    return response.data;
  },

  /**
   * Get a single search by ID
   */
  getById: async (id: number): Promise<Search> => {
    const response = await apiClient.axios.get<Search>(`/searches/${id}`);
    return response.data;
  },

  /**
   * Create a new search
   */
  create: async (data: SearchCreate): Promise<Search> => {
    const response = await apiClient.axios.post<Search>('/searches', data);
    return response.data;
  },

  /**
   * Update a search
   */
  update: async (id: number, data: SearchUpdate): Promise<Search> => {
    const response = await apiClient.axios.put<Search>(`/searches/${id}`, data);
    return response.data;
  },

  /**
   * Delete a search
   */
  delete: async (id: number): Promise<void> => {
    await apiClient.axios.delete(`/searches/${id}`);
  },

  /**
   * Trigger a search manually
   */
  trigger: async (id: number): Promise<{ message: string; task_id: string }> => {
    const response = await apiClient.axios.post<{ message: string; task_id: string }>(
      `/searches/${id}/trigger`
    );
    return response.data;
  },
};
