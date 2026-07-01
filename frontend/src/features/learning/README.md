# Learning Feature

The learning feature provides the core video watching and learning workspace experience for LearnOS.

## Architecture

```
learning/
├── components/          # Reusable UI components
│   ├── video-player.tsx           # YouTube embed player
│   ├── playlist-sidebar.tsx       # Playlist navigation sidebar
│   ├── learning-controls.tsx      # Playback controls
│   ├── notes-panel.tsx            # Notes editor (UI only)
│   ├── resources-panel.tsx        # Resources panel (placeholder)
│   └── continue-learning-card.tsx # Dashboard continue learning widget
├── pages/
│   └── workspace-page.tsx         # Main learning workspace page
├── hooks/
│   └── use-learning-workspace.ts  # Workspace state management
├── services/
│   └── learning-service.ts        # API calls for progress tracking
├── types/
│   ├── video.ts                   # TypeScript types
│   ├── index.ts                   # Type exports
│   └── youtube.d.ts               # YouTube API type declarations
└── index.ts                       # Public API exports
```

## Components

### VideoPlayer
Embeds YouTube videos with custom controls and state tracking.

**Props:**
- `videoId`: YouTube video ID
- `isPlaying`: Play/pause state
- `currentTime`: Current playback time
- `duration`: Video duration
- `playbackSpeed`: Playback speed (0.5x - 2x)
- `onTimeUpdate`: Time update callback
- `onDurationChange`: Duration change callback
- `onPlayStateChange`: Play state change callback
- `onPlaybackSpeedChange`: Speed change callback

### PlaylistSidebar
Displays playlist videos with progress indicators and navigation.

**Props:**
- `playlist`: Playlist with videos
- `currentVideoId`: Currently playing video ID
- `collapsed`: Sidebar collapse state
- `onVideoSelect`: Video selection callback

### LearningControls
Provides video navigation and playback controls.

**Props:**
- `hasPrevious`/`hasNext`: Navigation availability
- `autoplayEnabled`: Autoplay state
- `playbackSpeed`: Current speed
- `onPrevious`/`onNext`: Navigation callbacks
- `onMarkComplete`: Mark complete callback
- `onAutoplayToggle`: Autoplay toggle callback
- `onPlaybackSpeedChange`: Speed change callback
- `onFullscreen`: Fullscreen toggle callback

### NotesPanel
Notes editor with timestamp linking (UI only, backend integration future).

**Props:**
- `videoId`: Current video ID
- `currentTime`: Current timestamp

### ResourcesPanel
Placeholder for future PDFs, links, and attachments.

**Props:**
- `videoId`: Current video ID

### ContinueLearningCard
Dashboard widget showing resume points and recently watched videos.

**Props:**
- `data`: Continue learning data from API
- `isLoading`: Loading state

## Hooks

### useLearningWorkspace
Manages all learning workspace state including:
- Current video/playlist
- Playback state (play/pause, speed, time)
- Video navigation (previous/next)
- Active tab
- Sidebar state
- Autoplay state
- Keyboard shortcuts

**Returns:**
```typescript
{
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
```

## Services

### learning-service.ts
API functions for learning/workspace operations:

- `getContinueLearning()`: Fetch continue learning data
- `getVideoProgress(videoId)`: Get video progress
- `updateVideoProgress(payload)`: Update video progress
- `markVideoComplete(videoId, playlistId)`: Mark video as completed
- `markVideoInProgress(videoId, playlistId, progressSeconds)`: Mark video as in progress

## Types

### Video
Extended video type with learning-specific fields:
```typescript
interface Video extends PlaylistServiceVideo {
  progress?: VideoProgress;
  is_current?: boolean;
}
```

### VideoProgress
Progress tracking state:
```typescript
interface VideoProgress {
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
```

### PlaybackSpeed
Union type for valid playback speeds: `0.5 | 0.75 | 1 | 1.25 | 1.5 | 1.75 | 2`

### WorkspaceTab
Union type for info panel tabs: `'overview' | 'transcript' | 'notes' | 'tutor' | 'resources'`

## Routes

- `/dashboard/workspace/:playlistId/:videoId` - Learning workspace page

## Keyboard Shortcuts

- `Space`: Toggle play/pause
- `Ctrl/Cmd + Right Arrow`: Next video
- `Ctrl/Cmd + Left Arrow`: Previous video
- `Ctrl/Cmd + B`: Toggle sidebar

## Backend Integration

### Currently Connected
- Playlist/video fetching (via playlist service)
- Continue learning data (via learning service)

### Future Integration
- Video progress persistence
- Notes CRUD
- Transcript fetching
- AI Tutor chat

## Responsive Design

- **Desktop (lg+)**: Three-column layout (sidebar + player + info panel)
- **Tablet (md)**: Two-column layout (sidebar + player, info panel hidden)
- **Mobile (sm)**: Single column with collapsible sidebar

## Accessibility

- All interactive elements keyboard accessible
- ARIA labels on buttons and controls
- Focus management for tab navigation
- Screen reader support for video player state
- Semantic HTML structure

## Future Enhancements

1. **Progress Persistence**: Connect to backend progress API
2. **Notes Backend**: Save/load notes from database
3. **Transcript Integration**: Display and search transcripts
4. **AI Tutor**: Connect chat interface to RAG backend
5. **Video Bookmarks**: Timestamp-based bookmarks
6. **Playback Analytics**: Track watch time and engagement
7. **Offline Mode**: Download videos for offline viewing
8. **Picture-in-Picture**: Floating video player