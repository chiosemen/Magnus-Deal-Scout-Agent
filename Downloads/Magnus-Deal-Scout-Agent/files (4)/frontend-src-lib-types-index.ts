// src/lib/types/index.ts

export type Marketplace = 'ebay' | 'facebook' | 'gumtree' | 'craigslist';

export type SearchStatus = 'active' | 'paused' | 'disabled';

export type SubscriptionTier = 'free' | 'starter' | 'pro' | 'business';

export type AlertChannel = 'email' | 'sms' | 'push' | 'webhook';

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  subscription_tier: SubscriptionTier;
  created_at: string;
  updated_at: string;
}

export interface Search {
  id: number;
  user_id: number;
  name: string;
  keywords: string;
  marketplaces: Marketplace[];
  location?: string;
  radius_km?: number;
  min_price?: number;
  max_price?: number;
  filters: Record<string, any>;
  status: SearchStatus;
  check_interval_minutes: number;
  last_checked_at?: string;
  created_at: string;
  updated_at: string;
  _count?: {
    listings: number;
  };
}

export interface Listing {
  id: number;
  search_id: number;
  external_id: string;
  marketplace: Marketplace;
  title: string;
  description?: string;
  price: number;
  currency: string;
  location?: string;
  url: string;
  image_urls: string[];
  seller_name?: string;
  seller_rating?: number;
  is_featured: boolean;
  is_saved: boolean;
  metadata: Record<string, any>;
  posted_at?: string;
  scraped_at: string;
  created_at: string;
  search?: Search;
}

export interface Alert {
  id: number;
  user_id: number;
  search_id: number;
  channel: AlertChannel;
  enabled: boolean;
  config: Record<string, any>;
  last_triggered_at?: string;
  created_at: string;
  updated_at: string;
}

export interface SearchFormData {
  name: string;
  keywords: string;
  marketplaces: Marketplace[];
  location?: string;
  radius_km?: number;
  min_price?: number;
  max_price?: number;
  check_interval_minutes: number;
  alerts?: {
    channel: AlertChannel;
    enabled: boolean;
    config?: Record<string, any>;
  }[];
}

export interface ListingFilters {
  search_id?: number;
  marketplaces?: Marketplace[];
  min_price?: number;
  max_price?: number;
  location?: string;
  is_featured?: boolean;
  is_saved?: boolean;
  posted_after?: string;
  sort_by?: 'price_asc' | 'price_desc' | 'newest' | 'oldest';
  page?: number;
  per_page?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  full_name: string;
}

export interface DashboardStats {
  total_searches: number;
  active_searches: number;
  total_listings: number;
  new_listings_today: number;
  saved_listings: number;
}
