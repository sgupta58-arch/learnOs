/**
 * Learning controls component.
 *
 * Features:
 * - Previous/Next video navigation
 * - Mark as complete button
 * - Playback speed selector
 * - Autoplay toggle
 * - Fullscreen button
 * - Keyboard shortcut hints
 */

import { ChevronLeft, ChevronRight, Check, Monitor, Gauge } from 'lucide-react';
import { Button } from '@/common/components/ui/button';
import { cn } from '@/common/utils/cn';
import type { PlaybackSpeed } from '@/features/learning/types';

interface LearningControlsProps {
  /** Whether there's a previous video */
  hasPrevious: boolean;
  /** Whether there's a next video */
  hasNext: boolean;
  /** Whether autoplay is enabled */
  autoplayEnabled: boolean;
  /** Current playback speed */
  playbackSpeed: PlaybackSpeed;
  /** Callback when previous video is clicked */
  onPrevious: () => void;
  /** Callback when next video is clicked */
  onNext: () => void;
  /** Callback when mark complete is clicked */
  onMarkComplete: () => void;
  /** Callback when autoplay is toggled */
  onAutoplayToggle: () => void;
  /** Callback when playback speed changes */
  onPlaybackSpeedChange: (speed: PlaybackSpeed) => void;
  /** Callback when fullscreen is clicked */
  onFullscreen: () => void;
  /** Additional CSS classes */
  className?: string;
}

const PLAYBACK_SPEEDS: PlaybackSpeed[] = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];

export function LearningControls({
  hasPrevious,
  hasNext,
  autoplayEnabled,
  playbackSpeed,
  onPrevious,
  onNext,
  onMarkComplete,
  onAutoplayToggle,
  onPlaybackSpeedChange,
  onFullscreen,
  className = '',
}: LearningControlsProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-between gap-2 border-t bg-background p-3',
        className
      )}
    >
      {/* Left: Navigation */}
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={onPrevious}
          disabled={!hasPrevious}
          aria-label="Previous video"
          title="Previous video (Ctrl+Left)"
        >
          <ChevronLeft className="size-4" />
        </Button>

        <Button
          variant="ghost"
          size="sm"
          onClick={onNext}
          disabled={!hasNext}
          aria-label="Next video"
          title="Next video (Ctrl+Right)"
        >
          <ChevronRight className="size-4" />
        </Button>

        <Button
          variant="ghost"
          size="sm"
          onClick={onMarkComplete}
          aria-label="Mark as complete"
          title="Mark as complete"
        >
          <Check className="mr-1 size-4" />
          <span className="hidden sm:inline">Complete</span>
        </Button>
      </div>

      {/* Center: Autoplay */}
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={onAutoplayToggle}
          aria-label={autoplayEnabled ? 'Disable autoplay' : 'Enable autoplay'}
          title={autoplayEnabled ? 'Autoplay enabled' : 'Autoplay disabled'}
        >
          <Gauge className={cn('size-4', autoplayEnabled && 'text-primary')} />
          <span className="hidden sm:inline ml-1">
            {autoplayEnabled ? 'Autoplay On' : 'Autoplay Off'}
          </span>
        </Button>
      </div>

      {/* Right: Speed and Fullscreen */}
      <div className="flex items-center gap-2">
        {/* Playback speed selector */}
        <div className="flex items-center gap-1">
          {PLAYBACK_SPEEDS.map((speed) => (
            <Button
              key={speed}
              variant={playbackSpeed === speed ? 'default' : 'ghost'}
              size="sm"
              onClick={() => onPlaybackSpeedChange(speed)}
              aria-label={`Playback speed ${speed}x`}
              title={`${speed}x`}
              className="hidden md:flex min-w-[3rem]"
            >
              {speed}x
            </Button>
          ))}
          {/* Mobile: Show current speed only */}
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden"
            aria-label="Change playback speed"
          >
            <Gauge className="size-4" />
            {playbackSpeed}x
          </Button>
        </div>

        <Button
          variant="ghost"
          size="icon"
          onClick={onFullscreen}
          aria-label="Toggle fullscreen"
          title="Fullscreen"
        >
          <Monitor className="size-4" />
        </Button>
      </div>
    </div>
  );
}