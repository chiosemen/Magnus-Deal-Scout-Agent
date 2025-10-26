// src/lib/api/listings.ts

import apiClient from './client';
import { Listing, ListingFilters, PaginatedResponse } from '../types';
import { buildQueryString } from '../utils';

export const listingsApi = {
  async getListings(filters?: ListingFilters): Promise<PaginatedResponse<Listing>> {
    const query = filters ? `?${buildQueryString(filters)}` : '';
    return apiClient.get<PaginatedResponse<Listing>>(`/listings${query}`);
  },

  async getListing(id: number): Promise<Listing> {
    return apiClient.get<Listing>(`/listings/${id}`);
  },

  async saveListing(id: number): Promise<Listing> {
    return apiClient.post<Listing>(`/listings/${id}/save`);
  },

  async unsaveListing(id: number): Promise<Listing> {
    return apiClient.delete<Listing>(`/listings/${id}/save`);
  },

  async getSavedListings(params?: {
    page?: number;
    per_page?: number;
  }): Promise<PaginatedResponse<Listing>> {
    const query = params ? `?${buildQueryString(params)}` : '';
    return apiClient.get<PaginatedResponse<Listing>>(`/listings/saved${query}`);
  },

  async getRecentListings(limit: number = 10): Promise<Listing[]> {
    return apiClient.get<Listing[]>(`/listings/recent?limit=${limit}`);
  },

  async exportListings(searchId: number, format: 'csv' | 'json' = 'csv'): Promise<Blob> {
    const response = await apiClient.getClient().get(`/listings/export/${searchId}`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },
};
