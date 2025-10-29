'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { useListings } from '@/lib/hooks/useListings';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { formatCurrency, formatRelativeTime, getMarketplaceName, getMarketplaceColor } from '@/lib/utils';
import { Star, ExternalLink, Archive } from 'lucide-react';
import type { Listing } from '@/lib/types';

export default function ListingsPage() {
  const { listings, loading, toggleSave, toggleArchive } = useListings();
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  const handleToggleSave = async (listing: Listing) => {
    setActionLoading(listing.id);
    try {
      await toggleSave(listing.id, !listing.is_saved);
    } finally {
      setActionLoading(null);
    }
  };

  const handleToggleArchive = async (listing: Listing) => {
    setActionLoading(listing.id);
    try {
      await toggleArchive(listing.id, !listing.is_archived);
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex h-full items-center justify-center">
          <Spinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Listings</h1>
          <p className="text-muted-foreground">
            Browse and manage your marketplace listings
          </p>
        </div>

        {listings.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <p className="text-muted-foreground">No listings found</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {listings.map((listing) => (
              <Card key={listing.id} className="flex flex-col">
                {listing.image_url && (
                  <div className="relative h-48 w-full overflow-hidden rounded-t-lg bg-gray-100">
                    <img
                      src={listing.image_url}
                      alt={listing.title}
                      className="h-full w-full object-cover"
                    />
                    <div className="absolute right-2 top-2">
                      <Badge className={getMarketplaceColor(listing.marketplace)}>
                        {getMarketplaceName(listing.marketplace)}
                      </Badge>
                    </div>
                  </div>
                )}

                <CardContent className="flex flex-1 flex-col p-4">
                  <div className="mb-2 flex items-start justify-between">
                    <h3 className="line-clamp-2 text-lg font-semibold">{listing.title}</h3>
                  </div>

                  {listing.description && (
                    <p className="mb-3 line-clamp-2 text-sm text-muted-foreground">
                      {listing.description}
                    </p>
                  )}

                  <div className="mb-3 flex items-baseline gap-2">
                    <span className="text-2xl font-bold">
                      {formatCurrency(listing.price, listing.currency)}
                    </span>
                  </div>

                  {listing.location && (
                    <p className="mb-2 text-sm text-muted-foreground">
                      {listing.location}
                    </p>
                  )}

                  <p className="mb-4 text-xs text-muted-foreground">
                    Posted {formatRelativeTime(listing.posted_at || listing.scraped_at)}
                  </p>

                  <div className="mt-auto flex gap-2">
                    <Button
                      size="sm"
                      variant={listing.is_saved ? 'default' : 'outline'}
                      onClick={() => handleToggleSave(listing)}
                      disabled={actionLoading === listing.id}
                      className="flex-1"
                    >
                      <Star
                        className={`mr-1 h-4 w-4 ${
                          listing.is_saved ? 'fill-current' : ''
                        }`}
                      />
                      {listing.is_saved ? 'Saved' : 'Save'}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleToggleArchive(listing)}
                      disabled={actionLoading === listing.id}
                    >
                      <Archive className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      asChild
                    >
                      <a
                        href={listing.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </Button>
                  </div>

                  {listing.is_archived && (
                    <Badge variant="secondary" className="mt-2">
                      Archived
                    </Badge>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
