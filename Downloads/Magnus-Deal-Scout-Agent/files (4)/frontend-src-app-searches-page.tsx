// src/app/(dashboard)/searches/page.tsx

"use client";

import { useState } from "react";
import Link from "next/link";
import { useSearches, usePauseSearch, useResumeSearch, useDeleteSearch } from "@/lib/hooks/useSearches";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/combined-1";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/combined-2";
import { Skeleton } from "@/components/ui/combined-2";
import { Plus, Play, Pause, Trash2, Eye, Edit, MoreVertical } from "lucide-react";
import { formatRelativeTime, getMarketplaceName } from "@/lib/utils";
import { Search } from "@/lib/types";

export default function SearchesPage() {
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const { data, isLoading } = useSearches({ status: statusFilter });
  const pauseSearch = usePauseSearch();
  const resumeSearch = useResumeSearch();
  const deleteSearch = useDeleteSearch();

  const handlePause = (id: number) => {
    if (confirm("Are you sure you want to pause this search?")) {
      pauseSearch.mutate(id);
    }
  };

  const handleResume = (id: number) => {
    resumeSearch.mutate(id);
  };

  const handleDelete = (id: number) => {
    if (confirm("Are you sure you want to delete this search? This action cannot be undone.")) {
      deleteSearch.mutate(id);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Searches</h1>
          <p className="text-muted-foreground">Manage your marketplace search queries</p>
        </div>
        <Link href="/searches/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Search
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        <Button
          variant={statusFilter === undefined ? "default" : "outline"}
          size="sm"
          onClick={() => setStatusFilter(undefined)}
        >
          All
        </Button>
        <Button
          variant={statusFilter === "active" ? "default" : "outline"}
          size="sm"
          onClick={() => setStatusFilter("active")}
        >
          Active
        </Button>
        <Button
          variant={statusFilter === "paused" ? "default" : "outline"}
          size="sm"
          onClick={() => setStatusFilter("paused")}
        >
          Paused
        </Button>
      </div>

      {/* Searches Grid */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-full" />
                <Skeleton className="mt-2 h-4 w-2/3" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : data?.items.length === 0 ? (
        <Card>
          <CardContent className="flex min-h-[400px] flex-col items-center justify-center py-16 text-center">
            <div className="mb-4 rounded-full bg-muted p-6">
              <Plus className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="mb-2 text-lg font-semibold">No searches found</h3>
            <p className="mb-6 text-sm text-muted-foreground">
              Get started by creating your first search query
            </p>
            <Link href="/searches/new">
              <Button>Create Your First Search</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data?.items.map((search: Search) => (
            <Card key={search.id} className="flex flex-col">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="line-clamp-1">{search.name}</CardTitle>
                    <CardDescription className="mt-1 line-clamp-1">
                      {search.keywords}
                    </CardDescription>
                  </div>
                  <Badge
                    variant={search.status === "active" ? "default" : "secondary"}
                    className="ml-2"
                  >
                    {search.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="flex-1">
                <div className="space-y-2 text-sm">
                  <div className="flex flex-wrap gap-1">
                    {search.marketplaces.map((marketplace) => (
                      <Badge key={marketplace} variant="outline" className="text-xs">
                        {getMarketplaceName(marketplace)}
                      </Badge>
                    ))}
                  </div>
                  <div className="text-muted-foreground">
                    {search._count?.listings || 0} listings found
                  </div>
                  {search.last_checked_at && (
                    <div className="text-xs text-muted-foreground">
                      Last checked {formatRelativeTime(search.last_checked_at)}
                    </div>
                  )}
                </div>
                <div className="mt-4 flex gap-2">
                  <Link href={`/searches/${search.id}`} className="flex-1">
                    <Button variant="outline" size="sm" className="w-full">
                      <Eye className="mr-2 h-4 w-4" />
                      View
                    </Button>
                  </Link>
                  {search.status === "active" ? (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePause(search.id)}
                      disabled={pauseSearch.isPending}
                    >
                      <Pause className="h-4 w-4" />
                    </Button>
                  ) : (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleResume(search.id)}
                      disabled={resumeSearch.isPending}
                    >
                      <Play className="h-4 w-4" />
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(search.id)}
                    disabled={deleteSearch.isPending}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <div className="flex justify-center gap-2">
          <Button variant="outline" size="sm" disabled={data.page === 1}>
            Previous
          </Button>
          <span className="flex items-center px-4 text-sm">
            Page {data.page} of {data.total_pages}
          </span>
          <Button variant="outline" size="sm" disabled={data.page === data.total_pages}>
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
