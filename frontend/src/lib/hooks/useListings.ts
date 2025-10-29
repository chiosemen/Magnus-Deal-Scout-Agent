import { useState, useEffect } from 'react';
import { listingsApi } from '@/lib/api';
import type { Listing } from '@/lib/types';

interface UseListingsParams {
  searchId?: number;
  marketplace?: string;
  minPrice?: number;
  maxPrice?: number;
  isSaved?: boolean;
  autoFetch?: boolean;
}

export function useListings(params: UseListingsParams = {}) {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (params.autoFetch !== false) {
      fetchListings();
    }
  }, [params.searchId, params.marketplace, params.minPrice, params.maxPrice, params.isSaved]);

  const fetchListings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listingsApi.getAll({
        search_id: params.searchId,
        marketplace: params.marketplace,
        min_price: params.minPrice,
        max_price: params.maxPrice,
        is_saved: params.isSaved,
      });
      setListings(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch listings');
    } finally {
      setLoading(false);
    }
  };

  const fetchRecent = async (hours: number = 24) => {
    try {
      setLoading(true);
      setError(null);
      const data = await listingsApi.getRecent(hours);
      setListings(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch recent listings');
    } finally {
      setLoading(false);
    }
  };

  const fetchSaved = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listingsApi.getSaved();
      setListings(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch saved listings');
    } finally {
      setLoading(false);
    }
  };

  const toggleSave = async (id: number, isSaved: boolean) => {
    try {
      const updated = await listingsApi.toggleSave(id, isSaved);
      setListings(listings.map(l => l.id === id ? updated : l));
      return updated;
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to update listing';
      setError(message);
      throw err;
    }
  };

  const toggleArchive = async (id: number, isArchived: boolean) => {
    try {
      const updated = await listingsApi.toggleArchive(id, isArchived);
      setListings(listings.map(l => l.id === id ? updated : l));
      return updated;
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to update listing';
      setError(message);
      throw err;
    }
  };

  return {
    listings,
    loading,
    error,
    fetchListings,
    fetchRecent,
    fetchSaved,
    toggleSave,
    toggleArchive,
  };
}
