# 🚀 Deal Scout + Marketplace Monitor - Complete Integration Guide

## 🎯 Overview

This guide shows you how to integrate your **Marketplace Monitor Backend** with the **Deal Scout Frontend** - creating a unified platform that combines:

- 🛒 **Marketplace Deal Monitoring** (eBay, Facebook, Gumtree, Craigslist)
- 🔗 **Link-in-Bio & Creator Tools** (Pillar-style)
- 📊 **CRM & Marketing Automation** (HighLevel-style)
- 💰 **E-commerce Management** (Deal tracking & sales)

**The Result:** A powerful all-in-one platform for deal hunters, resellers, and e-commerce entrepreneurs!

---

## 🏗️ Unified Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   DEAL SCOUT FRONTEND                        │
│              (Next.js 14 + TypeScript)                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  🔗 Link-in-Bio      📊 CRM           🛒 Deal Monitoring    │
│  📚 Courses          📧 Campaigns     📦 Orders             │
│  🛍️ Store            📅 Calendar      📈 Analytics          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                            ↕️
┌─────────────────────────────────────────────────────────────┐
│              MARKETPLACE MONITOR BACKEND                      │
│            (FastAPI + PostgreSQL + Redis)                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ✅ User Auth (JWT)    ✅ Search Management                  │
│  ✅ eBay API           ✅ Facebook Scraper                    │
│  ✅ Listing Storage    ✅ Multi-channel Alerts               │
│  ✅ Celery Workers     ✅ Stripe Subscriptions               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Updated Deal Scout Structure (with Marketplace Monitor)

```
deal-scout-frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── forgot-password/
│   │   ├── (dashboard)/
│   │   │   ├── dashboard/              # Overview with deal metrics
│   │   │   │
│   │   │   ├── deals/                  # 🆕 MARKETPLACE MONITORING
│   │   │   │   ├── searches/           # Manage search configs
│   │   │   │   ├── listings/           # Browse found deals
│   │   │   │   ├── templates/          # Pre-built searches
│   │   │   │   └── alerts/             # Alert management
│   │   │   │
│   │   │   ├── contacts/               # CRM contacts
│   │   │   ├── pipeline/               # Sales pipeline
│   │   │   ├── campaigns/              # Marketing
│   │   │   ├── workflows/              # Automation
│   │   │   ├── calendar/               # Scheduling
│   │   │   ├── inbox/                  # Communication
│   │   │   ├── store/                  # Creator store
│   │   │   ├── courses/                # Course platform
│   │   │   ├── analytics/              # Analytics
│   │   │   └── settings/               # Settings
│   │   │
│   │   ├── (public)/
│   │   │   ├── [username]/             # Link-in-bio
│   │   │   ├── checkout/               # Checkout
│   │   │   └── booking/                # Public booking
│   │
│   ├── components/
│   │   ├── ui/                         # shadcn/ui
│   │   │
│   │   ├── deals/                      # 🆕 DEAL COMPONENTS
│   │   │   ├── SearchForm/             # Create search
│   │   │   ├── SearchList/             # List searches
│   │   │   ├── ListingCard/            # Display listing
│   │   │   ├── ListingGrid/            # Grid of listings
│   │   │   ├── ListingDetail/          # Detail view
│   │   │   ├── AlertSettings/          # Alert config
│   │   │   ├── TemplateSelector/       # Choose template
│   │   │   ├── MarketplaceToggle/      # Select marketplaces
│   │   │   └── DealFilters/            # Filter UI
│   │   │
│   │   ├── crm/                        # CRM components
│   │   ├── marketing/                  # Marketing
│   │   ├── store/                      # Store
│   │   ├── courses/                    # Courses
│   │   └── builders/                   # Visual builders
│   │
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts               # Base API client
│   │   │   ├── auth.ts                 # Auth endpoints
│   │   │   ├── deals.ts                # 🆕 Deal endpoints
│   │   │   ├── searches.ts             # 🆕 Search endpoints
│   │   │   ├── listings.ts             # 🆕 Listing endpoints
│   │   │   ├── contacts.ts             # CRM endpoints
│   │   │   └── campaigns.ts            # Marketing endpoints
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useSearches.ts          # 🆕 Search hooks
│   │   │   ├── useListings.ts          # 🆕 Listing hooks
│   │   │   ├── useTemplates.ts         # 🆕 Template hooks
│   │   │   └── useAlerts.ts            # 🆕 Alert hooks
│   │   │
│   │   ├── types/
│   │   │   ├── auth.types.ts
│   │   │   ├── deal.types.ts           # 🆕 Deal types
│   │   │   ├── search.types.ts         # 🆕 Search types
│   │   │   └── listing.types.ts        # 🆕 Listing types
│   │   │
│   │   └── validations/
│   │       ├── auth.schema.ts
│   │       └── search.schema.ts        # 🆕 Search validation
│   │
│   └── stores/
│       ├── auth.store.ts
│       ├── deal.store.ts               # 🆕 Deal state
│       ├── search.store.ts             # 🆕 Search state
│       └── ui.store.ts
```

---

## 🔌 API Integration Layer

### 1. API Client Setup

```typescript
// lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle 401, refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If 401 and haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh token
        const refreshToken = localStorage.getItem('refresh_token');
        const { data } = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`,
          { refresh_token: refreshToken }
        );
        
        // Store new token
        localStorage.setItem('access_token', data.access_token);
        
        // Retry original request
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed - logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

---

### 2. Deal API Endpoints

```typescript
// lib/api/searches.ts
import apiClient from './client';
import type { 
  SearchConfig, 
  CreateSearchRequest, 
  UpdateSearchRequest 
} from '@/lib/types/search.types';

export const searchesApi = {
  // Get all searches for current user
  getSearches: async () => {
    const { data } = await apiClient.get<SearchConfig[]>('/searches/');
    return data;
  },

  // Get single search by ID
  getSearch: async (id: string) => {
    const { data } = await apiClient.get<SearchConfig>(`/searches/${id}`);
    return data;
  },

  // Create new search
  createSearch: async (search: CreateSearchRequest) => {
    const { data } = await apiClient.post<SearchConfig>('/searches/', search);
    return data;
  },

  // Update search
  updateSearch: async (id: string, updates: UpdateSearchRequest) => {
    const { data } = await apiClient.put<SearchConfig>(`/searches/${id}`, updates);
    return data;
  },

  // Delete search
  deleteSearch: async (id: string) => {
    await apiClient.delete(`/searches/${id}`);
  },

  // Pause search
  pauseSearch: async (id: string) => {
    const { data } = await apiClient.post<SearchConfig>(`/searches/${id}/pause`);
    return data;
  },

  // Resume search
  resumeSearch: async (id: string) => {
    const { data } = await apiClient.post<SearchConfig>(`/searches/${id}/resume`);
    return data;
  },
};

// lib/api/listings.ts
import apiClient from './client';
import type { Listing, ListingFilters } from '@/lib/types/listing.types';

export const listingsApi = {
  // Get listings with filters
  getListings: async (filters?: ListingFilters) => {
    const { data } = await apiClient.get<{ items: Listing[]; total: number }>(
      '/listings/',
      { params: filters }
    );
    return data;
  },

  // Get recent listings
  getRecentListings: async (hours: number = 24) => {
    const { data } = await apiClient.get<Listing[]>(`/listings/recent`, {
      params: { hours }
    });
    return data;
  },

  // Get single listing
  getListing: async (id: string) => {
    const { data } = await apiClient.get<Listing>(`/listings/${id}`);
    return data;
  },

  // Update listing (save, hide, etc.)
  updateListing: async (id: string, updates: Partial<Listing>) => {
    const { data } = await apiClient.put<Listing>(`/listings/${id}`, updates);
    return data;
  },

  // Save listing as favorite
  saveListing: async (id: string) => {
    const { data } = await apiClient.put<Listing>(`/listings/${id}`, {
      is_saved: true
    });
    return data;
  },

  // Hide listing
  hideListing: async (id: string) => {
    const { data } = await apiClient.put<Listing>(`/listings/${id}`, {
      is_hidden: true
    });
    return data;
  },
};

// lib/api/templates.ts
import apiClient from './client';
import type { SearchTemplate } from '@/lib/types/template.types';

export const templatesApi = {
  // Get all templates
  getTemplates: async () => {
    const { data } = await apiClient.get<SearchTemplate[]>('/templates/');
    return data;
  },

  // Get single template
  getTemplate: async (id: string) => {
    const { data } = await apiClient.get<SearchTemplate>(`/templates/${id}`);
    return data;
  },
};
```

---

### 3. TypeScript Types

```typescript
// lib/types/search.types.ts
export type Marketplace = 'ebay' | 'facebook' | 'gumtree' | 'craigslist';
export type AlertChannel = 'email' | 'sms' | 'webhook' | 'push';
export type SearchStatus = 'active' | 'paused' | 'disabled';

export interface SearchCriteria {
  keywords?: string[];
  exclude_keywords?: string[];
  max_price?: number;
  min_price?: number;
  location?: string;
  condition?: string;
  category?: string;
}

export interface SearchConfig {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  status: SearchStatus;
  criteria: SearchCriteria;
  marketplaces: Marketplace[];
  facebook_url?: string;
  alert_channels: AlertChannel[];
  check_frequency_minutes: number;
  last_checked_at?: string;
  total_matches_found: number;
  created_at: string;
  updated_at: string;
}

export interface CreateSearchRequest {
  name: string;
  description?: string;
  criteria: SearchCriteria;
  marketplaces: Marketplace[];
  facebook_url?: string;
  alert_channels?: AlertChannel[];
  check_frequency_minutes?: number;
}

export type UpdateSearchRequest = Partial<CreateSearchRequest>;

// lib/types/listing.types.ts
export interface Listing {
  id: string;
  search_config_id: string;
  external_id: string;
  marketplace: Marketplace;
  url: string;
  title: string;
  description?: string;
  price: number;
  currency: string;
  location?: string;
  image_url?: string;
  metadata: Record<string, any>;
  first_seen_at: string;
  last_seen_at: string;
  is_active: boolean;
  is_viewed: boolean;
  is_saved: boolean;
  is_hidden: boolean;
  created_at: string;
  updated_at: string;
}

export interface ListingFilters {
  search_config_id?: string;
  marketplace?: Marketplace;
  is_saved?: boolean;
  is_hidden?: boolean;
  min_price?: number;
  max_price?: number;
  limit?: number;
  offset?: number;
}

// lib/types/template.types.ts
export interface SearchTemplate {
  id: string;
  name: string;
  description?: string;
  category: string;
  config: SearchCriteria;
  usage_count: number;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}
```

---

## 🎨 React Components

### 1. Search Form Component

```typescript
// components/deals/SearchForm.tsx
'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { searchesApi } from '@/lib/api/searches';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'react-hot-toast';

const searchSchema = z.object({
  name: z.string().min(3, 'Name must be at least 3 characters'),
  description: z.string().optional(),
  keywords: z.string().min(1, 'At least one keyword required'),
  excludeKeywords: z.string().optional(),
  maxPrice: z.number().optional(),
  minPrice: z.number().optional(),
  location: z.string().optional(),
  marketplaces: z.array(z.enum(['ebay', 'facebook', 'gumtree', 'craigslist']))
    .min(1, 'Select at least one marketplace'),
  alertChannels: z.array(z.enum(['email', 'sms', 'webhook', 'push'])),
  checkFrequency: z.number().min(5).max(1440),
  facebookUrl: z.string().url().optional().or(z.literal('')),
});

type SearchFormData = z.infer<typeof searchSchema>;

export function SearchForm() {
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm<SearchFormData>({
    resolver: zodResolver(searchSchema),
    defaultValues: {
      marketplaces: ['ebay'],
      alertChannels: ['email'],
      checkFrequency: 30,
    },
  });

  const createMutation = useMutation({
    mutationFn: searchesApi.createSearch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['searches'] });
      toast.success('Search created successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create search');
    },
  });

  const onSubmit = async (data: SearchFormData) => {
    setIsSubmitting(true);
    
    const searchData = {
      name: data.name,
      description: data.description,
      criteria: {
        keywords: data.keywords.split(',').map(k => k.trim()),
        exclude_keywords: data.excludeKeywords 
          ? data.excludeKeywords.split(',').map(k => k.trim())
          : [],
        max_price: data.maxPrice,
        min_price: data.minPrice,
        location: data.location,
      },
      marketplaces: data.marketplaces,
      facebook_url: data.facebookUrl || undefined,
      alert_channels: data.alertChannels,
      check_frequency_minutes: data.checkFrequency,
    };

    await createMutation.mutateAsync(searchData);
    setIsSubmitting(false);
  };

  const selectedMarketplaces = watch('marketplaces');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Basic Info */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Basic Information</h3>
        
        <div>
          <Label htmlFor="name">Search Name *</Label>
          <Input
            id="name"
            {...register('name')}
            placeholder="e.g., iPhone 13 Deals"
          />
          {errors.name && (
            <p className="text-sm text-red-500 mt-1">{errors.name.message}</p>
          )}
        </div>

        <div>
          <Label htmlFor="description">Description</Label>
          <Input
            id="description"
            {...register('description')}
            placeholder="Optional description"
          />
        </div>
      </div>

      {/* Search Criteria */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Search Criteria</h3>
        
        <div>
          <Label htmlFor="keywords">Keywords * (comma-separated)</Label>
          <Input
            id="keywords"
            {...register('keywords')}
            placeholder="iPhone 13, iPhone 14"
          />
          {errors.keywords && (
            <p className="text-sm text-red-500 mt-1">{errors.keywords.message}</p>
          )}
        </div>

        <div>
          <Label htmlFor="excludeKeywords">Exclude Keywords (comma-separated)</Label>
          <Input
            id="excludeKeywords"
            {...register('excludeKeywords')}
            placeholder="broken, faulty, damaged"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="minPrice">Min Price (£)</Label>
            <Input
              id="minPrice"
              type="number"
              {...register('minPrice', { valueAsNumber: true })}
              placeholder="0"
            />
          </div>
          <div>
            <Label htmlFor="maxPrice">Max Price (£)</Label>
            <Input
              id="maxPrice"
              type="number"
              {...register('maxPrice', { valueAsNumber: true })}
              placeholder="500"
            />
          </div>
        </div>

        <div>
          <Label htmlFor="location">Location</Label>
          <Input
            id="location"
            {...register('location')}
            placeholder="London"
          />
        </div>
      </div>

      {/* Marketplaces */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Marketplaces *</h3>
        <div className="space-y-2">
          {['ebay', 'facebook', 'gumtree', 'craigslist'].map((marketplace) => (
            <div key={marketplace} className="flex items-center space-x-2">
              <Checkbox
                id={marketplace}
                checked={selectedMarketplaces.includes(marketplace as any)}
                onCheckedChange={(checked) => {
                  if (checked) {
                    setValue('marketplaces', [...selectedMarketplaces, marketplace as any]);
                  } else {
                    setValue(
                      'marketplaces',
                      selectedMarketplaces.filter(m => m !== marketplace)
                    );
                  }
                }}
              />
              <Label htmlFor={marketplace} className="capitalize cursor-pointer">
                {marketplace}
                {marketplace === 'ebay' && ' (Official API ✅)'}
                {marketplace === 'facebook' && ' (Scraping ⚠️)'}
              </Label>
            </div>
          ))}
        </div>
        {errors.marketplaces && (
          <p className="text-sm text-red-500">{errors.marketplaces.message}</p>
        )}
      </div>

      {/* Facebook URL (if Facebook selected) */}
      {selectedMarketplaces.includes('facebook') && (
        <div>
          <Label htmlFor="facebookUrl">Facebook Marketplace URL (Optional)</Label>
          <Input
            id="facebookUrl"
            {...register('facebookUrl')}
            placeholder="https://facebook.com/marketplace/london/search?query=iphone"
          />
          <p className="text-sm text-muted-foreground mt-1">
            💡 URL monitoring is safer than automated search
          </p>
        </div>
      )}

      {/* Alert Settings */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Alert Settings</h3>
        
        <div>
          <Label>Alert Channels</Label>
          <div className="space-y-2 mt-2">
            {['email', 'sms', 'webhook'].map((channel) => (
              <div key={channel} className="flex items-center space-x-2">
                <Checkbox
                  id={`alert-${channel}`}
                  {...register('alertChannels')}
                  value={channel}
                />
                <Label htmlFor={`alert-${channel}`} className="capitalize cursor-pointer">
                  {channel}
                </Label>
              </div>
            ))}
          </div>
        </div>

        <div>
          <Label htmlFor="checkFrequency">Check Frequency (minutes)</Label>
          <Input
            id="checkFrequency"
            type="number"
            {...register('checkFrequency', { valueAsNumber: true })}
            min="5"
            max="1440"
          />
          <p className="text-sm text-muted-foreground mt-1">
            How often to check for new listings (5-1440 minutes)
          </p>
        </div>
      </div>

      {/* Submit */}
      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? 'Creating...' : 'Create Search'}
      </Button>
    </form>
  );
}
```

---

### 2. Listing Card Component

```typescript
// components/deals/ListingCard.tsx
'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { listingsApi } from '@/lib/api/listings';
import type { Listing } from '@/lib/types/listing.types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Heart, ExternalLink, EyeOff } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { formatDistanceToNow } from 'date-fns';

interface ListingCardProps {
  listing: Listing;
}

export function ListingCard({ listing }: ListingCardProps) {
  const queryClient = useQueryClient();
  const [imageError, setImageError] = useState(false);

  const saveMutation = useMutation({
    mutationFn: () => listingsApi.saveListing(listing.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listings'] });
      toast.success(listing.is_saved ? 'Removed from saved' : 'Saved to favorites');
    },
  });

  const hideMutation = useMutation({
    mutationFn: () => listingsApi.hideListing(listing.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listings'] });
      toast.success('Listing hidden');
    },
  });

  const marketplaceColors = {
    ebay: 'bg-blue-500',
    facebook: 'bg-indigo-500',
    gumtree: 'bg-green-500',
    craigslist: 'bg-purple-500',
  };

  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      {/* Image */}
      <div className="relative h-48 bg-gray-100">
        {listing.image_url && !imageError ? (
          <Image
            src={listing.image_url}
            alt={listing.title}
            fill
            className="object-cover"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            No image available
          </div>
        )}
        
        {/* Marketplace badge */}
        <Badge 
          className={`absolute top-2 left-2 ${marketplaceColors[listing.marketplace]} text-white`}
        >
          {listing.marketplace}
        </Badge>

        {/* New badge */}
        {!listing.is_viewed && (
          <Badge className="absolute top-2 right-2 bg-red-500 text-white">
            NEW
          </Badge>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-lg line-clamp-2 mb-2">
          {listing.title}
        </h3>

        <div className="flex items-center justify-between mb-3">
          <span className="text-2xl font-bold text-primary">
            £{listing.price.toFixed(2)}
          </span>
          {listing.location && (
            <span className="text-sm text-muted-foreground">
              📍 {listing.location}
            </span>
          )}
        </div>

        {listing.description && (
          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
            {listing.description}
          </p>
        )}

        <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
          <span>
            Found {formatDistanceToNow(new Date(listing.first_seen_at))} ago
          </span>
          {!listing.is_active && (
            <Badge variant="secondary">Inactive</Badge>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={() => saveMutation.mutate()}
          >
            <Heart className={`w-4 h-4 mr-1 ${listing.is_saved ? 'fill-current' : ''}`} />
            {listing.is_saved ? 'Saved' : 'Save'}
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={() => hideMutation.mutate()}
          >
            <EyeOff className="w-4 h-4" />
          </Button>

          <Button
            size="sm"
            asChild
          >
            <Link href={listing.url} target="_blank">
              <ExternalLink className="w-4 h-4 mr-1" />
              View
            </Link>
          </Button>
        </div>
      </div>
    </Card>
  );
}
```

---

### 3. Listing Grid Component

```typescript
// components/deals/ListingGrid.tsx
'use client';

import { useQuery } from '@tanstack/react-query';
import { listingsApi } from '@/lib/api/listings';
import { ListingCard } from './ListingCard';
import { Skeleton } from '@/components/ui/skeleton';
import type { ListingFilters } from '@/lib/types/listing.types';

interface ListingGridProps {
  filters?: ListingFilters;
}

export function ListingGrid({ filters }: ListingGridProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['listings', filters],
    queryFn: () => listingsApi.getListings(filters),
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <Skeleton key={i} className="h-80" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">Failed to load listings</p>
      </div>
    );
  }

  if (!data?.items.length) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No listings found</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">
          {data.total} {data.total === 1 ? 'Listing' : 'Listings'} Found
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.items.map((listing) => (
          <ListingCard key={listing.id} listing={listing} />
        ))}
      </div>
    </div>
  );
}
```

---

### 4. Dashboard Page

```typescript
// app/(dashboard)/deals/page.tsx
'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { searchesApi } from '@/lib/api/searches';
import { listingsApi } from '@/lib/api/listings';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ListingGrid } from '@/components/deals/ListingGrid';
import { Plus, Search, Bell, TrendingUp } from 'lucide-react';
import Link from 'next/link';

export default function DealsPage() {
  const [timeFilter, setTimeFilter] = useState(24);

  // Fetch user's searches
  const { data: searches } = useQuery({
    queryKey: ['searches'],
    queryFn: searchesApi.getSearches,
  });

  // Fetch recent listings
  const { data: recentListings } = useQuery({
    queryKey: ['listings', 'recent', timeFilter],
    queryFn: () => listingsApi.getRecentListings(timeFilter),
  });

  const activeSearches = searches?.filter(s => s.status === 'active').length || 0;
  const totalMatches = searches?.reduce((sum, s) => sum + s.total_matches_found, 0) || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Deal Monitor</h1>
          <p className="text-muted-foreground">
            Track deals across eBay, Facebook Marketplace, and more
          </p>
        </div>
        <Button asChild>
          <Link href="/deals/searches/new">
            <Plus className="w-4 h-4 mr-2" />
            New Search
          </Link>
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Searches</CardTitle>
            <Search className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeSearches}</div>
            <p className="text-xs text-muted-foreground">
              {searches?.length || 0} total searches
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Matches</CardTitle>
            <TrendingUp className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalMatches}</div>
            <p className="text-xs text-muted-foreground">
              All time
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">New Today</CardTitle>
            <Bell className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{recentListings?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              Last 24 hours
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Time Filter */}
      <div className="flex gap-2">
        <Button
          variant={timeFilter === 24 ? 'default' : 'outline'}
          size="sm"
          onClick={() => setTimeFilter(24)}
        >
          Last 24h
        </Button>
        <Button
          variant={timeFilter === 72 ? 'default' : 'outline'}
          size="sm"
          onClick={() => setTimeFilter(72)}
        >
          Last 3 days
        </Button>
        <Button
          variant={timeFilter === 168 ? 'default' : 'outline'}
          size="sm"
          onClick={() => setTimeFilter(168)}
        >
          Last week
        </Button>
      </div>

      {/* Recent Listings */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">Recent Finds</h2>
        <ListingGrid />
      </div>
    </div>
  );
}
```

---

## 🔄 React Query Setup

```typescript
// lib/providers/query-provider.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            cacheTime: 5 * 60 * 1000, // 5 minutes
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

---

## 🎯 Custom Hooks

```typescript
// lib/hooks/useSearches.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { searchesApi } from '@/lib/api/searches';
import { toast } from 'react-hot-toast';

export function useSearches() {
  return useQuery({
    queryKey: ['searches'],
    queryFn: searchesApi.getSearches,
  });
}

export function useSearch(id: string) {
  return useQuery({
    queryKey: ['searches', id],
    queryFn: () => searchesApi.getSearch(id),
    enabled: !!id,
  });
}

export function useCreateSearch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: searchesApi.createSearch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['searches'] });
      toast.success('Search created!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create search');
    },
  });
}

export function usePauseSearch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: searchesApi.pauseSearch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['searches'] });
      toast.success('Search paused');
    },
  });
}

// lib/hooks/useListings.ts
import { useQuery } from '@tanstack/react-query';
import { listingsApi } from '@/lib/api/listings';
import type { ListingFilters } from '@/lib/types/listing.types';

export function useListings(filters?: ListingFilters) {
  return useQuery({
    queryKey: ['listings', filters],
    queryFn: () => listingsApi.getListings(filters),
  });
}

export function useRecentListings(hours: number = 24) {
  return useQuery({
    queryKey: ['listings', 'recent', hours],
    queryFn: () => listingsApi.getRecentListings(hours),
  });
}

export function useListing(id: string) {
  return useQuery({
    queryKey: ['listings', id],
    queryFn: () => listingsApi.getListing(id),
    enabled: !!id,
  });
}
```

---

## 🚀 Complete Implementation Steps

### Phase 1: Setup (1 day)
1. ✅ Initialize Next.js project with TypeScript
2. ✅ Install dependencies (Tailwind, shadcn/ui, React Query, etc.)
3. ✅ Setup environment variables
4. ✅ Configure API client
5. ✅ Setup authentication

### Phase 2: Core Deal Features (3-5 days)
1. ✅ Build search creation form
2. ✅ Build search management page
3. ✅ Build listing display components
4. ✅ Build dashboard with stats
5. ✅ Add filters and sorting
6. ✅ Integrate with backend API

### Phase 3: Additional Features (2-3 days)
1. ✅ Add template selector
2. ✅ Add alert configuration UI
3. ✅ Add saved/hidden listings
4. ✅ Add search analytics
5. ✅ Add notifications

### Phase 4: Integration with Other Modules (2-3 days)
1. ✅ Connect deals to CRM contacts
2. ✅ Add deals to sales pipeline
3. ✅ Create campaigns from deals
4. ✅ Add deal tracking to store

### Total: 8-12 days for complete integration

---

## 🎨 UI/UX Recommendations

### Color Scheme for Marketplaces
- **eBay**: Blue (#0064D2)
- **Facebook**: Indigo (#4267B2)
- **Gumtree**: Green (#72EF36)
- **Craigslist**: Purple (#6F1AB6)

### Status Colors
- **Active**: Green
- **Paused**: Yellow
- **New Listing**: Red badge
- **Saved**: Heart icon filled
- **Hidden**: Grayed out

---

## ⚡ Performance Optimizations

1. **Infinite Scroll** for listings
```typescript
import { useInfiniteQuery } from '@tanstack/react-query';
import { useInView } from 'react-intersection-observer';

export function InfiniteListingGrid() {
  const { ref, inView } = useInView();

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['listings'],
    queryFn: ({ pageParam = 0 }) =>
      listingsApi.getListings({ offset: pageParam, limit: 20 }),
    getNextPageParam: (lastPage, pages) => {
      const nextOffset = pages.length * 20;
      return nextOffset < lastPage.total ? nextOffset : undefined;
    },
  });

  useEffect(() => {
    if (inView && hasNextPage) {
      fetchNextPage();
    }
  }, [inView, fetchNextPage, hasNextPage]);

  return (
    <div>
      {data?.pages.map((page) =>
        page.items.map((listing) => (
          <ListingCard key={listing.id} listing={listing} />
        ))
      )}
      <div ref={ref}>{isFetchingNextPage && 'Loading...'}</div>
    </div>
  );
}
```

2. **Image Optimization**
- Use Next.js `<Image>` component
- Lazy load images
- Use placeholders

3. **Data Caching**
- React Query automatic caching
- Stale-while-revalidate strategy
- Optimistic updates

---

## 🎉 You're Ready to Build!

Your **Deal Scout** frontend now has everything it needs to integrate with the **Marketplace Monitor** backend!

### What You Have:
✅ Complete API client with auth  
✅ TypeScript types for all entities  
✅ React components for deals  
✅ Custom hooks with React Query  
✅ Dashboard layouts  
✅ Forms with validation  

### Next Steps:
1. Initialize Next.js project
2. Copy these components and adapt to your design
3. Connect to your backend (http://localhost:8000)
4. Test end-to-end
5. Deploy!

**Happy coding!** 🚀😎
