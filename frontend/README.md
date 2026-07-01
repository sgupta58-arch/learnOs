# LearnOS — Frontend

The frontend application for LearnOS, a Learning Operating System that transforms how people learn from video content.

## Phase Progress

| Phase | Focus | Status |
|-------|-------|--------|
| F1 | Project Foundation | ✅ Complete |
| F2 | Authentication | ✅ Complete |
| F3 | Dashboard & Playlists | ⬜ Next |
| F4 | Video Player & Progress | ⬜ Planned |
| F5+ | AI Features (Transcript, RAG, Tutor, etc.) | ⬜ Future |

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
│   │   │   └── ui/                  # shadcn/ui components (button, input, card, label)
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
│   │   ├── player/                  # Video player (Phase F3)
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

| Path | Component | Guard | Layout | Status |
|------|-----------|-------|--------|--------|
| `/` | LoginPage | PublicRoute | PublicLayout | ✅ Complete |
| `/login` | LoginPage | PublicRoute | PublicLayout | ✅ Complete |
| `/register` | RegisterPage | PublicRoute | PublicLayout | ✅ Complete |
| `/dashboard` | DashboardPage | ProtectedRoute | DashboardLayout | ⬜ Placeholder (Phase F3) |
| `*` | NotFoundPage | None | None | ✅ Complete |

All routes are lazy-loaded via `React.lazy()` for code splitting.

## Engineering Constraints

- **No Axios calls from components** — use the service layer
- **No business logic in pages** — extract to hooks and services
- **No `any` types** — strict TypeScript with `unknown` + narrowing
- **No inline styles** — use Tailwind utility classes
- **No cross-feature imports** — shared code via `common/` layer
- **No direct localStorage access** — use tokenStorage utility
- **Named exports** for components (default exports only for lazy-loaded pages)

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

**Phase F3 — Dashboard**

The next phase will implement the authenticated dashboard, application navigation, playlist listing, and establish the primary user workspace for LearnOS.

## License

MIT