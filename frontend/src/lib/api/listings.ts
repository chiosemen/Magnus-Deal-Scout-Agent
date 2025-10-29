import apiClient from './client';
import type { Listing } from '@/lib/types';

export const listingsApi = {
  /**
   * Get all listings with optional filters
   */
  getAll: async (params?: {
    search_id?: number;
    marketplace?: string;
    min_price?: number;
    max_price?: number;
    is_saved?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<Listing[]> => {
    const response = await apiClient.axios.get<Listing[]>('/listings', { params });
    return response.data;
  },

  /**
   * Get recent listings
   */
  getRecent: async (hours: number = 24): Promise<Listing[]> => {
    const response = await apiClient.axios.get<Listing[]>('/listings/recent', {
      params: { hours },
    });
    return response.data;
  },

  /**
   * Get saved listings
   */
  getSaved: async (): Promise<Listing[]> => {
    const response = await apiClient.axios.get<Listing[]>('/listings/saved');
    return response.data;
  },

  /**
   * Get a single listing by ID
   */
  getById: async (id: number): Promise<Listing> => {
    const response = await apiClient.axios.get<Listing>(`/listings/${id}`);
    return response.data;
  },

  /**
   * Save/unsave a listing
   */
  toggleSave: async (id: number, isSaved: boolean): Promise<Listing> => {
    const response = await apiClient.axios.patch<Listing>(`/listings/${id}`, {
      is_saved: isSaved,
    });
    return response.data;
  },

  /**
   * Archive/unarchive a listing
   */
  toggleArchive: async (id: number, isArchived: boolean): Promise<Listing> => {
    const response = await apiClient.axios.patch<Listing>(`/listings/${id}`, {
      is_archived: isArchived,
    });
    return response.data;
  },
};
