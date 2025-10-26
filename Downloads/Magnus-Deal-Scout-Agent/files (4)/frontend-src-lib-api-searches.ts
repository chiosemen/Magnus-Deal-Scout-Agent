// src/lib/api/searches.ts

import apiClient from './client';
import { Search, SearchFormData, PaginatedResponse } from '../types';
import { buildQueryString } from '../utils';

export const searchesApi = {
  async getSearches(params?: {
    status?: string;
    page?: number;
    per_page?: number;
  }): Promise<PaginatedResponse<Search>> {
    const query = params ? `?${buildQueryString(params)}` : '';
    return apiClient.get<PaginatedResponse<Search>>(`/searches${query}`);
  },

  async getSearch(id: number): Promise<Search> {
    return apiClient.get<Search>(`/searches/${id}`);
  },

  async createSearch(data: SearchFormData): Promise<Search> {
    return apiClient.post<Search>('/searches', data);
  },

  async updateSearch(id: number, data: Partial<SearchFormData>): Promise<Search> {
    return apiClient.put<Search>(`/searches/${id}`, data);
  },

  async deleteSearch(id: number): Promise<void> {
    return apiClient.delete(`/searches/${id}`);
  },

  async pauseSearch(id: number): Promise<Search> {
    return apiClient.post<Search>(`/searches/${id}/pause`);
  },

  async resumeSearch(id: number): Promise<Search> {
    return apiClient.post<Search>(`/searches/${id}/resume`);
  },

  async triggerSearch(id: number): Promise<{ message: string; task_id: string }> {
    return apiClient.post(`/searches/${id}/trigger`);
  },

  async getSearchStats(id: number): Promise<{
    total_listings: number;
    new_listings_today: number;
    average_price: number;
    price_trend: 'up' | 'down' | 'stable';
  }> {
    return apiClient.get(`/searches/${id}/stats`);
  },
};
