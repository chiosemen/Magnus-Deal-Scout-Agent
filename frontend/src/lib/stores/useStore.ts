import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/lib/types';

interface AppState {
  // User state
  user: User | null;
  setUser: (user: User | null) => void;

  // UI state
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  // Filters
  selectedMarketplaces: string[];
  setSelectedMarketplaces: (marketplaces: string[]) => void;
  priceRange: [number, number] | null;
  setPriceRange: (range: [number, number] | null) => void;

  // Reset functions
  resetFilters: () => void;
  reset: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // User state
      user: null,
      setUser: (user) => set({ user }),

      // UI state
      sidebarOpen: true,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

      // Filters
      selectedMarketplaces: [],
      setSelectedMarketplaces: (marketplaces) => set({ selectedMarketplaces: marketplaces }),
      priceRange: null,
      setPriceRange: (range) => set({ priceRange: range }),

      // Reset functions
      resetFilters: () =>
        set({
          selectedMarketplaces: [],
          priceRange: null,
        }),
      reset: () =>
        set({
          user: null,
          sidebarOpen: true,
          selectedMarketplaces: [],
          priceRange: null,
        }),
    }),
    {
      name: 'deal-scout-storage',
      partializ: (state) => ({
        sidebarOpen: state.sidebarOpen,
      }),
    }
  )
);
