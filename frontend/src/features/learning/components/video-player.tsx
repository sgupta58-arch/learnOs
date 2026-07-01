/**
 * Video player component with YouTube embed.
 *
 * Features:
 * - YouTube iframe embed
 * - Play/pause state tracking
 * - Playback speed control
 * - Time tracking for progress
 * - Responsive aspect ratio
 */

import { useRef, useEffect, useCallback } from 'react';
import { Play, Pause, Volume2 } from 'lucide-react';
import { Button } from '@/common/components/ui/button';
import type { PlaybackSpeed } from '@/features/learning/types';

// Extend Window interface for YouTube API
declare global {
  interface Window {
    YT: any;
    onYouTubeIframeAPIReady: () => void;
  }
}

interface VideoPlayerProps {
  /** YouTube video ID */
  videoId: string;
  /** Whether video is currently playing */
  isPlaying: boolean;
  /** Current playback time in seconds */
  currentTime: number;
  /** Playback speed */
  playbackSpeed: PlaybackSpeed;
  /** Callback when time updates */
  onTimeUpdate: (time: number) => void;
  /** Callback when duration changes */
  onDurationChange: (duration: number) => void;
  /** Callback when play state changes */
  onPlayStateChange: (isPlaying: boolean) => void;
  /** Callback when playback speed changes */
  onPlaybackSpeedChange: (speed: PlaybackSpeed) => void;
  /** Additional CSS classes */
  className?: string;
}

export function VideoPlayer({
  videoId,
  isPlaying,
  currentTime,
  playbackSpeed,
  onTimeUpdate,
  onDurationChange,
  onPlayStateChange,
  onPlaybackSpeedChange,
  className = '',
}: VideoPlayerProps) {
  const playerRef = useRef<any | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const isInitialized = useRef(false);

  // Initialize YouTube player
  useEffect(() => {
    // Load YouTube API if not already loaded
    if (!window.YT) {
      const tag = document.createElement('script');
      tag.src = 'https://www.youtube.com/iframe_api';
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);

      window.onYouTubeIframeAPIReady = () => {
        initializePlayer();
      };
    } else if (!isInitialized.current) {
      initializePlayer();
    }

    return () => {
      if (playerRef.current) {
        playerRef.current.destroy();
        playerRef.current = null;
        isInitialized.current = false;
      }
    };
  }, [videoId]);

  const initializePlayer = useCallback(() => {
    if (!containerRef.current || !window.YT || isInitialized.current) return;

    playerRef.current = new window.YT.Player(containerRef.current, {
      videoId,
      playerVars: {
        autoplay: isPlaying ? 1 : 0,
        controls: 1,
        modestbranding: 1,
        rel: 0,
        fs: 1,
        playsinline: 1,
      },
      events: {
        onReady: (event: any) => {
          isInitialized.current = true;
          onDurationChange(event.target.getDuration());
          
          // Set initial playback speed
          event.target.setPlaybackRate(playbackSpeed);
          
          // Start playing if needed
          if (isPlaying) {
            event.target.playVideo();
          }
        },
        onStateChange: (event: any) => {
          // PlayerState: -1 (unstarted), 0 (ended), 1 (playing), 2 (paused), 3 (buffering)
          const playing = event.data === window.YT.PlayerState.PLAYING;
          onPlayStateChange(playing);
        },
      },
    });

    // Start time update interval
    const interval = setInterval(() => {
      if (playerRef.current && window.YT) {
        const time = playerRef.current.getCurrentTime();
        onTimeUpdate(time);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [videoId, isPlaying, playbackSpeed, onTimeUpdate, onDurationChange, onPlayStateChange]);

  // Handle play/pause changes
  useEffect(() => {
    if (!playerRef.current || !isInitialized.current) return;

    if (isPlaying) {
      playerRef.current.playVideo();
    } else {
      playerRef.current.pauseVideo();
    }
  }, [isPlaying]);

  // Handle playback speed changes
  useEffect(() => {
    if (!playerRef.current || !isInitialized.current) return;
    playerRef.current.setPlaybackRate(playbackSpeed);
  }, [playbackSpeed]);

  // Handle seeking
  useEffect(() => {
    if (!playerRef.current || !isInitialized.current) return;
    const playerTime = playerRef.current.getCurrentTime();
    
    // Only seek if difference is significant (avoid feedback loop)
    if (Math.abs(playerTime - currentTime) > 2) {
      playerRef.current.seekTo(currentTime, true);
    }
  }, [currentTime]);

  const handlePlayPause = useCallback(() => {
    onPlayStateChange(!isPlaying);
  }, [isPlaying, onPlayStateChange]);

  const cyclePlaybackSpeed = useCallback(() => {
    const speeds: PlaybackSpeed[] = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];
    const currentIndex = speeds.indexOf(playbackSpeed);
    const nextIndex = (currentIndex + 1) % speeds.length;
    onPlaybackSpeedChange(speeds[nextIndex]);
  }, [playbackSpeed, onPlaybackSpeedChange]);

  return (
    <div className={`relative w-full ${className}`}>
      {/* YouTube player container */}
      <div
        ref={containerRef}
        className="aspect-video w-full bg-black"
        aria-label="Video player"
      />
      
      {/* Custom controls overlay */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="size-10 text-white hover:bg-white/20"
            onClick={handlePlayPause}
            aria-label={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? (
              <Pause className="size-5" fill="white" />
            ) : (
              <Play className="size-5" fill="white" />
            )}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            className="text-white hover:bg-white/20"
            onClick={cyclePlaybackSpeed}
            aria-label={`Playback speed: ${playbackSpeed}x`}
          >
            <Volume2 className="mr-1 size-4" />
            {playbackSpeed}x
          </Button>
        </div>
      </div>
    </div>
  );
}
