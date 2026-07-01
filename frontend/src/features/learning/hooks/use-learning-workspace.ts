/**
 * Custom hook for managing learning workspace state.
 *
 * Handles:
 * - Current video and playlist state
 * - Playback controls (play/pause, speed, time)
 * - Video navigation (previous/next)
 * - Progress tracking
 * - Keyboard shortcuts
 */

import { useState, useCallback, useEffect } from 'react';
import type { Video, PlaylistWithVideos, PlaybackSpeed, WorkspaceTab } from '@/features/learning/types';

export interface UseLearningWorkspaceReturn {
  // State
  currentVideo: Video | null;
  currentPlaylist: PlaylistWithVideos | null;
  isPlaying: boolean;
  playbackSpeed: PlaybackSpeed;
  currentTime: number;
  duration: number;
  activeTab: WorkspaceTab;
  sidebarCollapsed: boolean;
  autoplayEnabled: boolean;
  
  // Actions
  setCurrentVideo: (video: Video | null) => void;
  setCurrentPlaylist: (playlist: PlaylistWithVideos | null) => void;
  setIsPlaying: (playing: boolean) => void;
  setPlaybackSpeed: (speed: PlaybackSpeed) => void;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
  setActiveTab: (tab: WorkspaceTab) => void;
  toggleSidebar: () => void;
  toggleAutoplay: () => void;
  
  // Navigation
  goToVideo: (video: Video) => void;
  goToNextVideo: () => void;
  goToPreviousVideo: () => void;
  hasNextVideo: boolean;
  hasPreviousVideo: boolean;
}

export function useLearningWorkspace(): UseLearningWorkspaceReturn {
  const [currentVideo, setCurrentVideo] = useState<Video | null>(null);
  const [currentPlaylist, setCurrentPlaylist] = useState<PlaylistWithVideos | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<PlaybackSpeed>(1);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [autoplayEnabled, setAutoplayEnabled] = useState(true);

  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed((prev) => !prev);
  }, []);

  const toggleAutoplay = useCallback(() => {
    setAutoplayEnabled((prev) => !prev);
  }, []);

  const getCurrentIndex = useCallback(() => {
    if (!currentPlaylist || !currentVideo) return -1;
    return currentPlaylist.videos.findIndex((v) => v.id === currentVideo.id);
  }, [currentPlaylist, currentVideo]);

  const hasNextVideo = currentPlaylist ? getCurrentIndex() < currentPlaylist.videos.length - 1 : false;
  const hasPreviousVideo = getCurrentIndex() > 0;

  const goToVideo = useCallback(
    (video: Video) => {
      setCurrentVideo(video);
      setCurrentTime(0);
      setIsPlaying(true);
    },
    []
  );

  const goToNextVideo = useCallback(() => {
    if (!hasNextVideo || !currentPlaylist) return;
    const currentIndex = getCurrentIndex();
    const nextVideo = currentPlaylist.videos[currentIndex + 1];
    if (nextVideo) {
      goToVideo(nextVideo);
    }
  }, [hasNextVideo, currentPlaylist, getCurrentIndex, goToVideo]);

  const goToPreviousVideo = useCallback(() => {
    if (!hasPreviousVideo || !currentPlaylist) return;
    const currentIndex = getCurrentIndex();
    const previousVideo = currentPlaylist.videos[currentIndex - 1];
    if (previousVideo) {
      goToVideo(previousVideo);
    }
  }, [hasPreviousVideo, currentPlaylist, getCurrentIndex, goToVideo]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in inputs
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement ||
        event.target instanceof HTMLSelectElement
      ) {
        return;
      }

      switch (event.key) {
        case ' ':
          // Space: Toggle play/pause
          event.preventDefault();
          setIsPlaying((prev) => !prev);
          break;
        case 'ArrowRight':
          // Right arrow: Next video (with Ctrl/Cmd)
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            goToNextVideo();
          }
          break;
        case 'ArrowLeft':
          // Left arrow: Previous video (with Ctrl/Cmd)
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            goToPreviousVideo();
          }
          break;
        case 'b':
          // B: Toggle sidebar
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            toggleSidebar();
          }
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [goToNextVideo, goToPreviousVideo, toggleSidebar]);

  return {
    // State
    currentVideo,
    currentPlaylist,
    isPlaying,
    playbackSpeed,
    currentTime,
    duration,
    activeTab,
    sidebarCollapsed,
    autoplayEnabled,
    
    // Actions
    setCurrentVideo,
    setCurrentPlaylist,
    setIsPlaying,
    setPlaybackSpeed,
    setCurrentTime,
    setDuration,
    setActiveTab,
    toggleSidebar,
    toggleAutoplay,
    
    // Navigation
    goToVideo,
    goToNextVideo,
    goToPreviousVideo,
    hasNextVideo,
    hasPreviousVideo,
  };
}