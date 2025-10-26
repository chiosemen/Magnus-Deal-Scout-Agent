// src/lib/hooks/useListings.ts

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { listingsApi } from '../api';
import { ListingFilters } from '../types';
import { toast } from 'sonner';

export function useListings(filters?: ListingFilters) {
  return useQuery({
    queryKey: ['listings', filters],
    queryFn: () => listingsApi.getListings(filters),
    staleTime: 30000, // 30 seconds
    keepPreviousData: true,
  });
}

export function useListing(id: number) {
  return useQuery({
    queryKey: ['listing', id],
    queryFn: () => listingsApi.getListing(id),
    enabled: !!id,
  });
}

export function useRecentListings(limit: number = 10) {
  return useQuery({
    queryKey: ['recentListings', limit],
    queryFn: () => listingsApi.getRecentListings(limit),
    staleTime: 60000, // 1 minute
  });
}

export function useSavedListings(params?: { page?: number; per_page?: number }) {
  return useQuery({
    queryKey: ['savedListings', params],
    queryFn: () => listingsApi.getSavedListings(params),
    staleTime: 30000,
  });
}

export function useSaveListing() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => listingsApi.saveListing(id),
    onSuccess: (listing) => {
      queryClient.invalidateQueries({ queryKey: ['listing', listing.id] });
      queryClient.invalidateQueries({ queryKey: ['listings'] });
      queryClient.invalidateQueries({ queryKey: ['savedListings'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
      toast.success('Listing saved!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to save listing');
    },
  });
}

export function useUnsaveListing() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => listingsApi.unsaveListing(id),
    onSuccess: (listing) => {
      queryClient.invalidateQueries({ queryKey: ['listing', listing.id] });
      queryClient.invalidateQueries({ queryKey: ['listings'] });
      queryClient.invalidateQueries({ queryKey: ['savedListings'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
      toast.success('Listing removed from saved');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to unsave listing');
    },
  });
}

export function useExportListings() {
  return useMutation({
    mutationFn: ({ searchId, format }: { searchId: number; format: 'csv' | 'json' }) =>
      listingsApi.exportListings(searchId, format),
    onSuccess: (blob, { format }) => {
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `listings-${Date.now()}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Listings exported successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to export listings');
    },
  });
}
