/**
 * Playlist sidebar component for the learning workspace.
 *
 * Features:
 * - Displays playlist title and video count
 * - Lists all videos with progress indicators
 * - Highlights current video
 * - Shows completion status
 * - Supports keyboard navigation
 * - Responsive: collapsible on desktop, drawer on mobile
 */

import { useMemo } from 'react';
import { Play, CheckCircle2, Clock } from 'lucide-react';
import { cn } from '@/common/utils/cn';
import type { Video, PlaylistWithVideos } from '@/features/learning/types';

interface PlaylistSidebarProps {
  /** Current playlist with videos */
  playlist: PlaylistWithVideos | null;
  /** Currently playing video ID */
  currentVideoId: string | null;
  /** Whether sidebar is collapsed */
  collapsed: boolean;
  /** Callback when video is selected */
  onVideoSelect: (video: Video) => void;
  /** Additional CSS classes */
  className?: string;
}

export function PlaylistSidebar({
  playlist,
  currentVideoId,
  collapsed,
  onVideoSelect,
  className = '',
}: PlaylistSidebarProps) {
  const videos = useMemo(() => playlist?.videos ?? [], [playlist]);

  const formatDuration = (seconds: number | null): string => {
    if (!seconds) return '';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!playlist) {
    return null;
  }

  return (
    <div
      className={cn(
        'flex h-full flex-col border-r bg-background',
        collapsed ? 'w-0 overflow-hidden' : 'w-80',
        className
      )}
    >
      {/* Playlist header */}
      <div className="border-b p-4">
        <h2 className="text-lg font-semibold line-clamp-2">{playlist.title}</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          {videos.length} video{videos.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Video list */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2">
          {videos.map((video, index) => {
            const isCurrent = video.id === currentVideoId;
            const isCompleted = video.progress?.status === 'completed';
            const isInProgress = video.progress?.status === 'in_progress';

            return (
              <button
                key={video.id}
                onClick={() => onVideoSelect(video)}
                className={cn(
                  'w-full rounded-lg p-3 text-left transition-colors',
                  'hover:bg-accent focus:bg-accent focus:outline-none',
                  'focus:ring-2 focus:ring-ring focus:ring-offset-2',
                  isCurrent && 'bg-accent'
                )}
                aria-current={isCurrent ? 'true' : undefined}
              >
                <div className="flex items-start gap-3">
                  {/* Video number or status icon */}
                  <div className="flex size-8 shrink-0 items-center justify-center rounded-md bg-muted">
                    {isCompleted ? (
                      <CheckCircle2 className="size-4 text-green-600" />
                    ) : isCurrent ? (
                      <Play className="size-4 text-primary" fill="currentColor" />
                    ) : (
                      <span className="text-xs font-medium text-muted-foreground">
                        {index + 1}
                      </span>
                    )}
                  </div>

                  {/* Video info */}
                  <div className="flex-1 min-w-0">
                    <p
                      className={cn(
                        'text-sm line-clamp-2',
                        isCurrent && 'font-medium text-primary'
                      )}
                    >
                      {video.title}
                    </p>
                    <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                      {video.duration_seconds && (
                        <span className="flex items-center gap-1">
                          <Clock className="size-3" />
                          {formatDuration(video.duration_seconds)}
                        </span>
                      )}
                      {isInProgress && (
                        <span className="text-xs text-blue-600">In Progress</span>
                      )}
                    </div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}