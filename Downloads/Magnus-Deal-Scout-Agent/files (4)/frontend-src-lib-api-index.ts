// src/lib/api/alerts.ts

import apiClient from './client';
import { Alert, AlertChannel } from '../types';

export const alertsApi = {
  async getAlerts(searchId?: number): Promise<Alert[]> {
    const query = searchId ? `?search_id=${searchId}` : '';
    return apiClient.get<Alert[]>(`/alerts${query}`);
  },

  async getAlert(id: number): Promise<Alert> {
    return apiClient.get<Alert>(`/alerts/${id}`);
  },

  async createAlert(data: {
    search_id: number;
    channel: AlertChannel;
    config?: Record<string, any>;
  }): Promise<Alert> {
    return apiClient.post<Alert>('/alerts', data);
  },

  async updateAlert(id: number, data: Partial<{
    enabled: boolean;
    config: Record<string, any>;
  }>): Promise<Alert> {
    return apiClient.put<Alert>(`/alerts/${id}`, data);
  },

  async deleteAlert(id: number): Promise<void> {
    return apiClient.delete(`/alerts/${id}`);
  },

  async testAlert(id: number): Promise<{ message: string }> {
    return apiClient.post(`/alerts/${id}/test`);
  },
};

// src/lib/api/dashboard.ts

import { DashboardStats } from '../types';

export const dashboardApi = {
  async getStats(): Promise<DashboardStats> {
    return apiClient.get<DashboardStats>('/dashboard/stats');
  },

  async getActivity(days: number = 7): Promise<{
    date: string;
    new_listings: number;
    saved_listings: number;
  }[]> {
    return apiClient.get(`/dashboard/activity?days=${days}`);
  },
};

// Export all API services together
export { authApi } from './auth';
export { searchesApi } from './searches';
export { listingsApi } from './listings';
