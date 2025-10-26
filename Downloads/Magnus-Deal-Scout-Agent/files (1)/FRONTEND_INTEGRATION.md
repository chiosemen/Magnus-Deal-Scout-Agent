# Frontend Integration Guide

## Quick Reference for Your Next.js Frontend

This guide shows you exactly how to integrate your Next.js frontend with the backend.

## Base URL

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
```

## Authentication Setup

### 1. Create an API client with auth interceptor

```typescript
// lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          `${api.defaults.baseURL}/auth/refresh`,
          { refresh_token: refreshToken }
        );
        
        const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Redirect to login
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### 2. Authentication Service

```typescript
// services/auth.service.ts
import api from '../lib/api';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

export const authService = {
  async register(data: RegisterData) {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  async login(credentials: LoginCredentials) {
    const response = await api.post('/auth/login', credentials);
    const { access_token, refresh_token } = response.data;
    
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    return response.data;
  },

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  },

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }
};
```

### 3. Auth Context (React Context)

```typescript
// contexts/AuthContext.tsx
'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/auth.service';
import api from '../lib/api';

interface User {
  id: number;
  email: string;
  full_name: string;
  subscription_tier: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: any) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load user on mount
    if (authService.isAuthenticated()) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await api.get('/users/me');
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      authService.logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    await authService.login({ email, password });
    await fetchUser();
  };

  const logout = () => {
    setUser(null);
    authService.logout();
  };

  const register = async (data: any) => {
    await authService.register(data);
    await login(data.email, data.password);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

## Data Services

### User Service

```typescript
// services/user.service.ts
import api from '../lib/api';

export const userService = {
  async getProfile() {
    const response = await api.get('/users/me');
    return response.data;
  },

  async getStats() {
    const response = await api.get('/users/me/stats');
    return response.data;
  },

  async updateProfile(data: { full_name?: string; phone_number?: string; webhook_url?: string }) {
    const response = await api.put('/users/me', data);
    return response.data;
  }
};
```

### Search Service

```typescript
// services/search.service.ts
import api from '../lib/api';

export interface SearchConfig {
  name: string;
  description?: string;
  criteria: {
    keywords: string[];
    min_price?: number;
    max_price?: number;
    exclude_keywords?: string[];
    location?: string;
    condition?: string[];
  };
  marketplaces: ('ebay' | 'facebook' | 'gumtree' | 'craigslist')[];
  alert_channels: ('email' | 'sms' | 'push' | 'webhook')[];
  check_frequency_minutes: number;
}

export const searchService = {
  async list(status?: 'active' | 'paused' | 'disabled') {
    const params = status ? { status } : {};
    const response = await api.get('/searches/', { params });
    return response.data;
  },

  async get(id: number) {
    const response = await api.get(`/searches/${id}`);
    return response.data;
  },

  async create(data: SearchConfig) {
    const response = await api.post('/searches/', data);
    return response.data;
  },

  async update(id: number, data: Partial<SearchConfig>) {
    const response = await api.put(`/searches/${id}`, data);
    return response.data;
  },

  async delete(id: number) {
    await api.delete(`/searches/${id}`);
  },

  async pause(id: number) {
    const response = await api.post(`/searches/${id}/pause`);
    return response.data;
  },

  async resume(id: number) {
    const response = await api.post(`/searches/${id}/resume`);
    return response.data;
  }
};
```

### Listing Service

```typescript
// services/listing.service.ts
import api from '../lib/api';

export const listingService = {
  async list(filters?: {
    search_id?: number;
    is_active?: boolean;
    is_hidden?: boolean;
    is_saved?: boolean;
    limit?: number;
    offset?: number;
  }) {
    const response = await api.get('/listings/', { params: filters });
    return response.data;
  },

  async getRecent(hours: number = 24) {
    const response = await api.get('/listings/recent', { params: { hours } });
    return response.data;
  },

  async get(id: number) {
    const response = await api.get(`/listings/${id}`);
    return response.data;
  },

  async update(id: number, data: { is_saved?: boolean; is_hidden?: boolean }) {
    const response = await api.put(`/listings/${id}`, data);
    return response.data;
  }
};
```

### Template Service

```typescript
// services/template.service.ts
import api from '../lib/api';

export const templateService = {
  async list(filters?: { category?: string; featured_only?: boolean }) {
    const response = await api.get('/templates/', { params: filters });
    return response.data;
  },

  async get(id: number) {
    const response = await api.get(`/templates/${id}`);
    return response.data;
  }
};
```

## Component Examples

### Login Form

```typescript
// components/LoginForm.tsx
'use client';

import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useRouter } from 'next/navigation';

export default function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded">
          {error}
        </div>
      )}
      
      <div>
        <label className="block text-sm font-medium mb-1">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full px-3 py-2 border rounded-md"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full px-3 py-2 border rounded-md"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### Listing Card

```typescript
// components/ListingCard.tsx
import { useState } from 'react';
import { listingService } from '../services/listing.service';

interface Listing {
  id: number;
  title: string;
  price: number;
  currency: string;
  url: string;
  marketplace: string;
  location: string;
  first_seen_at: string;
  is_saved: boolean;
  is_hidden: boolean;
}

export default function ListingCard({ listing: initialListing }: { listing: Listing }) {
  const [listing, setListing] = useState(initialListing);
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    try {
      const updated = await listingService.update(listing.id, {
        is_saved: !listing.is_saved
      });
      setListing(updated);
    } catch (error) {
      console.error('Failed to save listing:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleHide = async () => {
    setLoading(true);
    try {
      await listingService.update(listing.id, { is_hidden: true });
      // Optionally remove from UI
    } catch (error) {
      console.error('Failed to hide listing:', error);
    } finally {
      setLoading(false);
    }
  };

  const timeAgo = (date: string) => {
    const seconds = Math.floor((new Date().getTime() - new Date(date).getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  if (listing.is_hidden) return null;

  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-lg line-clamp-2">{listing.title}</h3>
        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
          {listing.marketplace.toUpperCase()}
        </span>
      </div>

      <div className="space-y-2">
        <p className="text-2xl font-bold text-green-600">
          {listing.currency} {listing.price.toFixed(2)}
        </p>

        <div className="flex items-center text-sm text-gray-600">
          <span>{listing.location || 'Location not specified'}</span>
          <span className="mx-2">•</span>
          <span>{timeAgo(listing.first_seen_at)}</span>
        </div>

        <div className="flex gap-2 mt-4">
          <a
            href={listing.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded text-center hover:bg-blue-700"
          >
            View Listing
          </a>

          <button
            onClick={handleSave}
            disabled={loading}
            className={`px-4 py-2 rounded border ${
              listing.is_saved
                ? 'bg-yellow-100 border-yellow-500 text-yellow-700'
                : 'bg-white border-gray-300'
            }`}
          >
            {listing.is_saved ? '★' : '☆'}
          </button>

          <button
            onClick={handleHide}
            disabled={loading}
            className="px-4 py-2 rounded border border-gray-300 hover:bg-gray-50"
          >
            Hide
          </button>
        </div>
      </div>
    </div>
  );
}
```

### Search Configuration Form

```typescript
// components/SearchForm.tsx
'use client';

import { useState } from 'react';
import { searchService, SearchConfig } from '../services/search.service';

export default function SearchForm({ onSuccess }: { onSuccess?: () => void }) {
  const [formData, setFormData] = useState<Partial<SearchConfig>>({
    name: '',
    description: '',
    criteria: {
      keywords: [],
      max_price: undefined,
      exclude_keywords: [],
    },
    marketplaces: ['ebay'],
    alert_channels: ['email'],
    check_frequency_minutes: 30,
  });

  const [keywordInput, setKeywordInput] = useState('');
  const [loading, setLoading] = useState(false);

  const addKeyword = () => {
    if (keywordInput.trim()) {
      setFormData({
        ...formData,
        criteria: {
          ...formData.criteria!,
          keywords: [...(formData.criteria?.keywords || []), keywordInput.trim()]
        }
      });
      setKeywordInput('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await searchService.create(formData as SearchConfig);
      onSuccess?.();
    } catch (error) {
      console.error('Failed to create search:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium mb-1">Search Name</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
          className="w-full px-3 py-2 border rounded-md"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Keywords</label>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={keywordInput}
            onChange={(e) => setKeywordInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addKeyword())}
            placeholder="Enter keyword and press Enter"
            className="flex-1 px-3 py-2 border rounded-md"
          />
          <button
            type="button"
            onClick={addKeyword}
            className="px-4 py-2 bg-gray-200 rounded"
          >
            Add
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {formData.criteria?.keywords?.map((keyword, index) => (
            <span
              key={index}
              className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
            >
              {keyword}
              <button
                type="button"
                onClick={() => {
                  const newKeywords = formData.criteria!.keywords!.filter((_, i) => i !== index);
                  setFormData({
                    ...formData,
                    criteria: { ...formData.criteria!, keywords: newKeywords }
                  });
                }}
                className="ml-2 text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Max Price (£)</label>
        <input
          type="number"
          value={formData.criteria?.max_price || ''}
          onChange={(e) => setFormData({
            ...formData,
            criteria: { ...formData.criteria!, max_price: parseFloat(e.target.value) }
          })}
          className="w-full px-3 py-2 border rounded-md"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Check Frequency</label>
        <select
          value={formData.check_frequency_minutes}
          onChange={(e) => setFormData({
            ...formData,
            check_frequency_minutes: parseInt(e.target.value)
          })}
          className="w-full px-3 py-2 border rounded-md"
        >
          <option value={30}>Every 30 minutes</option>
          <option value={60}>Every hour</option>
          <option value={180}>Every 3 hours</option>
          <option value={360}>Every 6 hours</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Creating...' : 'Create Search'}
      </button>
    </form>
  );
}
```

## Real-time Updates (Optional)

For real-time listing updates, you can poll the API:

```typescript
// hooks/useRealtimeListings.ts
import { useState, useEffect } from 'react';
import { listingService } from '../services/listing.service';

export function useRealtimeListings(intervalMs: number = 30000) {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchListings = async () => {
      try {
        const data = await listingService.getRecent(1); // Last hour
        setListings(data);
      } catch (error) {
        console.error('Failed to fetch listings:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchListings();
    const interval = setInterval(fetchListings, intervalMs);

    return () => clearInterval(interval);
  }, [intervalMs]);

  return { listings, loading };
}
```

## Environment Variables

Create `.env.local` in your Next.js project:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

## TypeScript Types

```typescript
// types/index.ts
export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  subscription_tier: 'free' | 'starter' | 'pro' | 'business';
  subscription_expires_at: string | null;
  created_at: string;
}

export interface SearchConfig {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  status: 'active' | 'paused' | 'disabled';
  criteria: {
    keywords: string[];
    min_price?: number;
    max_price?: number;
    exclude_keywords?: string[];
    location?: string;
    condition?: string[];
  };
  marketplaces: string[];
  alert_channels: string[];
  check_frequency_minutes: number;
  last_checked_at: string | null;
  total_matches_found: number;
  created_at: string;
  updated_at: string;
}

export interface Listing {
  id: number;
  search_config_id: number;
  external_id: string;
  marketplace: 'ebay' | 'facebook' | 'gumtree' | 'craigslist';
  url: string;
  title: string;
  description: string | null;
  price: number;
  currency: string;
  location: string | null;
  metadata: any;
  first_seen_at: string;
  last_seen_at: string;
  is_active: boolean;
  is_viewed: boolean;
  is_saved: boolean;
  is_hidden: boolean;
  created_at: string;
}

export interface SearchTemplate {
  id: number;
  name: string;
  description: string;
  category: string;
  config: any;
  usage_count: number;
  is_featured: boolean;
  created_at: string;
}

export interface UserStats {
  total_searches: number;
  active_searches: number;
  total_listings_found: number;
  alerts_sent_today: number;
  subscription_tier: string;
  searches_limit: number;
  searches_remaining: number;
}
```

## That's It!

You now have everything you need to integrate your Next.js frontend with the backend. The backend handles:

- ✅ Authentication
- ✅ Search management
- ✅ Marketplace monitoring
- ✅ Alerts
- ✅ Subscriptions

Your frontend just needs to make HTTP requests to these endpoints and display the data beautifully!
