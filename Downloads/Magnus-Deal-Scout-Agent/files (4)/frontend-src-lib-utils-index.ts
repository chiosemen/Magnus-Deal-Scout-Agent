// src/lib/utils/index.ts

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow, parseISO } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPrice(price: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(price);
}

export function formatDate(date: string | Date, formatStr: string = 'MMM d, yyyy'): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, formatStr);
}

export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return formatDistanceToNow(dateObj, { addSuffix: true });
}

export function truncateText(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
}

export function getMarketplaceColor(marketplace: string): string {
  const colors: Record<string, string> = {
    ebay: 'bg-yellow-500',
    facebook: 'bg-blue-500',
    gumtree: 'bg-green-500',
    craigslist: 'bg-purple-500',
  };
  return colors[marketplace] || 'bg-gray-500';
}

export function getMarketplaceName(marketplace: string): string {
  const names: Record<string, string> = {
    ebay: 'eBay',
    facebook: 'Facebook Marketplace',
    gumtree: 'Gumtree',
    craigslist: 'Craigslist',
  };
  return names[marketplace] || marketplace;
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .substring(0, 2);
}

export function buildQueryString(params: Record<string, any>): string {
  const filtered = Object.entries(params).filter(([_, value]) => value !== undefined && value !== null && value !== '');
  
  if (filtered.length === 0) return '';
  
  const searchParams = new URLSearchParams();
  filtered.forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach(v => searchParams.append(key, String(v)));
    } else {
      searchParams.append(key, String(value));
    }
  });
  
  return searchParams.toString();
}

export function generateRandomId(): string {
  return Math.random().toString(36).substring(2, 9);
}

export function validateEmail(email: string): boolean {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

export function extractErrorMessage(error: any): string {
  if (typeof error === 'string') return error;
  if (error?.response?.data?.detail) return error.response.data.detail;
  if (error?.message) return error.message;
  return 'An unexpected error occurred';
}
