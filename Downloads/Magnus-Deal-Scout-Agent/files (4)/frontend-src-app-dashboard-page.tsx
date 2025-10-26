// src/app/(dashboard)/dashboard/page.tsx

"use client";

import { useDashboardStats } from "@/lib/hooks/useDashboard";
import { useRecentListings } from "@/lib/hooks/useListings";
import { useSearches } from "@/lib/hooks/useSearches";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/combined-1";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/combined-2";
import { formatPrice, formatRelativeTime, getMarketplaceColor, getMarketplaceName } from "@/lib/utils";
import Link from "next/link";
import { Plus, TrendingUp, Search as SearchIcon, List, Bookmark } from "lucide-react";

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: recentListings, isLoading: listingsLoading } = useRecentListings(5);
  const { data: searchesData, isLoading: searchesLoading } = useSearches({ per_page: 5 });

  const statsCards = [
    {
      title: "Total Searches",
      value: stats?.total_searches || 0,
      icon: SearchIcon,
      description: `${stats?.active_searches || 0} active`,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      title: "Total Listings",
      value: stats?.total_listings || 0,
      icon: List,
      description: `${stats?.new_listings_today || 0} new today`,
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      title: "Saved Listings",
      value: stats?.saved_listings || 0,
      icon: Bookmark,
      description: "Bookmarked deals",
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      title: "New Today",
      value: stats?.new_listings_today || 0,
      icon: TrendingUp,
      description: "Fresh opportunities",
      color: "text-orange-600",
      bgColor: "bg-orange-50",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Welcome back! Here's what's happening.</p>
        </div>
        <Link href="/searches/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Search
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsLoading
          ? Array.from({ length: 4 }).map((_, i) => (
              <Card key={i}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-4" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-8 w-16" />
                  <Skeleton className="mt-1 h-3 w-32" />
                </CardContent>
              </Card>
            ))
          : statsCards.map((stat) => (
              <Card key={stat.title}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                  <div className={`rounded-lg p-2 ${stat.bgColor}`}>
                    <stat.icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">{stat.description}</p>
                </CardContent>
              </Card>
            ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Searches */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Searches</CardTitle>
            <CardDescription>Your active search queries</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {searchesLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              ))
            ) : searchesData?.items.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">
                No searches yet. Create your first search to get started!
              </div>
            ) : (
              searchesData?.items.map((search) => (
                <Link
                  key={search.id}
                  href={`/searches/${search.id}`}
                  className="block rounded-lg border p-4 transition-colors hover:bg-accent"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium">{search.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        {search.keywords} • {search.marketplaces.length} marketplace(s)
                      </p>
                    </div>
                    <div className="text-right text-sm">
                      <div className="font-medium">{search._count?.listings || 0}</div>
                      <div className="text-muted-foreground">listings</div>
                    </div>
                  </div>
                </Link>
              ))
            )}
            {!searchesLoading && (searchesData?.items.length || 0) > 0 && (
              <Link href="/searches">
                <Button variant="outline" className="w-full">
                  View All Searches
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>

        {/* Recent Listings */}
        <Card>
          <CardHeader>
            <CardTitle>Latest Listings</CardTitle>
            <CardDescription>Newest deals found</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {listingsLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="flex gap-3">
                  <Skeleton className="h-16 w-16 rounded" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                </div>
              ))
            ) : recentListings?.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">
                No listings yet. Your searches will populate this section.
              </div>
            ) : (
              recentListings?.map((listing) => (
                <Link
                  key={listing.id}
                  href={`/listings/${listing.id}`}
                  className="flex gap-3 rounded-lg border p-3 transition-colors hover:bg-accent"
                >
                  {listing.image_urls[0] && (
                    <img
                      src={listing.image_urls[0]}
                      alt={listing.title}
                      className="h-16 w-16 rounded object-cover"
                    />
                  )}
                  <div className="flex-1 overflow-hidden">
                    <h3 className="truncate font-medium">{listing.title}</h3>
                    <div className="mt-1 flex items-center gap-2">
                      <span className="font-semibold text-primary">
                        {formatPrice(listing.price, listing.currency)}
                      </span>
                      <span
                        className={`rounded px-2 py-0.5 text-xs font-medium text-white ${getMarketplaceColor(
                          listing.marketplace
                        )}`}
                      >
                        {getMarketplaceName(listing.marketplace)}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {formatRelativeTime(listing.posted_at || listing.created_at)}
                    </p>
                  </div>
                </Link>
              ))
            )}
            {!listingsLoading && (recentListings?.length || 0) > 0 && (
              <Link href="/listings">
                <Button variant="outline" className="w-full">
                  View All Listings
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
