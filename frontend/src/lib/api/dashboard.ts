import apiClient from './client';
import type { DashboardStats } from '@/lib/types';

export const dashboardApi = {
  /**
   * Get dashboard statistics
   */
  getStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.axios.get<DashboardStats>('/dashboard/stats');
    return response.data;
  },
};
