import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getPlaylist, getPlaylistVideos } from '@/features/playlist/services/playlist-service';
import { PageHeader } from '@/common/components/page-header';
import { Card, CardContent } from '@/common/components/ui/card';
import { Button } from '@/common/components/ui/button';
import { ArrowLeft, Play, Clock, ListVideo, AlertCircle } from 'lucide-react';

export function PlaylistDetailPage() {
  const { playlistId } = useParams<{ playlistId: string }>();

  const { data: playlistData, isLoading: playlistLoading } = useQuery({
    queryKey: ['playlist', playlistId],
    queryFn: () => getPlaylist(playlistId!),
    enabled: !!playlistId,
  });

  const { data: videos, isLoading: videosLoading, isError: videosError, refetch: refetchVideos } = useQuery({
    queryKey: ['playlist-videos', playlistId],
    queryFn: () => getPlaylistVideos(playlistId!),
    enabled: !!playlistId,
  });

  const playlist = playlistData?.data;
  const isLoading = playlistLoading || videosLoading;

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Loading..." />
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-16 animate-pulse rounded-lg bg-muted" />
          ))}
        </div>
      </div>
    );
  }

  if (!playlist) {
    return (
      <div>
        <PageHeader
          title="Playlist not found"
          actions={
            <Link to="/dashboard/playlists">
              <Button variant="outline" size="sm">
                <ArrowLeft className="mr-1 size-4" />
                Back to Playlists
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
        title={playlist.title}
        description={
          videos ? `${videos.length} video${videos.length !== 1 ? 's' : ''}` : undefined
        }
        actions={
          <Link to="/dashboard/playlists">
            <Button variant="outline" size="sm">
              <ArrowLeft className="mr-1 size-4" />
              Back
            </Button>
          </Link>
        }
      />

      {videosError ? (
        <div className="flex flex-col items-center justify-center py-12">
          <AlertCircle className="mb-2 size-8 text-destructive" />
          <p className="text-sm text-muted-foreground">Failed to load videos</p>
          <Button variant="outline" size="sm" className="mt-4" onClick={() => refetchVideos()}>
            Retry
          </Button>
        </div>
      ) : !videos || videos.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12">
          <ListVideo className="mb-2 size-8 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">No videos in this playlist</p>
        </div>
      ) : (
        <div className="space-y-2">
          {videos.map((video, index) => (
            <Card key={video.id} className="transition-shadow hover:shadow-sm">
              <CardContent className="flex items-center gap-4 p-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted text-sm text-muted-foreground">
                  {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{video.title}</p>
                  {video.channel_name && (
                    <p className="text-xs text-muted-foreground">{video.channel_name}</p>
                  )}
                </div>
                {video.duration_seconds && (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="size-3" />
                    {Math.floor(video.duration_seconds / 60)}:{(video.duration_seconds % 60).toString().padStart(2, '0')}
                  </div>
                )}
                <Button variant="ghost" size="icon" className="size-8">
                  <Play className="size-4" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}