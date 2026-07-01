import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getPlaylists } from '@/features/playlist/services/playlist-service';
import { PageHeader } from '@/common/components/page-header';
import { EmptyState } from '@/common/components/empty-state';
import { Card, CardContent } from '@/common/components/ui/card';
import { Button } from '@/common/components/ui/button';
import { ListVideo, Upload, AlertCircle } from 'lucide-react';

export function PlaylistsPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['playlists'],
    queryFn: getPlaylists,
  });

  const playlists = data?.data?.items ?? [];

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Playlists" description="Your learning playlists" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i}>
              <CardContent className="p-0">
                <div className="aspect-video animate-pulse bg-muted" />
                <div className="space-y-2 p-4">
                  <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
                  <div className="h-3 w-1/2 animate-pulse rounded bg-muted" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div>
        <PageHeader title="Playlists" description="Your learning playlists" />
        <div className="flex flex-col items-center justify-center py-12">
          <AlertCircle className="mb-2 size-8 text-destructive" />
          <p className="text-sm text-muted-foreground">Failed to load playlists</p>
          <Button variant="outline" size="sm" className="mt-4" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (playlists.length === 0) {
    return (
      <div>
        <PageHeader
          title="Playlists"
          description="Your learning playlists"
          actions={
            <Link to="/dashboard/import">
              <Button size="sm">
                <Upload className="mr-1 size-4" />
                Import Playlist
              </Button>
            </Link>
          }
        />
        <EmptyState
          icon={<ListVideo className="size-12" />}
          title="No playlists yet"
          description="Import a YouTube playlist to get started with your learning journey."
          action={
            <Link to="/dashboard/import">
              <Button>
                <Upload className="mr-2 size-4" />
                Import Your First Playlist
              </Button>
            </Link>
          }
        />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Playlists"
        description={`${playlists.length} playlist${playlists.length !== 1 ? 's' : ''}`}
        actions={
          <Link to="/dashboard/import">
            <Button size="sm">
              <Upload className="mr-1 size-4" />
              Import
            </Button>
          </Link>
        }
      />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {playlists.map((playlist) => (
          <Link key={playlist.id} to={`/dashboard/playlists/${playlist.id}`}>
            <Card className="transition-shadow hover:shadow-md">
              <CardContent className="p-0">
                <div className="flex aspect-video items-center justify-center bg-muted">
                  {playlist.thumbnail_url ? (
                    <img
                      src={playlist.thumbnail_url}
                      alt={playlist.title}
                      className="h-full w-full object-cover"
                      loading="lazy"
                    />
                  ) : (
                    <ListVideo className="size-8 text-muted-foreground" />
                  )}
                </div>
                <div className="p-4">
                  <h3 className="font-medium truncate">{playlist.title}</h3>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {playlist.source_type} · {new Date(playlist.created_at).toLocaleDateString()}
                  </p>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}