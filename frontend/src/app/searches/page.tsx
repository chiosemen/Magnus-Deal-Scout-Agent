'use client';

import { useState } from 'react';
import Link from 'next/link';
import { DashboardLayout } from '@/components/DashboardLayout';
import { useSearches } from '@/lib/hooks/useSearches';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { formatRelativeTime, getMarketplaceName } from '@/lib/utils';
import { Plus, Play, Pause, Trash2 } from 'lucide-react';
import type { Search, SearchStatus } from '@/lib/types';

export default function SearchesPage() {
  const { searches, loading, updateSearch, deleteSearch, triggerSearch } = useSearches();
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  const handleToggleStatus = async (search: Search) => {
    setActionLoading(search.id);
    try {
      const newStatus: SearchStatus =
        search.status === 'active' ? 'paused' : 'active';
      await updateSearch(search.id, { status: newStatus });
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this search?')) return;
    setActionLoading(id);
    try {
      await deleteSearch(id);
    } finally {
      setActionLoading(null);
    }
  };

  const handleTrigger = async (id: number) => {
    setActionLoading(id);
    try {
      await triggerSearch(id);
      alert('Search triggered successfully!');
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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Searches</h1>
            <p className="text-muted-foreground">Manage your marketplace searches</p>
          </div>
          <Link href="/searches/new">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Search
            </Button>
          </Link>
        </div>

        {searches.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <p className="mb-4 text-muted-foreground">No searches yet</p>
              <Link href="/searches/new">
                <Button>Create Your First Search</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {searches.map((search) => (
              <Card key={search.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-lg">{search.name}</CardTitle>
                      <CardDescription className="text-xs">
                        {search.keywords}
                      </CardDescription>
                    </div>
                    <Badge
                      variant={search.status === 'active' ? 'default' : 'secondary'}
                    >
                      {search.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="text-xs text-muted-foreground">Marketplaces:</div>
                    <div className="flex flex-wrap gap-1">
                      {search.marketplaces.map((marketplace) => (
                        <Badge key={marketplace} variant="outline">
                          {getMarketplaceName(marketplace)}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {search.last_run_at && (
                    <div className="text-xs text-muted-foreground">
                      Last run: {formatRelativeTime(search.last_run_at)}
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleToggleStatus(search)}
                      disabled={actionLoading === search.id}
                    >
                      {search.status === 'active' ? (
                        <>
                          <Pause className="mr-1 h-3 w-3" />
                          Pause
                        </>
                      ) : (
                        <>
                          <Play className="mr-1 h-3 w-3" />
                          Resume
                        </>
                      )}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTrigger(search.id)}
                      disabled={actionLoading === search.id}
                    >
                      Run Now
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDelete(search.id)}
                      disabled={actionLoading === search.id}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
