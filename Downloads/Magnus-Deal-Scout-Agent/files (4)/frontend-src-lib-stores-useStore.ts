// src/lib/stores/useStore.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ListingFilters, Marketplace } from '../types';

interface AppState {
  // Listing filters
  listingFilters: ListingFilters;
  setListingFilters: (filters: Partial<ListingFilters>) => void;
  resetListingFilters: () => void;

  // UI state
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  // Recently viewed listings
  recentlyViewedListings: number[];
  addRecentlyViewedListing: (id: number) => void;

  // Theme
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

const defaultFilters: ListingFilters = {
  page: 1,
  per_page: 20,
  sort_by: 'newest',
};

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // Listing filters
      listingFilters: defaultFilters,
      setListingFilters: (filters) =>
        set((state) => ({
          listingFilters: { ...state.listingFilters, ...filters, page: 1 },
        })),
      resetListingFilters: () => set({ listingFilters: defaultFilters }),

      // UI state
      sidebarOpen: true,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

      // Recently viewed listings
      recentlyViewedListings: [],
      addRecentlyViewedListing: (id) =>
        set((state) => ({
          recentlyViewedListings: [
            id,
            ...state.recentlyViewedListings.filter((listingId) => listingId !== id),
          ].slice(0, 20), // Keep only last 20
        })),

      // Theme
      theme: 'system',
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'deal-scout-storage',
      partialize: (state) => ({
        recentlyViewedListings: state.recentlyViewedListings,
        theme: state.theme,
      }),
    }
  )
);

// Convenience selectors
export const useListingFilters = () => useStore((state) => state.listingFilters);
export const useSidebar = () => useStore((state) => ({
  isOpen: state.sidebarOpen,
  toggle: state.toggleSidebar,
  setOpen: state.setSidebarOpen,
}));
