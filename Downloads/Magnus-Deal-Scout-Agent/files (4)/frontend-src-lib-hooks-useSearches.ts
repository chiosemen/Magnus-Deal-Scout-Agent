// src/lib/hooks/useSearches.ts

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { searchesApi } from '../api';
import { SearchFormData } from '../types';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';

export function useSearches(params?: { status?: string; page?: number; per_page?: number }) {
  return useQuery({
    queryKey: ['searches', params],
    queryFn: () => searchesApi.getSearches(params),
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

export function useSearch(id: number) {
  return useQuery({
    queryKey: ['search', id],
    queryFn: () => searchesApi.getSearch(id),
    enabled: !!id,
  });
}

export function useSearchStats(id: number) {
  return useQuery({
    queryKey: ['searchStats', id],
    queryFn: () => searchesApi.getSearchStats(id),
    enabled: !!id,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useCreateSearch() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SearchFormData) => searchesApi.createSearch(data),
    onSuccess: (search) => {
      queryClient.invalidateQueries({ queryKey: ['searches'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
      toast.success(`Search "${search.name}" created successfully!`);
      router.push(`/searches/${search.id}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create search');
    },
  });
}

export function useUpdateSearch(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<SearchFormData>) => searchesApi.updateSearch(id, data),
    onSuccess: (search) => {
      queryClient.invalidateQueries({ queryKey: ['search', id] });
      queryClient.invalidateQueries({ queryKey: ['searches'] });
      toast.success(`Search "${search.name}" updated successfully!`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update search');
    },
  });
}

export function useDeleteSearch() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => searchesApi.deleteSearch(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['searches'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
      toast.success('Search deleted successfully');
      router.push('/searches');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete search');
    },
  });
}

export function usePauseSearch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => searchesApi.pauseSearch(id),
    onSuccess: (search) => {
      queryClient.invalidateQueries({ queryKey: ['search', search.id] });
      queryClient.invalidateQueries({ queryKey: ['searches'] });
      toast.success(`Search "${search.name}" paused`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to pause search');
    },
  });
}

export function useResumeSearch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => searchesApi.resumeSearch(id),
    onSuccess: (search) => {
      queryClient.invalidateQueries({ queryKey: ['search', search.id] });
      queryClient.invalidateQueries({ queryKey: ['searches'] });
      toast.success(`Search "${search.name}" resumed`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to resume search');
    },
  });
}

export function useTriggerSearch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => searchesApi.triggerSearch(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['search', id] });
      toast.success('Search triggered! New listings will appear shortly.');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to trigger search');
    },
  });
}
