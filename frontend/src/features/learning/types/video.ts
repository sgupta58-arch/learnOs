/**
 * Video types for the learning workspace.
 * Extends backend Video schema with learning-specific fields.
 */

export interface Video extends PlaylistServiceVideo {
  /** Learning progress state */
  progress?: VideoProgress;
  
  /** Whether video is currently being watched */
  is_current?: boolean;
}

export interface PlaylistServiceVideo {
  id: string;
  playlist_id: string;
  youtube_video_id: string;
  title: string;
  description: string | null;
  thumbnail_url: string | null;
  channel_name: string | null;
  duration_seconds: number | null;
  position: number | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface VideoProgress {
  id: string;
  user_id: string;
  video_id: string;
  playlist_id: string;
  status: 'not_started' | 'in_progress' | 'completed';
  progress_seconds: number;
  last_watched_at: string;
  created_at: string;
  updated_at: string;
}

export interface VideoProgressUpdate {
  video_id: string;
  playlist_id: string;
  progress_seconds: number;
  status?: 'not_started' | 'in_progress' | 'completed';
}

export interface PlaylistWithVideos {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  source_type: string;
  source_url: string | null;
  thumbnail_url: string | null;
  status: string;
  target_completion_date: string | null;
  created_at: string;
  updated_at: string;
  videos: Video[];
}

export type PlaybackSpeed = 0.5 | 0.75 | 1 | 1.25 | 1.5 | 1.75 | 2;

export type WorkspaceTab = 'overview' | 'transcript' | 'notes' | 'tutor' | 'resources';

export interface LearningWorkspaceState {
  currentVideo: Video | null;
  currentPlaylist: PlaylistWithVideos | null;
  isPlaying: boolean;
  playbackSpeed: PlaybackSpeed;
  currentTime: number;
  duration: number;
  activeTab: WorkspaceTab;
  sidebarCollapsed: boolean;
  autoplayEnabled: boolean;
}