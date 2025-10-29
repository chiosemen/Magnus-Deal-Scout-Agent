'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/DashboardLayout';
import { useSearches } from '@/lib/hooks/useSearches';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';

const MARKETPLACES = [
  { id: 'ebay', name: 'eBay' },
  { id: 'facebook', name: 'Facebook Marketplace' },
  { id: 'gumtree', name: 'Gumtree' },
  { id: 'craigslist', name: 'Craigslist' },
];

export default function NewSearchPage() {
  const router = useRouter();
  const { createSearch } = useSearches();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    keywords: '',
    marketplaces: [] as string[],
    minPrice: '',
    maxPrice: '',
    location: '',
    radiusKm: '',
  });

  const handleMarketplaceToggle = (marketplaceId: string) => {
    setFormData((prev) => ({
      ...prev,
      marketplaces: prev.marketplaces.includes(marketplaceId)
        ? prev.marketplaces.filter((m) => m !== marketplaceId)
        : [...prev.marketplaces, marketplaceId],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.marketplaces.length === 0) {
      setError('Please select at least one marketplace');
      return;
    }

    setLoading(true);
    try {
      await createSearch({
        name: formData.name,
        keywords: formData.keywords,
        marketplaces: formData.marketplaces,
        min_price: formData.minPrice ? parseFloat(formData.minPrice) : undefined,
        max_price: formData.maxPrice ? parseFloat(formData.maxPrice) : undefined,
        location: formData.location || undefined,
        radius_km: formData.radiusKm ? parseFloat(formData.radiusKm) : undefined,
      });
      router.push('/searches');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create search');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Create New Search</h1>
          <p className="text-muted-foreground">Set up a new marketplace search</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Search Details</CardTitle>
            <CardDescription>Configure your search parameters</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                  {error}
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="name">Search Name</Label>
                <Input
                  id="name"
                  placeholder="e.g., Vintage Cameras"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="keywords">Keywords</Label>
                <Input
                  id="keywords"
                  placeholder="e.g., canon ae-1, nikon f3"
                  value={formData.keywords}
                  onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Separate multiple keywords with commas
                </p>
              </div>

              <div className="space-y-2">
                <Label>Marketplaces</Label>
                <div className="grid grid-cols-2 gap-2">
                  {MARKETPLACES.map((marketplace) => (
                    <label
                      key={marketplace.id}
                      className="flex cursor-pointer items-center space-x-2 rounded-md border p-3 hover:bg-accent"
                    >
                      <input
                        type="checkbox"
                        checked={formData.marketplaces.includes(marketplace.id)}
                        onChange={() => handleMarketplaceToggle(marketplace.id)}
                        className="h-4 w-4"
                      />
                      <span className="text-sm">{marketplace.name}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="minPrice">Min Price ($)</Label>
                  <Input
                    id="minPrice"
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    value={formData.minPrice}
                    onChange={(e) => setFormData({ ...formData, minPrice: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maxPrice">Max Price ($)</Label>
                  <Input
                    id="maxPrice"
                    type="number"
                    step="0.01"
                    placeholder="1000.00"
                    value={formData.maxPrice}
                    onChange={(e) => setFormData({ ...formData, maxPrice: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    placeholder="e.g., San Francisco, CA"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="radiusKm">Radius (km)</Label>
                  <Input
                    id="radiusKm"
                    type="number"
                    placeholder="50"
                    value={formData.radiusKm}
                    onChange={(e) => setFormData({ ...formData, radiusKm: e.target.value })}
                  />
                </div>
              </div>

              <div className="flex gap-4">
                <Button type="submit" disabled={loading}>
                  {loading ? 'Creating...' : 'Create Search'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.back()}
                  disabled={loading}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
