import { useState, useEffect } from 'react';
import { searchesApi } from '@/lib/api';
import type { Search, SearchCreate, SearchUpdate } from '@/lib/types';

export function useSearches() {
  const [searches, setSearches] = useState<Search[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSearches();
  }, []);

  const fetchSearches = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await searchesApi.getAll();
      setSearches(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch searches');
    } finally {
      setLoading(false);
    }
  };

  const createSearch = async (data: SearchCreate) => {
    try {
      const newSearch = await searchesApi.create(data);
      setSearches([...searches, newSearch]);
      return newSearch;
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to create search';
      setError(message);
      throw err;
    }
  };

  const updateSearch = async (id: number, data: SearchUpdate) => {
    try {
      const updated = await searchesApi.update(id, data);
      setSearches(searches.map(s => s.id === id ? updated : s));
      return updated;
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to update search';
      setError(message);
      throw err;
    }
  };

  const deleteSearch = async (id: number) => {
    try {
      await searchesApi.delete(id);
      setSearches(searches.filter(s => s.id !== id));
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to delete search';
      setError(message);
      throw err;
    }
  };

  const triggerSearch = async (id: number) => {
    try {
      const result = await searchesApi.trigger(id);
      return result;
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to trigger search';
      setError(message);
      throw err;
    }
  };

  return {
    searches,
    loading,
    error,
    fetchSearches,
    createSearch,
    updateSearch,
    deleteSearch,
    triggerSearch,
  };
}
