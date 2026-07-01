/**
 * Continue learning card component.
 *
 * Shows the user's current learning progress and provides
 * a quick way to resume watching.
 *
 * Used on the dashboard.
 */

import { Play, Clock, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/common/components/ui/card';
import { Button } from '@/common/components/ui/button';
import type { ContinueLearningResponse } from '@/features/learning/services/learning-service';

interface ContinueLearningCardProps {
  /** Continue learning data from API */
  data: ContinueLearningResponse | undefined;
  /** Whether data is loading */
  isLoading?: boolean;
  /** Additional CSS classes */
  className?: string;
}

export function ContinueLearningCard({
  data,
  isLoading = false,
  className = '',
}: ContinueLearningCardProps) {
  const currentVideo = data?.current_video;
  const recentlyWatched = data?.recently_watched ?? [];

  const formatDuration = (seconds: number | null): string => {
    if (!seconds) return '';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Play className="size-5" />
            Continue Learning
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2].map((i) => (
              <div key={i} className="h-16 animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!currentVideo && recentlyWatched.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Play className="size-5" />
            Continue Learning
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="mb-3 flex size-12 items-center justify-center rounded-full bg-muted">
              <Play className="size-6 text-muted-foreground" />
            </div>
            <p className="text-sm font-medium">No videos in progress</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Start watching a video to see it here
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Play className="size-5" />
          Continue Learning
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Current video - Resume button */}
          {currentVideo && (
            <div>
              <p className="mb-2 text-xs font-medium text-muted-foreground uppercase">
                Resume Watching
              </p>
              <a
                href={`/dashboard/workspace/${currentVideo.playlist.id}/${currentVideo.video.id}`}
                className="block"
              >
                <div className="flex items-center gap-3 rounded-lg border p-3 transition-colors hover:bg-accent">
                  {currentVideo.video.thumbnail_url ? (
                    <img
                      src={currentVideo.video.thumbnail_url}
                      alt={currentVideo.video.title}
                      className="size-16 rounded-md object-cover"
                    />
                  ) : (
                    <div className="flex size-16 items-center justify-center rounded-md bg-muted">
                      <Play className="size-6 text-muted-foreground" />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium line-clamp-2">
                      {currentVideo.video.title}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {currentVideo.playlist.title}
                    </p>
                    <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                      <Clock className="size-3" />
                      {formatDuration(currentVideo.video.duration_seconds ?? null)}
                    </div>
                  </div>
                  <Button size="sm" className="shrink-0">
                    <Play className="mr-1 size-4" fill="currentColor" />
                    Resume
                  </Button>
                </div>
              </a>
            </div>
          )}

          {/* Recently watched */}
          {recentlyWatched.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-medium text-muted-foreground uppercase">
                Recently Opened
              </p>
              <div className="space-y-2">
                {recentlyWatched.slice(0, 3).map((item) => (
                  <a
                    key={item.video.id}
                    href={`/dashboard/workspace/${item.playlist.id}/${item.video.id}`}
                    className="flex items-center gap-2 rounded-lg p-2 transition-colors hover:bg-accent"
                  >
                    {item.video.thumbnail_url ? (
                      <img
                        src={item.video.thumbnail_url}
                        alt={item.video.title}
                        className="size-10 rounded-md object-cover"
                      />
                    ) : (
                      <div className="flex size-10 items-center justify-center rounded-md bg-muted">
                        <Play className="size-4 text-muted-foreground" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium line-clamp-1">{item.video.title}</p>
                      <p className="text-xs text-muted-foreground">{item.playlist.title}</p>
                    </div>
                    {item.progress.status === 'completed' && (
                      <CheckCircle2 className="size-4 text-green-600" />
                    )}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}