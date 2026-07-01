# LearnOS — Frontend

The frontend application for LearnOS, a Learning Operating System that transforms how people learn from video content.

## Phase Progress

| Phase | Focus | Status |
|-------|-------|--------|
| | F1 | Project Foundation | ✅ Complete |
| | F2 | Authentication | ✅ Complete |
| | F3 | Application Shell & Product Experience | ✅ Complete |
| | F4 | Video Learning Experience | ✅ Complete |
| | F5+ | AI Backend Integration | ⬜ Future |

## Phase F1: Project Foundation

This phase established the engineering foundation for the frontend. No business logic or feature implementation is included — only infrastructure, configuration, and architecture.

### What Was Built

| Deliverable | Status |
|------------|--------|
| Vite + React + TypeScript project initialization | ✅ |
| Strict TypeScript configuration | ✅ |
| Feature-based folder structure | ✅ |
| React Router with lazy-loaded routes | ✅ |
| Layout system (PublicLayout, DashboardLayout) | ✅ |
| AppProviders with QueryClientProvider | ✅ |
| TanStack Query infrastructure | ✅ |
| Axios client with interceptor placeholders | ✅ |
| Environment configuration module | ✅ |
| Tailwind CSS v4 + shadcn/ui CSS variables | ✅ |
| Global styles and theme foundation | ✅ |
| Shared utilities (cn, types, constants) | ✅ |
| Error pages (404, generic error) | ✅ |
| Updated README | ✅ |

## Phase F2: Authentication

This phase implemented a complete authentication system that integrates with the existing backend auth API. Users can register, log in, and maintain sessions with JWT tokens.

### What Was Built

| Deliverable | Status |
|------------|--------|
| Auth types matching backend schemas | ✅ |
| Zod validation schemas (login, register) | ✅ |
| Token storage utility (localStorage, centralized) | ✅ |
| Auth service (API functions using Axios) | ✅ |
| AuthContext + AuthProvider (React Context) | ✅ |
| ProtectedRoute component (redirects to /login) | ✅ |
| PublicRoute component (redirects to /dashboard) | ✅ |
| Axios interceptors (JWT attachment + 401 handling) | ✅ |
| Login page (React Hook Form + Zod + shadcn/ui) | ✅ |
| Register page (React Hook Form + Zod + shadcn/ui) | ✅ |
| Auth-aware router configuration | ✅ |
| TanStack Query mutations for auth actions | ✅ |
| Logout with state + cache cleanup | ✅ |
| Session restoration on app startup | ✅ |
| Success state on registration | ✅ |

### Authentication Architecture

```
User
  ↓
Login/Register Form
  ↓
React Hook Form
  ↓
Zod Validation
  ↓
useAuth hook (AuthContext)
  ↓
Auth Service (auth-service.ts)
  ↓
Axios Client (api-client.ts)
  ↓
Backend API
  ↓
JWT Token
  ↓
Token Storage (token-storage.ts)
  ↓
Auth Context (isAuthenticated = true)
  ↓
Protected Routes accessible
```

### Authentication Flow

**Login:**
1. User submits email + password via LoginPage form
2. React Hook Form validates with Zod schema
3. `useAuth().login()` calls `loginUser` from auth service
4. Axios POSTs form data (`username=email`, `password`) to `/auth/token`
5. Backend returns `{ access_token, token_type }`
6. Token is stored via `tokenStorage.set()` (localStorage)
7. AuthContext sets `isAuthenticated = true`
8. `ProtectedRoute` allows access to `/dashboard`
9. User is navigated to dashboard

**Registration:**
1. User submits full_name + email + password via RegisterPage form
2. React Hook Form validates with Zod schema (including password match)
3. `useAuth().register()` calls `registerUser` from auth service
4. Axios POSTs JSON to `/users`
5. Backend returns user data
6. Success page is shown, then user is redirected to login

**Session Restoration:**
1. App starts, `AuthProvider` mounts
2. `useEffect` reads stored token via `tokenStorage.get()`
3. If token exists → `isAuthenticated = true`, `isInitialized = true`
4. If no token → `isAuthenticated = false`, `isInitialized = true`
5. `ProtectedRoute` and `PublicRoute` wait for `isInitialized` before deciding
6. Prevents flash of login page on refresh

**Logout:**
1. `useAuth().logout()` is called
2. Token is removed from storage via `tokenStorage.remove()`
3. TanStack Query cache is cleared via `queryClient.clear()`
4. AuthContext sets `isAuthenticated = false`
5. `ProtectedRoute` redirects to `/login`

**JWT Lifecycle:**
- Token is stored in localStorage under key `learnos_access_token`
- Axios request interceptor reads token from storage and attaches `Authorization: Bearer <token>` header
- Axios response interceptor catches 401 responses, removes token, redirects to `/login`
- Token refresh is not implemented (backend may support in future)

### Route Protection

| Route | Guard | Behavior |
|-------|-------|----------|
| `/`, `/login` | PublicRoute | Redirects authenticated users to `/dashboard` |
| `/register` | PublicRoute | Redirects authenticated users to `/dashboard` |
| `/dashboard` | ProtectedRoute | Redirects unauthenticated users to `/login` |

## Phase F5: Playlist Import & Learning Entry Flow

This phase completes the first end-to-end learning workflow. Users can now import YouTube playlists and seamlessly transition from dashboard to learning workspace. This is the first point where LearnOS becomes a genuinely usable product.

### What Was Built

| Deliverable | Status |
||------------|--------|
| YouTube URL validation utility | ✅ |
| Enhanced import page with success/error states | ✅ |
| Real-time URL validation with inline feedback | ✅ |
| Success state with "Start Learning" CTA | ✅ |
| Playlist detail page with "Start Learning" banner | ✅ |
| Dashboard integration (import CTA, playlist cards) | ✅ |
| React Query invalidation after import | ✅ |
| Automatic navigation after successful import | ✅ |
| Empty state for new users | ✅ |
| Continue Learning card (existing, enhanced) | ✅ |

### Primary User Journey (MVP)

```
Register
  ↓
Login
  ↓
Dashboard
  ↓
Import Playlist
  ↓
Paste YouTube Playlist URL
  ↓
Validate URL (real-time)
  ↓
Import Playlist (API call)
  ↓
See Progress (loading state)
  ↓
Playlist Imported Successfully
  ↓
Open Playlist / Start Learning
  ↓
Learning Workspace
  ↓
Start Learning
```

### Import Flow Architecture

```
ImportPage
├── URL Input with real-time validation
│   ├── Validates YouTube domain
│   ├── Extracts playlist ID
│   └── Shows inline errors
├── Import Button (disabled until valid)
├── Loading State (spinner + "Importing...")
├── Success State
│   ├── Playlist title
│   ├── Video count
│   ├── "Start Learning" button
│   ├── "View Playlist" button
│   └── "Import Another" button
└── Error State (user-friendly messages)
```

### Backend Integration

**Import endpoint:**
- `POST /playlists/import/youtube?source_url={url}`
- Request: Query parameter with YouTube playlist URL
- Response: `{ playlist_id, title, videos_imported }`
- Authentication: JWT token required
- Error handling: Invalid URL, private playlist, API failures

**Query invalidation strategy:**
- After successful import, invalidate `['playlists']` query
- Invalidate `['continue-learning']` query
- Dashboard automatically refreshes to show new playlist

### URL Validation

Supported formats:
- `https://www.youtube.com/playlist?list=PLxxx`
- `https://youtube.com/playlist?list=PLxxx`
- `https://m.youtube.com/playlist?list=PLxxx`
- `https://youtu.be/PLxxx`

Validation rules:
- Must be from youtube.com or youtu.be domain
- Must contain `list` query parameter
- Playlist ID must start with valid prefix (PL, OL, UU, FL, RD, LL)
- Real-time validation as user types (after 10 characters)

### Dashboard Integration

**Empty state (no playlists):**
- Shows "No playlists yet" message
- Prominent "Import Your First Playlist" button
- Helpful text explaining next steps

**With playlists:**
- Recent playlists section shows last 5 playlists
- Each playlist is clickable (navigates to detail page)
- Quick Actions card has "Import Playlist" as primary action
- Continue Learning card shows resume options

**Playlist detail page:**
- "Start Learning" banner at top (if videos exist)
- Shows first video title and duration
- Prominent "Start Learning" button
- Navigates to workspace with first video

### Accessibility

- All form inputs have associated labels
- Error messages linked via `aria-describedby`
- `aria-invalid` on inputs with errors
- `role="alert"` on error messages
- Keyboard navigation supported
- Focus management after import

### Engineering Rules Applied

- ✅ No Axios calls from components (uses service layer)
- ✅ No business logic in pages (extracted to hooks/services)
- ✅ No `any` types (strict TypeScript)
- ✅ No inline styles (Tailwind utility classes)
- ✅ No cross-feature imports (shared code via `common/`)
- ✅ Named exports for components
- ✅ No mock data in components

## Phase F3: Application Shell & Product Experience

This phase built the complete application shell and all product pages. LearnOS is designed as a full SaaS application, not just a frontend for backend APIs. Pages without backend support have polished placeholder experiences ready for future integration.

### What Was Built

| Deliverable | Status |
|------------|--------|
| Responsive DashboardLayout with collapsible sidebar | ✅ |
| Top navigation with search/notification/user placeholders | ✅ |
| Dashboard page with stat widgets and recent playlists | ✅ |
| Playlists page (backend-connected via TanStack Query) | ✅ |
| Playlist detail page with video list | ✅ |
| YouTube playlist import page (backend-connected) | ✅ |
| AI Tutor page (placeholder UI, future-ready) | ✅ |
| Analytics page (mock data, chart placeholders) | ✅ |
| Progress page (mock data, stat cards) | ✅ |
| Revision Planner page (mock data, calendar placeholder) | ✅ |
| Flashcards page (mock data, card UI placeholder) | ✅ |
| Notes page (mock data, editor placeholder) | ✅ |
| Knowledge Graph page (mock data, viz placeholder) | ✅ |
| Settings page (profile, logout functional) | ✅ |
| All routes lazy-loaded with React.lazy() | ✅ |
| Reusable components (PageHeader, StatCard, EmptyState) | ✅ |
| Loading, error, and empty states for all pages | ✅ |
| Responsive sidebar (desktop expand/collapse, mobile drawer) | ✅ |
| Active route highlighting in sidebar | ✅ |
| Logout from sidebar and settings | ✅ |

### Application Shell Architecture

```
DashboardLayout
├── Sidebar (collapsible, responsive)
│   ├── Navigation items (11 pages)
│   └── Logout button
├── Top Navigation
│   ├── Page title with icon
│   ├── Search placeholder
│   ├── Notifications placeholder
│   └── User profile placeholder
└── Main Content Area
    └── Outlet (lazy-loaded feature pages)
```

### Navigation Structure

| Page | Route | Backend | Status |
|------|-------|---------|--------|
| Dashboard | `/dashboard` | Partial | ✅ Live |
| Playlists | `/dashboard/playlists` | Yes | ✅ Live |
| Playlist Detail | `/dashboard/playlists/:id` | Yes | ✅ Live |
| Import Playlist | `/dashboard/import` | Yes | ✅ Live |
| AI Tutor | `/dashboard/tutor` | No | ✅ Placeholder |
| Analytics | `/dashboard/analytics` | No | ✅ Placeholder |
| Progress | `/dashboard/progress` | No | ✅ Placeholder |
| Revision Planner | `/dashboard/revision` | No | ✅ Placeholder |
| Flashcards | `/dashboard/flashcards` | No | ✅ Placeholder |
| Notes | `/dashboard/notes` | No | ✅ Placeholder |
| Knowledge Graph | `/dashboard/knowledge-graph` | No | ✅ Placeholder |
| Settings | `/dashboard/settings` | Partial | ✅ Live |

### Backend Integration Strategy

**Currently connected:**
- `GET /playlists` — List user playlists
- `GET /playlists/{id}` — Get playlist detail
- `DELETE /playlists/{id}` — Delete playlist
- `POST /playlists/import/youtube` — Import YouTube playlist
- `GET /videos?playlist_id={id}` — List playlist videos

**Future integration (no UI changes needed):**
- Progress tracking — replace mock data with `GET /users/me/progress`
- Analytics — replace mock data with analytics endpoints
- AI Tutor — connect chat interface to AI backend
- Revision — connect to spaced repetition engine
- Flashcards — connect to flashcard generation service
- Notes — connect to notes CRUD API
- Knowledge Graph — connect to graph visualization backend

### Mock Data Strategy

Future-only pages use dedicated placeholder UIs with:
- Clear "coming in a future phase" messaging
- Disabled inputs/buttons showing intended UX
- Stat cards with zero values
- Empty states explaining what the feature will do
- No fake network requests or hardcoded mock data in components

This makes replacing placeholders with real API data straightforward — no component redesign needed.

### Responsive Design

- **Desktop**: Full sidebar with labels, expand/collapse toggle
- **Tablet**: Collapsible sidebar, full content area
- **Mobile**: Hidden sidebar with hamburger menu, slide-out drawer

## Phase F4: Video Learning Experience

This phase transforms LearnOS from a playlist manager into an actual learning platform. Users can now watch videos, track progress, take notes, and navigate playlists in a professional learning workspace.

### What Was Built

| Deliverable | Status |
||------------|--------|
| Learning feature structure (types, services, hooks, components, pages) | ✅ |
| Video player with YouTube embed | ✅ |
| Playlist sidebar with video navigation | ✅ |
| Learning controls (previous/next, speed, autoplay) | ✅ |
| Notes panel (UI only, backend future) | ✅ |
| Resources panel (placeholder) | ✅ |
| Continue Learning dashboard widget | ✅ |
| Learning workspace page route | ✅ |
| Keyboard shortcuts (space, Ctrl+arrows, Ctrl+B) | ✅ |
| Responsive three-column layout | ✅ |
| Progress indicators (not started, in progress, completed) | ✅ |
| Video navigation from playlist detail | ✅ |

### Learning Workspace Architecture

```
WorkspacePage
├── Top Bar (playlist title, sidebar toggle, exit)
├── Main Content
│   ├── PlaylistSidebar (collapsible)
│   │   ├── Playlist header (title, video count)
│   │   └── Video list with progress indicators
│   ├── Center Column
│   │   ├── VideoPlayer (YouTube embed)
│   │   └── LearningControls (navigation, speed, autoplay)
│   └── Right Panel (desktop only)
│       ├── Tabs (Overview, Transcript, Notes, Tutor, Resources)
│       └── Tab Content
│           ├── Overview (video details)
│           ├── Notes (editor UI)
│           ├── Resources (placeholder)
│           ├── Transcript (placeholder)
│           └── Tutor (placeholder)
└── Keyboard Shortcuts
    ├── Space: Play/Pause
    ├── Ctrl+Right: Next video
    ├── Ctrl+Left: Previous video
    └── Ctrl+B: Toggle sidebar
```

### User Journey

```
Login
  ↓
Dashboard
  ↓
Continue Learning (resume video)
  ↓
Playlists
  ↓
Select Playlist
  ↓
Playlist Detail
  ↓
Click Play button
  ↓
Learning Workspace
  ↓
Watch Video
  ↓
Track Progress
  ↓
Next Video (autoplay)
  ↓
Continue Learning
```

### Backend Integration

**Currently connected:**
- Playlist/video fetching (via playlist service)
- Continue learning data (via learning service)

**Future integration:**
- Video progress persistence
- Notes CRUD
- Transcript fetching
- AI Tutor chat

### Responsive Design

- **Desktop (lg+)**: Three-column layout (sidebar + player + info panel)
- **Tablet (md)**: Two-column layout (sidebar + player, info panel hidden)
- **Mobile (sm)**: Single column with collapsible sidebar

### Learning Workspace Architecture

```
WorkspacePage
├── Top Bar (playlist title, sidebar toggle, exit)
├── Main Content
│   ├── PlaylistSidebar (collapsible)
│   │   ├── Playlist header (title, video count)
│   │   └── Video list with progress indicators
│   ├── Center Column
│   │   ├── VideoPlayer (YouTube embed)
│   │   └── LearningControls (navigation, speed, autoplay)
│   └── Right Panel (desktop only)
│       ├── Tabs (Overview, Transcript, Notes, Tutor, Resources)
│       └── Tab Content
│           ├── Overview (video details)
│           ├── Notes (editor UI)
│           ├── Resources (placeholder)
│           ├── Transcript (placeholder)
│           └── Tutor (placeholder)
└── Keyboard Shortcuts
    ├── Space: Play/Pause
    ├── Ctrl+Right: Next video
    ├── Ctrl+Left: Previous video
    └── Ctrl+B: Toggle sidebar
```

### User Journey

```
Login
  ↓
Dashboard
  ↓
Continue Learning (resume video)
  ↓
Playlists
  ↓
Select Playlist
  ↓
Playlist Detail
  ↓
Click Play button
  ↓
Learning Workspace
  ↓
Watch Video
  ↓
Track Progress
  ↓
Next Video (autoplay)
  ↓
Continue Learning
```

### Backend Integration

**Currently connected:**
- Playlist/video fetching (via playlist service)
- Continue learning data (via learning service)

**Future integration:**
- Video progress persistence
- Notes CRUD
- Transcript fetching
- AI Tutor chat

### Responsive Design

- **Desktop (lg+)**: Three-column layout (sidebar + player + info panel)
- **Tablet (md)**: Two-column layout (sidebar + player, info panel hidden)
- **Mobile (sm)**: Single column with collapsible sidebar

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| **React 19+** | UI library |
| **TypeScript 6** (strict mode) | Type safety with zero `any` |
| **Vite 8** | Build tool and dev server |
| **React Router v7** | Client-side routing with lazy loading |
| **TanStack Query v5** | Server state management |
| **Axios** | HTTP client with interceptors |
| **React Hook Form** | Form state management |
| **Zod** | Schema validation |
| **Tailwind CSS v4** | Utility-first styling with CSS variables |
| **shadcn/ui** | Accessible component primitives via CSS variables |
| **clsx + tailwind-merge** | Conditional class merging |
| **lucide-react** | Icon library |

## Architecture

### Data Flow Architecture

```
Page Component
    ↓
Feature Component
    ↓
Custom Hook / Context
    ↓
Service Layer (TanStack Query / API functions)
    ↓
Axios Client (api-client.ts)
    ↓
Backend API
```

### State Management Stratification

| State Type | Tool | Scope |
|-----------|------|-------|
| Server state | TanStack Query | Global, cached |
| Auth state | React Context (AuthProvider) | Global |
| Form state | React Hook Form | Local to form |
| UI state (local) | useState | Component |
| URL state | React Router | Route params |

### Project Structure

```
frontend/
├── public/                          # Static assets
├── src/
│   ├── app/                         # Application entry point
│   │   ├── providers/               # Global providers (QueryClient, Auth)
│   │   ├── layouts/                 # Page layouts (PublicLayout, DashboardLayout)
│   │   ├── router/                  # Centralized router configuration
│   │   └── App.tsx                  # Root component
│   ├── assets/                      # Static assets (images, icons)
│   ├── common/                      # Shared code across features
│   │   ├── components/              # Reusable UI components
│   │   │   ├── ui/                  # shadcn/ui components
│   │   │   ├── page-header.tsx      # Reusable page header
│   │   │   ├── stat-card.tsx        # Dashboard stat card
│   │   │   ├── empty-state.tsx      # Empty state component
│   │   │   └── card.tsx             # Card component
│   │   ├── hooks/                   # Shared custom hooks
│   │   ├── utils/                   # Utility functions (cn, etc.)
│   │   ├── constants/               # Application constants
│   │   └── types/                   # Shared TypeScript types
│   ├── config/                      # Configuration (env, app settings)
│   │   └── env.ts                   # Environment variable module
│   ├── features/                    # Feature-based modules
│   │   ├── auth/                    # Authentication (Phase F2)
│   │   │   ├── components/          # ProtectedRoute, PublicRoute
│   │   │   ├── context/             # AuthContext, AuthProvider, useAuth
│   │   │   ├── hooks/               # Auth hooks
│   │   │   ├── pages/               # LoginPage, RegisterPage
│   │   │   ├── schemas/             # Zod validation schemas
│   │   │   ├── services/            # Auth service (login, register)
│   │   │   ├── types/               # Auth TypeScript types
│   │   │   └── utils/               # Token storage utility
│   │   ├── dashboard/               # Dashboard (Phase F3)
│   │   ├── playlist/                # Playlist management (Phase F3)
│   │   │   ├── pages/               # PlaylistsPage, PlaylistDetailPage, ImportPage
│   │   │   ├── services/            # Playlist service (API functions)
│   │   │   └── types/               # Playlist TypeScript types
│   │   ├── learning/                # Learning workspace (Phase F4) ⭐ NEW
│   │   │   ├── components/          # VideoPlayer, PlaylistSidebar, etc.
│   │   │   ├── pages/               # WorkspacePage
│   │   │   ├── hooks/               # useLearningWorkspace
│   │   │   ├── services/            # Learning service (progress API)
│   │   │   ├── types/               # Learning TypeScript types
│   │   │   └── index.ts             # Public API exports
│   │   ├── tutor/                   # AI Tutor (Phase F3, placeholder)
│   │   ├── analytics/               # Analytics (Phase F3, placeholder)
│   │   ├── progress/                # Progress (Phase F3, placeholder)
│   │   ├── revision/                # Revision Planner (Phase F3, placeholder)
│   │   ├── flashcards/              # Flashcards (Phase F3, placeholder)
│   │   ├── notes/                   # Notes (Phase F3, placeholder)
│   │   ├── knowledge-graph/         # Knowledge Graph (Phase F3, placeholder)
│   │   ├── settings/                # Settings (Phase F3)
│   │   └── error/                   # Error pages (404, error boundary)
│   ├── lib/                         # Third-party library configurations
│   │   ├── query-client.ts          # TanStack Query client config
│   │   └── utils.ts                 # shadcn/ui cn utility
│   ├── services/                    # Service layer
│   │   └── api-client.ts            # Axios client with JWT interceptors
│   ├── styles/                      # Global styles
│   │   └── globals.css              # Tailwind import, CSS variables, theme
│   ├── main.tsx                     # Application entry point
│   └── vite-env.d.ts                # Vite environment type declarations
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.app.json                # Strict TypeScript config
├── tsconfig.node.json
├── vite.config.ts                   # Vite + Tailwind + path aliases
├── components.json                  # shadcn/ui configuration
├── .env.example                     # Environment variable template
├── AGENTS.md                        # AI coding agent guide
├── SKILLS.md                        # Engineering competencies
├── END_GOAL.md                      # Long-term product vision
└── README.md                        # This file
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm 9+ or pnpm 8+
- Backend API running (see `backend/README.md` in project root)

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Edit .env.local with your configuration:
# VITE_API_URL=http://localhost:8000/api/v1
```

### Running Against Backend

```bash
# 1. Start the backend (from project root)
docker compose up -d

# 2. Start the frontend dev server
cd frontend
npm run dev

# 3. Open http://localhost:5173
# 4. Register a new account
# 5. Log in with your credentials
# 6. You will be redirected to the dashboard
```

### Development

```bash
# Start development server (default: http://localhost:5173)
npm run dev
```

### Build

```bash
# TypeScript check + production build
npm run build

# Preview production build
npm run preview
```

## Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start Vite dev server |
| `npm run build` | TypeScript check + production Vite build |
| `npm run preview` | Preview production build |
| `npm run lint` | ESLint check |

## Routes

| Path | Component | Guard | Layout | Backend | Status |
|------|-----------|-------|--------|---------|--------|
| `/` | LoginPage | PublicRoute | PublicLayout | No | ✅ Complete |
| `/login` | LoginPage | PublicRoute | PublicLayout | No | ✅ Complete |
| `/register` | RegisterPage | PublicRoute | PublicLayout | No | ✅ Complete |
| `/dashboard` | DashboardPage | ProtectedRoute | DashboardLayout | Partial | ✅ Complete |
| `/dashboard/playlists` | PlaylistsPage | ProtectedRoute | DashboardLayout | Yes | ✅ Live |
| `/dashboard/playlists/:id` | PlaylistDetailPage | ProtectedRoute | DashboardLayout | Yes | ✅ Live |
| `/dashboard/workspace/:playlistId/:videoId` | WorkspacePage | ProtectedRoute | DashboardLayout | Partial | ✅ Complete |
| `/dashboard/import` | ImportPage | ProtectedRoute | DashboardLayout | Yes | ✅ Live |
| `/dashboard/tutor` | TutorPage | ProtectedRoute | DashboardLayout | No | ✅ Placeholder |
| `/dashboard/analytics` | AnalyticsPage | ProtectedRoute | DashboardLayout | No | ✅ Placeholder |
| `/dashboard/progress` | ProgressPage | ProtectedRoute | DashboardLayout | No | ✅ Placeholder |
| `/dashboard/revision` | RevisionPage | ProtectedRoute | DashboardLayout | No | ✅ Placeholder |
| `/dashboard/flashcards` | FlashcardsPage | ProtectedRoute | DashboardLayout | No | ✅ Placeholder |
| `/dashboard/notes` | NotesPage | ProtectedRoute | DashboardLayout | No | ✅ Placeholder |
| `/dashboard/knowledge-graph` | KnowledgeGraphPage | ProtectedRoute | DashboardLayout | No | ✅ Placeholder |
| `/dashboard/settings` | SettingsPage | ProtectedRoute | DashboardLayout | Partial | ✅ Complete |
| `*` | NotFoundPage | None | None | No | ✅ Complete |

All routes are lazy-loaded via `React.lazy()` for code splitting.

## Engineering Constraints

- **No Axios calls from components** — use the service layer
- **No business logic in pages** — extract to hooks and services
- **No `any` types** — strict TypeScript with `unknown` + narrowing
- **No inline styles** — use Tailwind utility classes
- **No cross-feature imports** — shared code via `common/` layer
- **No direct localStorage access** — use tokenStorage utility
- **Named exports** for components (default exports only for lazy-loaded pages)
- **No mock data inside components** — use dedicated mock modules when needed

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `VITE_API_URL` | Backend API base URL | Yes | `http://localhost:8000/api/v1` |
| `VITE_APP_NAME` | Application name | No | `LearnOS` |

## Key Architectural Documents

- **[AGENTS.md](./AGENTS.md)** — Comprehensive guide for AI coding agents and human developers covering engineering principles, architecture philosophy, component design, state management, coding standards, and development workflow.
- **[SKILLS.md](./SKILLS.md)** — Defines the 21 technical competencies expected of contributors.
- **[END_GOAL.md](./END_GOAL.md)** — Long-term product vision from MVP through 11 planned phases.

## Next Phase

**Phase F5 — Learning Intelligence**

The next phase will add AI-powered features:
- Transcript pipeline and display
- AI Tutor integration with RAG backend
- Progress analytics with real data
- Knowledge graph visualization

## License

MIT