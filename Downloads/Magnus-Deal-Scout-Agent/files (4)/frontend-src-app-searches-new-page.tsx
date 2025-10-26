// src/app/(dashboard)/searches/new/page.tsx

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useCreateSearch } from "@/lib/hooks/useSearches";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Input, Label } from "@/components/ui/combined-1";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/combined-2";
import { Marketplace, SearchFormData } from "@/lib/types";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

const MARKETPLACES: { value: Marketplace; label: string }[] = [
  { value: "ebay", label: "eBay" },
  { value: "facebook", label: "Facebook Marketplace" },
  { value: "gumtree", label: "Gumtree" },
  { value: "craigslist", label: "Craigslist" },
];

export default function NewSearchPage() {
  const router = useRouter();
  const createSearch = useCreateSearch();

  const [formData, setFormData] = useState<SearchFormData>({
    name: "",
    keywords: "",
    marketplaces: [],
    location: "",
    radius_km: 50,
    min_price: undefined,
    max_price: undefined,
    check_interval_minutes: 60,
  });

  const [selectedMarketplaces, setSelectedMarketplaces] = useState<Set<Marketplace>>(new Set());

  const toggleMarketplace = (marketplace: Marketplace) => {
    const newSet = new Set(selectedMarketplaces);
    if (newSet.has(marketplace)) {
      newSet.delete(marketplace);
    } else {
      newSet.add(marketplace);
    }
    setSelectedMarketplaces(newSet);
    setFormData({ ...formData, marketplaces: Array.from(newSet) });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.marketplaces.length === 0) {
      alert("Please select at least one marketplace");
      return;
    }
    createSearch.mutate(formData);
  };

  const handleChange = (field: keyof SearchFormData, value: any) => {
    setFormData({ ...formData, [field]: value });
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Header */}
      <div>
        <Link href="/searches">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Searches
          </Button>
        </Link>
        <h1 className="text-3xl font-bold tracking-tight">Create New Search</h1>
        <p className="text-muted-foreground">
          Set up a new search query to monitor across marketplaces
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>Define what you're looking for</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Search Name*</Label>
              <Input
                id="name"
                placeholder="e.g., Vintage Cameras"
                value={formData.name}
                onChange={(e) => handleChange("name", e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="keywords">Keywords*</Label>
              <Input
                id="keywords"
                placeholder="e.g., canon ae-1, nikon f3, film camera"
                value={formData.keywords}
                onChange={(e) => handleChange("keywords", e.target.value)}
                required
              />
              <p className="text-xs text-muted-foreground">
                Comma-separated keywords to search for
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Marketplaces</CardTitle>
            <CardDescription>Select where to search</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {MARKETPLACES.map((marketplace) => (
                <button
                  key={marketplace.value}
                  type="button"
                  onClick={() => toggleMarketplace(marketplace.value)}
                  className={`rounded-lg border-2 p-4 text-left transition-all ${
                    selectedMarketplaces.has(marketplace.value)
                      ? "border-primary bg-primary/5"
                      : "border-border hover:border-primary/50"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <div
                      className={`h-4 w-4 rounded border-2 ${
                        selectedMarketplaces.has(marketplace.value)
                          ? "border-primary bg-primary"
                          : "border-border"
                      }`}
                    />
                    <span className="font-medium">{marketplace.label}</span>
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Location & Price</CardTitle>
            <CardDescription>Optional filters to narrow results</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  placeholder="e.g., London, UK"
                  value={formData.location}
                  onChange={(e) => handleChange("location", e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="radius">Radius (km)</Label>
                <Input
                  id="radius"
                  type="number"
                  min="1"
                  max="500"
                  value={formData.radius_km}
                  onChange={(e) => handleChange("radius_km", parseInt(e.target.value))}
                />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="minPrice">Min Price</Label>
                <Input
                  id="minPrice"
                  type="number"
                  min="0"
                  placeholder="0"
                  value={formData.min_price || ""}
                  onChange={(e) => handleChange("min_price", e.target.value ? parseFloat(e.target.value) : undefined)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="maxPrice">Max Price</Label>
                <Input
                  id="maxPrice"
                  type="number"
                  min="0"
                  placeholder="No limit"
                  value={formData.max_price || ""}
                  onChange={(e) => handleChange("max_price", e.target.value ? parseFloat(e.target.value) : undefined)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Search Frequency</CardTitle>
            <CardDescription>How often should we check for new listings?</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Label htmlFor="interval">Check Interval</Label>
              <Select
                value={formData.check_interval_minutes.toString()}
                onValueChange={(value) => handleChange("check_interval_minutes", parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="15">Every 15 minutes</SelectItem>
                  <SelectItem value="30">Every 30 minutes</SelectItem>
                  <SelectItem value="60">Every hour</SelectItem>
                  <SelectItem value="120">Every 2 hours</SelectItem>
                  <SelectItem value="360">Every 6 hours</SelectItem>
                  <SelectItem value="720">Every 12 hours</SelectItem>
                  <SelectItem value="1440">Once daily</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3">
          <Link href="/searches">
            <Button type="button" variant="outline">
              Cancel
            </Button>
          </Link>
          <Button type="submit" disabled={createSearch.isPending}>
            {createSearch.isPending ? "Creating..." : "Create Search"}
          </Button>
        </div>
      </form>
    </div>
  );
}
