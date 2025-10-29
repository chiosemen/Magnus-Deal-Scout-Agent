'use client';

import { DashboardLayout } from '@/components/DashboardLayout';
import { useDashboard } from '@/lib/hooks/useDashboard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Spinner } from '@/components/ui/Spinner';
import { formatCurrency, getMarketplaceName } from '@/lib/utils';
import { TrendingUp, Search, List, Star, DollarSign } from 'lucide-react';

export default function DashboardPage() {
  const { stats, loading } = useDashboard();

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex h-full items-center justify-center">
          <Spinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  if (!stats) {
    return (
      <DashboardLayout>
        <div className="text-center text-muted-foreground">No data available</div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Overview of your marketplace searches</p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Searches</CardTitle>
              <Search className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_searches}</div>
              <p className="text-xs text-muted-foreground">
                {stats.active_searches} active
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Listings</CardTitle>
              <List className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_listings}</div>
              <p className="text-xs text-muted-foreground">
                Across all marketplaces
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">New (24h)</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.new_listings_24h}</div>
              <p className="text-xs text-muted-foreground">
                New listings today
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Saved Listings</CardTitle>
              <Star className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.saved_listings}</div>
              <p className="text-xs text-muted-foreground">
                Items you&apos;ve saved
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Average Price & Marketplaces */}
        <div className="grid gap-4 md:grid-cols-2">
          {stats.avg_price && (
            <Card>
              <CardHeader>
                <CardTitle>Average Price</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2">
                  <DollarSign className="h-8 w-8 text-muted-foreground" />
                  <div className="text-3xl font-bold">
                    {formatCurrency(stats.avg_price)}
                  </div>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">
                  Across all listings
                </p>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Listings by Marketplace</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(stats.marketplaces).map(([marketplace, count]) => (
                  <div key={marketplace} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="text-sm font-medium">
                        {getMarketplaceName(marketplace)}
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">{count} listings</div>
                  </div>
                ))}
                {Object.keys(stats.marketplaces).length === 0 && (
                  <p className="text-sm text-muted-foreground">No listings yet</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
