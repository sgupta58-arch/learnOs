/**
 * Learning feature public API.
 *
 * This file exports all public components, hooks, and utilities
 * from the learning feature for use by other features and pages.
 */

// Components
export { VideoPlayer } from './components/video-player';
export { PlaylistSidebar } from './components/playlist-sidebar';
export { LearningControls } from './components/learning-controls';
export { NotesPanel } from './components/notes-panel';
export { ResourcesPanel } from './components/resources-panel';
export { ContinueLearningCard } from './components/continue-learning-card';

// Hooks
export { useLearningWorkspace } from './hooks/use-learning-workspace';

// Services
export {
  getContinueLearning,
  getVideoProgress,
  updateVideoProgress,
  markVideoComplete,
  markVideoInProgress,
} from './services/learning-service';

// Types
export type {
  Video,
  PlaylistServiceVideo,
  VideoProgress,
  VideoProgressUpdate,
  PlaylistWithVideos,
  PlaybackSpeed,
  WorkspaceTab,
  LearningWorkspaceState,
} from './types';

export type { ContinueLearningResponse } from './services/learning-service';