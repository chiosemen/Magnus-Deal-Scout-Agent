import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow } from "date-fns";

/**
 * Merge Tailwind CSS classes with clsx
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format currency
 */
export function formatCurrency(amount: number, currency: string = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(amount);
}

/**
 * Format date
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return format(d, "MMM d, yyyy");
}

/**
 * Format relative time
 */
export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return formatDistanceToNow(d, { addSuffix: true });
}

/**
 * Truncate text
 */
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length) + "...";
}

/**
 * Get marketplace display name
 */
export function getMarketplaceName(marketplace: string): string {
  const names: Record<string, string> = {
    ebay: "eBay",
    facebook: "Facebook Marketplace",
    gumtree: "Gumtree",
    craigslist: "Craigslist",
  };
  return names[marketplace] || marketplace;
}

/**
 * Get marketplace color
 */
export function getMarketplaceColor(marketplace: string): string {
  const colors: Record<string, string> = {
    ebay: "bg-yellow-500",
    facebook: "bg-blue-500",
    gumtree: "bg-green-500",
    craigslist: "bg-purple-500",
  };
  return colors[marketplace] || "bg-gray-500";
}
