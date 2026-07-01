# AGENTS.md — AI Coding Agent Guide

## Project Mission

LearnOS transforms how people learn from video content. We move beyond passive watching into an active, intelligent learning experience. Our mission is to build a Learning Operating System that understands what you watch, helps you retain it, and connects knowledge across your entire learning journey.

## Product Vision

LearnOS starts as a YouTube playlist manager but evolves into an AI-powered Learning Operating System. The product will eventually:

- Ingest video transcripts and generate embeddings
- Enable natural language queries over personal learning libraries
- Provide an AI tutor that understands your progress and gaps
- Build knowledge graphs connecting concepts across videos
- Offer adaptive revision planning based on spaced repetition
- Act as a personal learning assistant that grows with you

Every line of code written today should anticipate this future. We do not hack for a demo; we engineer for a product that will scale across these phases.

## Engineering Principles

### 1. Production Quality First
Every component, hook, utility, and page must be written as if it will be deployed to millions of users. There is no "prototype mode." Code must be robust, tested, accessible, and performant from the first commit.

### 2. Scalability by Design
Architect for growth. A feature implemented today should support ten times the data, ten times the users, and ten times the features without structural changes. Avoid premature optimization, but never write yourself into a corner.

### 3. Maintainability Over Cleverness
Write code that another engineer (or another AI agent) can read and modify six months from now. Prefer explicit, readable patterns over concise but cryptic ones. Favor composition over inheritance. Name things by what they do, not how they do it.

### 4. Consistency is King
Follow established patterns. If the codebase uses a certain approach for API calls, state management, error handling, or component structure, follow it. Consistency reduces cognitive load and makes the entire codebase predictable.

### 5. Accessibility is Non-Negotiable
LearnOS serves diverse learners. Some may have visual, auditory, motor, or cognitive disabilities. Every UI element must be accessible by default. Accessibility is not a feature branch; it is part of definition of done.

### 6. Performance is a Feature
Loading states, skeleton screens, optimized renders, code splitting, and lazy loading are not afterthoughts. They are integral to the user experience. Every component must consider its performance impact.

### 7. Data Integrity and Security
User data, learning progress, and personal information must be handled with care. Follow security best practices. Never expose sensitive data to the client. Validate all inputs. Sanitize all outputs.

## Frontend Architecture Philosophy

### Component-Driven Architecture
LearnOS follows a component-driven architecture using React. Every piece of UI is a component. Components are composed to build features. Features are composed to build pages. Pages are composed to build the application.

### Feature-Based Organization
The codebase is organized by features, not by technical concerns. Each feature is a self-contained module with its own components, hooks, types, and utilities. Shared code lives in a common layer. This structure scales because features can be developed, tested, and removed independently.

### Data-Fetching as a Declarative Concern
We use TanStack Query for all server state management. Data fetching is declarative, cached, and synchronized automatically. Mutations are optimistic where appropriate. Every API interaction has defined loading, error, and success states.

### Type Safety Across the Boundary
TypeScript types are shared between frontend and backend concepts. API request/response shapes are strictly typed. No `any` types escape into the application layer. Zod schemas validate runtime data at the API boundary.

### State Management Stratification
- **Server state**: TanStack Query (cached, synchronized)
- **Client state**: React Context (scoped, minimal)
- **Form state**: React Hook Form (local, validated)
- **Global UI state**: Zustand (sparingly, for truly global concerns)

## Feature-based Folder Structure

```
src/
├── features/
│   ├── auth/           # Authentication feature
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   ├── types/
│   │   └── index.ts
│   ├── playlists/      # Playlist feature
│   ├── videos/         # Video feature
│   ├── player/         # Video player feature
│   ├── progress/       # Learning progress feature
│   ├── search/         # Search feature (future)
│   └── tutor/          # AI Tutor feature (future)
├── shared/
│   ├── components/     # Reusable UI components
│   ├── hooks/          # Shared custom hooks
│   ├── utils/          # Utility functions
│   ├── api/            # Base API client
│   └── types/          # Shared TypeScript types
├── layouts/            # Page layouts
├── routes/             # Route definitions
├── stores/             # Global state stores
└── app/                # App entry point
```

### Rules for Feature Folders

1. **No cross-feature imports from `features/` to `features/`**. If two features share code, extract it to `shared/`.
2. **Each feature folder must have a public API** via its `index.ts`. Only export what other features (or pages) need.
3. **Feature-internal components, hooks, and utilities** are private to the feature. Don't export them if they're only used internally.
4. **Keep feature folders shallow**. Group logically, but don't nest beyond 3 levels.

## Component Design Rules

### Component Categories

1. **Page Components** — Route-level components that compose features and layouts. No business logic.
2. **Feature Components** — Components that implement a specific feature's UI. May contain feature logic.
3. **Shared Components** — Reusable UI primitives (buttons, inputs, modals, cards) from shadcn/ui and project-specific components.
4. **Layout Components** — Structural components (headers, sidebars, page shells).

### Component Rules

1. **One component per file**. Name the file after the component (PascalCase).
2. **Keep components focused**. If a component does more than one thing, split it.
3. **Prefer composition**. Build complex UIs by composing simple components.
4. **Props should be typed** with an interface exported from the component file.
5. **Default exports for page components** (for lazy loading). Named exports for everything else.
6. **No inline styles**. Use Tailwind utility classes or CSS modules.
7. **Every interactive element must be keyboard accessible**.

### Component File Template

```tsx
import { type FC } from 'react';
import { cn } from '@/shared/utils/cn';

interface VideoCardProps {
  title: string;
  duration: string;
  thumbnailUrl: string;
  className?: string;
}

export const VideoCard: FC<VideoCardProps> = ({
  title,
  duration,
  thumbnailUrl,
  className,
}) => {
  return (
    <div
      className={cn(
        'group relative overflow-hidden rounded-lg border',
        'transition-shadow hover:shadow-md',
        'focus-within:ring-2 focus-within:ring-ring',
        className
      )}
      role="article"
      aria-label={`Video: ${title}`}
    >
      <img
        src={thumbnailUrl}
        alt={`Thumbnail for ${title}`}
        className="aspect-video w-full object-cover"
        loading="lazy"
      />
      <div className="p-3">
        <h3 className="line-clamp-2 text-sm font-medium">{title}</h3>
        <p className="mt-1 text-xs text-muted-foreground">{duration}</p>
      </div>
    </div>
  );
};
```

## State Management Strategy

### Server State (TanStack Query)

- All data from the backend is server state.
- Use `useQuery` for reads, `useMutation` for writes.
- Define query keys as constants in a centralized file.
- Invalidate queries after successful mutations.
- Use optimistic updates for fast UIs where data integrity is assured.
- Always handle error states from queries.

```ts
// ✅ Good: Defined query key factory
export const playlistKeys = {
  all: ['playlists'] as const,
  detail: (id: string) => ['playlists', id] as const,
  videos: (id: string) => ['playlists', id, 'videos'] as const,
};
```

### Client State (React Context)

- Use React Context for state that is truly global but UI-specific (e.g., theme, sidebar state).
- Keep contexts small and focused. One context per concern.
- Provide default values that make sense for tests.

### Form State (React Hook Form + Zod)

- All forms use React Hook Form for state management.
- Validation schemas are defined with Zod.
- Error messages are user-friendly and accessible (linked to inputs via `aria-describedby`).

### Global State (Zustand)

- Use sparingly. Most state belongs in TanStack Query or React Context.
- Zustand is for truly global, cross-feature state (e.g., auth user, app settings).
- Keep stores flat. Avoid deeply nested store objects.

## API Communication Rules

### Axios Instance

- A single Axios instance is configured with base URL, interceptors, and default headers.
- Request interceptor attaches auth tokens.
- Response interceptor handles token refresh and global error handling.
- Response interceptor normalizes errors into a standard format.

### API Module Pattern

Each feature has an `api/` folder with functions that call the backend:

```ts
// features/playlists/api/get-playlists.ts
import { api } from '@/shared/api/client';
import type { Playlist } from '../types';

export async function getPlaylists(): Promise<Playlist[]> {
  const { data } = await api.get<Playlist[]>('/api/v1/playlists');
  return data;
}
```

### Error Handling

- Every API call must handle errors at the hook level.
- Network errors, server errors, and validation errors are distinct.
- Use TanStack Query's `onError` callback or error boundary for global handling.
- Show toast notifications for user-facing errors.

## Coding Standards

### TypeScript

- **Strict mode** enabled. No `strict: false`.
- **No `any`**. Use `unknown` if type is truly uncertain, then narrow.
- **Explicit return types** on public functions and React components.
- **Prefer `interface`** for object types that may be extended.
- **Prefer `type`** for unions, intersections, and utility types.
- **Use `as const`** for literal types and enums.
- **Use `satisfies` operator** to validate types without widening.
- **Avoid type assertions** (`as Type`). Use proper type narrowing instead.

### React

- **Functional components only**. No class components.
- **Hooks at the top level**. Never inside conditions, loops, or callbacks.
- **Custom hooks** for reusable stateful logic. Name them `use*`.
- **No `useEffect` for data fetching**. Use TanStack Query.
- **Use React.memo sparingly**. Profile first, then optimize.

## Naming Conventions

| Category | Convention | Example |
|----------|-----------|---------|
| Component files | PascalCase | `VideoCard.tsx` |
| Hook files | camelCase, `use` prefix | `usePlaylist.ts` |
| Utility files | camelCase | `formatDuration.ts` |
| Type files | camelCase | `playlist.ts` |
| API modules | camelCase | `getPlaylists.ts` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT` |
| CSS classes | kebab-case (Tailwind) | `bg-primary` |
| Folders | kebab-case | `playlist-detail` |
| Exported interfaces | PascalCase | `Playlist` |
| Exported types | PascalCase | `PlaylistStatus` |
| Props interfaces | Component name + `Props` | `VideoCardProps` |

## Accessibility Requirements

1. **All images must have `alt` text**. Decorative images use `alt=""`.
2. **All form inputs must have associated labels** via `htmlFor` or `aria-label`.
3. **All interactive elements must be keyboard accessible**. Support `Enter` and `Space` where applicable.
4. **Use semantic HTML** (`<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<header>`, `<footer>`).
5. **Heading hierarchy must be logical**. No skipping levels (h1 → h2 → h2, not h1 → h4).
6. **Color is not the only indicator**. Use icons, text, or patterns to convey state.
7. **Focus indicators must be visible**. Never remove `outline` without providing an alternative.
8. **ARIA attributes** are used when semantic HTML is insufficient.
9. **Live regions** (`aria-live`) for dynamically updating content.
10. **Screen reader only text** (`sr-only` class) for additional context.

## Performance Guidelines

1. **Code split at route level** using React.lazy and Suspense.
2. **Lazy load below-the-fold content** using Intersection Observer.
3. **Memoize expensive computations** with `useMemo`.
4. **Avoid unnecessary re-renders** by colocating state and using proper keys.
5. **Optimize images**: use appropriate sizes, lazy loading, and modern formats.
6. **Bundle analysis**: regularly check bundle size. Keep third-party dependencies lean.
7. **Virtual lists** for long scrollable content (e.g., video lists).
8. **Debounce search inputs** and rapid user interactions.
9. **Use `React.memo` on pure presentational components** rendered in lists.
10. **Preload critical resources** (fonts, hero images, API responses).

## Error Handling Standards

1. **Error boundaries** wrap each route and feature. Catch rendering errors gracefully.
2. **API errors** are classified: network, timeout, server, validation, auth.
3. **User-facing errors** use toast notifications (success, error, warning, info).
4. **Form errors** are displayed inline, linked to the relevant input.
5. **Global error boundary** catches unhandled errors and shows a fallback UI.
6. **Error recovery** is built in: retry buttons, refetch queries, revalidate forms.
7. **Log errors** to console in development. In production, log to a monitoring service.
8. **Never expose raw error messages** to users. Map to user-friendly messages.

## Code Review Checklist

### Functionality
- [ ] Does the code implement the requirements correctly?
- [ ] Are edge cases handled (empty states, error states, loading states)?
- [ ] Are all user flows accounted for?

### Code Quality
- [ ] Is the code readable and well-organized?
- [ ] Are functions and variables named clearly?
- [ ] Is there any dead code, commented code, or console.log statements?
- [ ] Are there any `any` types that should be properly typed?

### Performance
- [ ] Are there unnecessary re-renders? (Check key props, memoization)
- [ ] Are images and assets optimized?
- [ ] Is code splitting used appropriately?

### Accessibility
- [ ] Are all images alt-tagged?
- [ ] Are all forms accessible?
- [ ] Is keyboard navigation possible?
- [ ] Is the contrast ratio sufficient?

### Error Handling
- [ ] Are API errors handled?
- [ ] Are loading and error states rendered?
- [ ] Are form validations in place?

### Consistency
- [ ] Does the code follow established patterns?
- [ ] Are naming conventions followed?
- [ ] Is the folder structure respected?

### Testing
- [ ] Are there unit tests for logic?
- [ ] Are there component tests for UI?
- [ ] Do existing tests still pass?

## Development Workflow

### Branch Strategy
- `main` — production-ready code. Protected. Requires PR review.
- `develop` — integration branch. Feature branches merge here.
- `feat/<feature-name>` — feature branches. Branch off `develop`.
- `fix/<bug-description>` — bug fix branches. Branch off `develop`.
- `chore/<task>` — maintenance, tooling, documentation.

### Commit Convention
Use conventional commits:
```
feat: add playlist creation form
fix: correct video duration formatting
chore: update dependencies
docs: add API documentation
refactor: extract video card component
test: add playlist query tests
style: format code with prettier
```

### Pull Request Process
1. Create feature branch from `develop`.
2. Implement changes with conventional commits.
3. Write or update tests.
4. Run linting and type checking.
5. Create PR against `develop`.
6. Ensure CI passes.
7. Request review.
8. Address feedback.
9. Merge (squash merge recommended).

## Pull Request Expectations

1. **PRs must be focused**. One feature or fix per PR. No scope creep.
2. **PR description** must explain what changed and why. Include screenshots for UI changes.
3. **PRs under 400 lines** of diff. Large PRs should be split.
4. **All checks must pass** before merge: lint, type check, tests, build.
5. **At least one approval** required.
6. **No direct pushes to `main`** or `develop`.
7. **Self-review first** before requesting review.

## Definition of Done

A feature or task is done when:

- [ ] Code is implemented and follows project standards
- [ ] All TypeScript types are defined (no `any`)
- [ ] API integration is complete with loading, error, and success states
- [ ] Accessibility requirements are met
- [ ] Responsive design is implemented (mobile, tablet, desktop)
- [ ] Error handling is in place (API errors, form validation, edge cases)
- [ ] Unit tests are written and passing
- [ ] Component tests are written and passing (where applicable)
- [ ] No lint warnings or errors
- [ ] No TypeScript errors
- [ ] PR description is complete
- [ ] Code review has been completed and approved
- [ ] Feature has been manually tested in the browser

## Things to Avoid

1. **❌ Premature abstraction**. Don't extract shared components until there are three instances.
2. **❌ Over-engineering**. Build what's needed now, not what might be needed in six months.
3. **❌ Magic numbers and strings**. Use named constants.
4. **❌ Side effects in render functions**. Keep renders pure.
5. **❌ Mutating state directly**. Always use state setters.
6. **❌ Large useEffect dependencies**. Split effects if needed.
7. **❌ Nested ternaries**. Extract to functions or use early returns.
8. **❌ Long functions (over 50 lines)**. Extract smaller functions.
9. **❌ Deeply nested JSX (over 4 levels)**. Extract components.
10. **❌ `// eslint-disable-next-line`** without a justifying comment.
11. **❌ Console.log in production code**. Use proper logging.
12. **❌ Hardcoded strings**. Use constants or i18n (future).

## Future Expansion Guidelines

LearnOS will evolve through multiple phases. When writing code:

1. **Design APIs for extension**. Use patterns that can be extended without breaking changes.
2. **Keep features isolated**. A future AI Tutor feature should be addable without touching the Playlists feature.
3. **Build the shared layer first**. Common components, hooks, and utilities are investments that pay off as the app grows.
4. **Plan for data growth**. Ensure list views can paginate, search can be added, and queries can be optimized.
5. **Plan for feature flags**. Use environment variables or config to toggle features on/off.
6. **Keep state management choices reversible**. Don't lock the app into a pattern that can't be changed.
7. **Document architectural decisions**. When you choose one approach over another, document why. This helps future engineers understand the reasoning.

---

*This document is a living guide. It should evolve alongside the codebase as new patterns emerge and old ones become obsolete. Update it when you discover better practices or encounter limitations in the current approach.*