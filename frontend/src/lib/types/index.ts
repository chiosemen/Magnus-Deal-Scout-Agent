// User types
export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  full_name: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

// Authentication types
export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Search types
export enum SearchStatus {
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
}

export interface Search {
  id: number;
  user_id: number;
  name: string;
  keywords: string;
  marketplaces: string[];
  min_price?: number;
  max_price?: number;
  location?: string;
  radius_km?: number;
  status: SearchStatus;
  created_at: string;
  updated_at: string;
  last_run_at?: string;
}

export interface SearchCreate {
  name: string;
  keywords: string;
  marketplaces: string[];
  min_price?: number;
  max_price?: number;
  location?: string;
  radius_km?: number;
}

export interface SearchUpdate {
  name?: string;
  keywords?: string;
  marketplaces?: string[];
  min_price?: number;
  max_price?: number;
  location?: string;
  radius_km?: number;
  status?: SearchStatus;
}

// Listing types
export interface Listing {
  id: number;
  search_id: number;
  external_id: string;
  marketplace: string;
  title: string;
  description?: string;
  price: number;
  currency: string;
  url: string;
  image_url?: string;
  location?: string;
  posted_at?: string;
  scraped_at: string;
  is_saved: boolean;
  is_archived: boolean;
}

// Alert types
export enum AlertChannel {
  EMAIL = 'email',
  SMS = 'sms',
  WEBHOOK = 'webhook',
}

export interface Alert {
  id: number;
  user_id: number;
  search_id?: number;
  channel: AlertChannel;
  destination: string;
  min_price?: number;
  max_price?: number;
  keywords?: string[];
  is_active: boolean;
  created_at: string;
}

export interface AlertCreate {
  search_id?: number;
  channel: AlertChannel;
  destination: string;
  min_price?: number;
  max_price?: number;
  keywords?: string[];
}

// Dashboard types
export interface DashboardStats {
  total_searches: number;
  active_searches: number;
  total_listings: number;
  new_listings_24h: number;
  saved_listings: number;
  avg_price?: number;
  marketplaces: {
    [key: string]: number;
  };
}

// API Response types
export interface ApiError {
  detail: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
