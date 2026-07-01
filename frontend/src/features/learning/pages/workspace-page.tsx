/**
 * Learning workspace page.
 *
 * This is the main learning experience where users watch videos,
 * take notes, and track their progress.
 *
 * Layout:
 * - Left: Playlist sidebar (collapsible)
 * - Center: Video player + controls
 * - Right: Info panel (tabs: Overview, Transcript, Notes, Tutor, Resources)
 *
 * Backend integration:
 * - Playlist/videos: Connected (via playlist service)
 * - Progress: Connected (via learning service)
 * - Notes: Future
 * - Transcript: Future
 * - AI Tutor: Future
 */

import { useParams, Navigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getPlaylist, getPlaylistVideos } from '@/features/playlist/services/playlist-service';
import { VideoPlayer } from '@/features/learning/components/video-player';
import { PlaylistSidebar } from '@/features/learning/components/playlist-sidebar';
import { LearningControls } from '@/features/learning/components/learning-controls';
import { NotesPanel } from '@/features/learning/components/notes-panel';
import { ResourcesPanel } from '@/features/learning/components/resources-panel';
import { useLearningWorkspace } from '@/features/learning/hooks/use-learning-workspace';
import { PageHeader } from '@/common/components/page-header';
import { Button } from '@/common/components/ui/button';
import { ArrowLeft, Sidebar, MessageSquare, FileText, FileType, Paperclip } from 'lucide-react';
import { cn } from '@/common/utils/cn';
import type { Video } from '@/features/learning/types';

type WorkspaceTab = 'overview' | 'transcript' | 'notes' | 'tutor' | 'resources';

export function WorkspacePage() {
  const { playlistId, videoId } = useParams<{ playlistId: string; videoId: string }>();

  // Fetch playlist and videos
  const { data: playlistData, isLoading: playlistLoading } = useQuery({
    queryKey: ['playlist', playlistId],
    queryFn: () => getPlaylist(playlistId!),
    enabled: !!playlistId,
  });

  const { data: videos, isLoading: videosLoading } = useQuery({
    queryKey: ['playlist-videos', playlistId],
    queryFn: () => getPlaylistVideos(playlistId!),
    enabled: !!playlistId,
  });

  // Learning workspace state
  const workspace = useLearningWorkspace();

  // Set playlist when loaded
  React.useEffect(() => {
    if (playlistData?.data && videos) {
      workspace.setCurrentPlaylist({
        ...playlistData.data,
        videos: videos as Video[],
      });
    }
  }, [playlistData, videos, workspace]);

  // Set initial video from URL param
  React.useEffect(() => {
    if (videoId && videos && !workspace.currentVideo) {
      const initialVideo = videos.find((v) => v.id === videoId);
      if (initialVideo) {
        workspace.goToVideo(initialVideo as Video);
      }
    }
  }, [videoId, videos, workspace]);

  const isLoading = playlistLoading || videosLoading;
  const playlist = playlistData?.data;

  // Redirect if no playlist ID
  if (!playlistId) {
    return <Navigate to="/dashboard/playlists" replace />;
  }

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Loading workspace..." />
        <div className="flex items-center justify-center py-12">
          <div className="size-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
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
            <Button variant="outline" size="sm" asChild>
              <a href="/dashboard/playlists">
                <ArrowLeft className="mr-1 size-4" />
                Back to Playlists
              </a>
            </Button>
          }
        />
      </div>
    );
  }

  const currentVideo = workspace.currentVideo;

  return (
    <div className="flex h-screen flex-col">
      {/* Top bar */}
      <div className="flex items-center justify-between border-b px-4 py-2">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={workspace.toggleSidebar}
            aria-label="Toggle sidebar"
          >
            <Sidebar className="size-4" />
          </Button>
          <div>
            <h1 className="text-sm font-medium">{playlist.title}</h1>
            {currentVideo && (
              <p className="text-xs text-muted-foreground line-clamp-1">
                {currentVideo.title}
              </p>
            )}
          </div>
        </div>

        <Button variant="ghost" size="sm" asChild>
          <a href="/dashboard/playlists">
            <ArrowLeft className="mr-1 size-4" />
            Exit
          </a>
        </Button>
      </div>

      {/* Main workspace */}
      <div className="flex flex-1 overflow-hidden">
        {/* Playlist sidebar */}
        <PlaylistSidebar
          playlist={playlistData?.data ? { ...playlistData.data, videos: videos as Video[] } : null}
          currentVideoId={currentVideo?.id ?? null}
          collapsed={workspace.sidebarCollapsed}
          onVideoSelect={(video) => workspace.goToVideo(video)}
        />

        {/* Center: Player + Controls */}
        <div className="flex flex-1 flex-col">
          {currentVideo ? (
            <>
              {/* Video player */}
              <div className="flex-1 flex items-center justify-center bg-black">
                <VideoPlayer
                  videoId={currentVideo.youtube_video_id}
                  isPlaying={workspace.isPlaying}
                  currentTime={workspace.currentTime}
                  playbackSpeed={workspace.playbackSpeed}
                  onTimeUpdate={workspace.setCurrentTime}
                  onDurationChange={workspace.setDuration}
                  onPlayStateChange={workspace.setIsPlaying}
                  onPlaybackSpeedChange={workspace.setPlaybackSpeed}
                  className="max-h-full"
                />
              </div>

              {/* Learning controls */}
              <LearningControls
                hasPrevious={workspace.hasPreviousVideo}
                hasNext={workspace.hasNextVideo}
                autoplayEnabled={workspace.autoplayEnabled}
                playbackSpeed={workspace.playbackSpeed}
                onPrevious={workspace.goToPreviousVideo}
                onNext={workspace.goToNextVideo}
                onMarkComplete={() => {}}
                onAutoplayToggle={workspace.toggleAutoplay}
                onPlaybackSpeedChange={workspace.setPlaybackSpeed}
                onFullscreen={() => {}}
              />
            </>
          ) : (
            <div className="flex flex-1 items-center justify-center">
              <div className="text-center">
                <p className="text-muted-foreground">Select a video to start learning</p>
              </div>
            </div>
          )}
        </div>

        {/* Right: Info panel */}
        {currentVideo && (
          <div className="hidden lg:flex w-96 flex-col border-l">
            {/* Tabs */}
            <div className="flex border-b">
              {[
                { id: 'overview', label: 'Overview', icon: MessageSquare },
                { id: 'transcript', label: 'Transcript', icon: FileType, disabled: true },
                { id: 'notes', label: 'Notes', icon: FileText },
                { id: 'tutor', label: 'Tutor', icon: MessageSquare, disabled: true },
                { id: 'resources', label: 'Resources', icon: Paperclip },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => workspace.setActiveTab(tab.id as WorkspaceTab)}
                  disabled={tab.disabled}
                  className={cn(
                    'flex-1 px-3 py-2 text-xs font-medium transition-colors',
                    'hover:bg-accent focus:bg-accent focus:outline-none',
                    'disabled:opacity-50 disabled:cursor-not-allowed',
                    workspace.activeTab === tab.id && 'border-b-2 border-primary'
                  )}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab content */}
            <div className="flex-1 overflow-hidden">
              {workspace.activeTab === 'overview' && (
                <div className="p-4">
                  <h3 className="font-semibold mb-2">{currentVideo.title}</h3>
                  {currentVideo.channel_name && (
                    <p className="text-sm text-muted-foreground mb-2">
                      {currentVideo.channel_name}
                    </p>
                  )}
                  {currentVideo.description && (
                    <p className="text-sm text-muted-foreground line-clamp-4">
                      {currentVideo.description}
                    </p>
                  )}
                </div>
              )}

              {workspace.activeTab === 'notes' && (
                <NotesPanel videoId={currentVideo.id} currentTime={workspace.currentTime} />
              )}

              {workspace.activeTab === 'resources' && (
                <ResourcesPanel videoId={currentVideo.id} />
              )}

              {workspace.activeTab === 'transcript' && (
                <div className="flex h-full items-center justify-center p-8">
                  <div className="text-center">
                    <FileType className="mx-auto mb-2 size-12 text-muted-foreground" />
                    <p className="text-sm font-medium">Transcript</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Transcript will be available in a future update.
                    </p>
                  </div>
                </div>
              )}

              {workspace.activeTab === 'tutor' && (
                <div className="flex h-full items-center justify-center p-8">
                  <div className="text-center">
                    <MessageSquare className="mx-auto mb-2 size-12 text-muted-foreground" />
                    <p className="text-sm font-medium">AI Tutor</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      AI Tutor will be available once transcript processing is complete.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Import React for useEffect
import React from 'react';