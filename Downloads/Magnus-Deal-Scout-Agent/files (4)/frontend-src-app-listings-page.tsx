// src/app/(dashboard)/listings/page.tsx

"use client";

import { useState } from "react";
import Link from "next/link";
import { useListings, useSaveListing, useUnsaveListing } from "@/lib/hooks/useListings";
import { Card, CardContent } from "@/components/ui/combined-1";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/combined-2";
import { Skeleton } from "@/components/ui/combined-2";
import { Bookmark, BookmarkCheck, ExternalLink, MapPin } from "lucide-react";
import { formatPrice, formatRelativeTime, getMarketplaceColor, getMarketplaceName, truncateText } from "@/lib/utils";
import { ListingFilters } from "@/lib/types";

export default function ListingsPage() {
  const [filters, setFilters] = useState<ListingFilters>({ page: 1, per_page: 20, sort_by: "newest" });
  const { data, isLoading } = useListings(filters);
  const saveListing = useSaveListing();
  const unsaveListing = useUnsaveListing();

  const handleSave = (id: number, isSaved: boolean) => {
    if (isSaved) {
      unsaveListing.mutate(id);
    } else {
      saveListing.mutate(id);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">All Listings</h1>
        <p className="text-muted-foreground">Browse all discovered listings from your searches</p>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        <Button
          variant={filters.sort_by === "newest" ? "default" : "outline"}
          size="sm"
          onClick={() => setFilters({ ...filters, sort_by: "newest" })}
        >
          Newest
        </Button>
        <Button
          variant={filters.sort_by === "price_asc" ? "default" : "outline"}
          size="sm"
          onClick={() => setFilters({ ...filters, sort_by: "price_asc" })}
        >
          Price: Low to High
        </Button>
        <Button
          variant={filters.sort_by === "price_desc" ? "default" : "outline"}
          size="sm"
          onClick={() => setFilters({ ...filters, sort_by: "price_desc" })}
        >
          Price: High to Low
        </Button>
      </div>

      {/* Listings Grid */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 9 }).map((_, i) => (
            <Card key={i}>
              <Skeleton className="h-48 w-full rounded-t-lg" />
              <CardContent className="p-4">
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="mt-2 h-4 w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : data?.items.length === 0 ? (
        <Card>
          <CardContent className="flex min-h-[400px] items-center justify-center py-16 text-center">
            <div>
              <h3 className="mb-2 text-lg font-semibold">No listings found</h3>
              <p className="text-sm text-muted-foreground">
                Your searches haven't found any listings yet
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data?.items.map((listing) => (
            <Card key={listing.id} className="flex flex-col overflow-hidden">
              <Link href={`/listings/${listing.id}`}>
                {listing.image_urls[0] ? (
                  <img
                    src={listing.image_urls[0]}
                    alt={listing.title}
                    className="h-48 w-full object-cover transition-transform hover:scale-105"
                  />
                ) : (
                  <div className="flex h-48 items-center justify-center bg-muted">
                    <span className="text-muted-foreground">No image</span>
                  </div>
                )}
              </Link>
              <CardContent className="flex flex-1 flex-col p-4">
                <div className="mb-2 flex items-start justify-between gap-2">
                  <Link href={`/listings/${listing.id}`} className="flex-1">
                    <h3 className="line-clamp-2 font-semibold hover:text-primary">
                      {listing.title}
                    </h3>
                  </Link>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleSave(listing.id, listing.is_saved)}
                    className="shrink-0"
                  >
                    {listing.is_saved ? (
                      <BookmarkCheck className="h-5 w-5 fill-primary text-primary" />
                    ) : (
                      <Bookmark className="h-5 w-5" />
                    )}
                  </Button>
                </div>

                <div className="mb-2">
                  <span className="text-2xl font-bold text-primary">
                    {formatPrice(listing.price, listing.currency)}
                  </span>
                </div>

                <div className="mb-3 flex flex-wrap gap-2">
                  <Badge
                    className={`${getMarketplaceColor(listing.marketplace)} text-white`}
                  >
                    {getMarketplaceName(listing.marketplace)}
                  </Badge>
                  {listing.is_featured && (
                    <Badge variant="secondary">Featured</Badge>
                  )}
                </div>

                {listing.location && (
                  <div className="mb-2 flex items-center gap-1 text-sm text-muted-foreground">
                    <MapPin className="h-3 w-3" />
                    {listing.location}
                  </div>
                )}

                <div className="mt-auto flex items-center justify-between pt-3 text-xs text-muted-foreground">
                  <span>{formatRelativeTime(listing.posted_at || listing.created_at)}</span>
                  <a
                    href={listing.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 hover:text-primary"
                  >
                    View <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <div className="flex justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={filters.page === 1}
            onClick={() => setFilters({ ...filters, page: filters.page! - 1 })}
          >
            Previous
          </Button>
          <span className="flex items-center px-4 text-sm">
            Page {data.page} of {data.total_pages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={filters.page === data.total_pages}
            onClick={() => setFilters({ ...filters, page: filters.page! + 1 })}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
