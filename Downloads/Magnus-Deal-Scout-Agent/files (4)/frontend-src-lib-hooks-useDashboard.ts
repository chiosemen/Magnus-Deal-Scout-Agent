// src/lib/hooks/useDashboard.ts

import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../api';

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboardStats'],
    queryFn: () => dashboardApi.getStats(),
    staleTime: 60000, // 1 minute
    refetchInterval: 60000, // Refetch every minute
  });
}

export function useDashboardActivity(days: number = 7) {
  return useQuery({
    queryKey: ['dashboardActivity', days],
    queryFn: () => dashboardApi.getActivity(days),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// src/lib/hooks/useAlerts.ts

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { alertsApi } from '../api';
import { AlertChannel } from '../types';
import { toast } from 'sonner';

export function useAlerts(searchId?: number) {
  return useQuery({
    queryKey: ['alerts', searchId],
    queryFn: () => alertsApi.getAlerts(searchId),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useAlert(id: number) {
  return useQuery({
    queryKey: ['alert', id],
    queryFn: () => alertsApi.getAlert(id),
    enabled: !!id,
  });
}

export function useCreateAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      search_id: number;
      channel: AlertChannel;
      config?: Record<string, any>;
    }) => alertsApi.createAlert(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alert created successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create alert');
    },
  });
}

export function useUpdateAlert(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<{
      enabled: boolean;
      config: Record<string, any>;
    }>) => alertsApi.updateAlert(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alert', id] });
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alert updated successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update alert');
    },
  });
}

export function useDeleteAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => alertsApi.deleteAlert(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alert deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete alert');
    },
  });
}

export function useTestAlert() {
  return useMutation({
    mutationFn: (id: number) => alertsApi.testAlert(id),
    onSuccess: () => {
      toast.success('Test notification sent!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to send test alert');
    },
  });
}
