# SKILLS.md — Engineering Competencies

This document defines the technical competencies expected of every engineer contributing to the LearnOS frontend. These are not optional preferences; they are the standards by which all code is evaluated.

---

## 1. React Architecture

### Expected Competency

Every engineer must understand React at an architectural level, not just the API surface.

### Standards

- **Component composition** over inheritance. Build UIs by composing small, focused components.
- **Lifting state up** when multiple children need shared state. Colocating state when only one component needs it.
- **Controlled vs uncontrolled components**. Know when to use each pattern. Prefer controlled components for form inputs.
- **React reconciliation**. Understand how keys work, why index-as-key is problematic, and how the virtual DOM diffing algorithm behaves.
- **Suspense and concurrent features**. Use `React.lazy` for code splitting. Understand how Suspense boundaries work.
- **Error boundaries**. Use class-based error boundaries (or a library) to catch rendering errors gracefully.
- **Portals** for modals, tooltips, and dropdowns that need to escape parent overflow/clipping contexts.
- **Refs** for DOM access when needed (focus management, media playback, measurements). Avoid refs for data flow.

### Anti-patterns to Avoid

- ❌ Using `useEffect` for data fetching (use TanStack Query)
- ❌ Prop drilling beyond 3 levels (use composition or context)
- ❌ Mutating props or state directly
- ❌ Creating components inside other components (breaks reconciliation)
- ❌ Overusing `useMemo` and `useCallback` without profiling

---

## 2. TypeScript Best Practices

### Expected Competency

Engineers must write TypeScript that leverages the type system for safety without fighting it.

### Standards

- **Strict mode** is enabled. No exceptions.
- **No `any`**. Use `unknown` and narrow with type guards, discriminated unions, or Zod validation.
- **Explicit return types** on all public functions, hooks, and components. This serves as documentation and catches errors at the definition site.
- **Prefer `interface`** for object shapes that may be extended (props, API responses, store state).
- **Prefer `type`** for unions, intersections, tuples, and utility types.
- **Use `as const`** for literal types, enum-like constants, and configuration objects.
- **Use `satisfies`** to validate that a value conforms to a type without widening.
- **Discriminated unions** for complex state (loading, error, success, empty).
- **Template literal types** for string patterns (route paths, event names).
- **Generic constraints** (`extends`) for type-safe abstractions.

### Example: Discriminated Union for Async State

```ts
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };
```

---

## 3. React Router

### Expected Competency

Engineers must be proficient with React Router v6+ for client-side routing.

### Standards

- **Route definitions** are centralized in a `routes/` directory.
- **Layout routes** for shared UI (headers, sidebars, footers).
- **Nested routes** for feature-specific sub-pages.
- **URL params** for dynamic routes (`/playlists/:playlistId`).
- **Search params** for filters, pagination, and search queries.
- **Loaders and actions** (when using React Router data APIs) for data loading before render.
- **Lazy loading** at the route level using `React.lazy`.
- **Error elements** per route for granular error handling.
- **Navigation guards** for protected routes (auth required).

### Route Structure

```tsx
// routes/index.tsx
const routes = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <RouteErrorBoundary />,
    children: [
      { index: true, element: <HomePage /> },
      {
        path: 'auth',
        children: [
          { path: 'login', element: <LoginPage /> },
          { path: 'register', element: <RegisterPage /> },
        ],
      },
      {
        path: 'playlists',
        element: <PlaylistsLayout />,
        children: [
          { index: true, element: <PlaylistsPage /> },
          { path: ':playlistId', element: <PlaylistDetailPage /> },
        ],
      },
    ],
  },
]);
```

---

## 4. TanStack Query

### Expected Competency

Engineers must use TanStack Query (React Query v5) as the primary data-fetching and server-state management solution.

### Standards

- **All server state** is managed through TanStack Query. No `useEffect` + `fetch` patterns.
- **Query keys** are organized using a factory pattern for consistency and easy invalidation.
- **Query functions** are defined in feature `api/` modules, not inline in components.
- **Mutations** use `useMutation` with `onSuccess` callbacks for cache invalidation.
- **Optimistic updates** for mutations where the user expects immediate feedback.
- **Stale time** and **cache time** are configured per query based on data volatility.
- **Error handling** is done at the query/mutation level, not in global interceptors.
- **Pagination** uses `keepPreviousData` for smooth transitions.
- **Infinite queries** for scroll-based pagination.
- **Prefetching** for anticipated user actions (hovering links, next page).

### Query Key Factory Pattern

```ts
export const playlistKeys = {
  all: ['playlists'] as const,
  lists: () => [...playlistKeys.all, 'list'] as const,
  list: (filters: PlaylistFilters) => [...playlistKeys.lists(), filters] as const,
  details: () => [...playlistKeys.all, 'detail'] as const,
  detail: (id: string) => [...playlistKeys.details(), id] as const,
  videos: (id: string) => [...playlistKeys.detail(id), 'videos'] as const,
};
```

---

## 5. Axios

### Expected Competency

Engineers must use Axios for HTTP communication with the backend API.

### Standards

- **Single Axios instance** configured with base URL, timeout, and default headers.
- **Request interceptor** attaches authentication tokens from secure storage.
- **Response interceptor** handles:
  - Token refresh on 401 responses
  - Global error normalization
  - Logging in development
- **AbortController** integration for request cancellation on unmount.
- **Type-safe responses** using Axios generic types.
- **Error handling** at the service layer, not in components.

### Axios Instance Pattern

```ts
import axios from 'axios';
import { getAccessToken, refreshTokens } from '@/shared/utils/auth';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await refreshTokens();
      // Retry the original request
      return api(error.config);
    }
    return Promise.reject(normalizeError(error));
  }
);
```

---

## 6. React Hook Form

### Expected Competency

Engineers must use React Hook Form for all form state management.

### Standards

- **All forms** use React Hook Form. No manual `useState` for form fields.
- **Validation** is handled by Zod schemas integrated via `@hookform/resolvers/zod`.
- **Field-level validation** for immediate feedback on blur.
- **Form-level validation** on submit.
- **Accessible error messages** linked to inputs via `aria-describedby` or `aria-invalid`.
- **Controlled components** for custom inputs (via `Controller`).
- **Uncontrolled components** for native HTML inputs (better performance).
- **Form submission** uses `handleSubmit` with proper TypeScript typing.

### Form Pattern

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const playlistSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  description: z.string().max(500).optional(),
  visibility: z.enum(['public', 'private']),
});

type PlaylistFormData = z.infer<typeof playlistSchema>;

export function PlaylistForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<PlaylistFormData>({
    resolver: zodResolver(playlistSchema),
  });

  const onSubmit = (data: PlaylistFormData) => {
    // mutation logic
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          {...register('name')}
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? 'name-error' : undefined}
        />
        {errors.name && (
          <p id="name-error" role="alert">{errors.name.message}</p>
        )}
      </div>
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Save Playlist'}
      </button>
    </form>
  );
}
```

---

## 7. Zod

### Expected Competency

Engineers must use Zod for runtime validation of data at the API boundary and for form validation.

### Standards

- **API response validation**: Validate API responses at the service layer to ensure type safety at runtime.
- **Form validation**: Define Zod schemas for all forms, integrated with React Hook Form.
- **Environment variables**: Validate `import.meta.env` variables with Zod at app startup.
- **Error messages**: Provide user-friendly error messages in validation schemas.
- **Type inference**: Use `z.infer<typeof schema>` to derive TypeScript types from schemas.
- **Refinement**: Use `.refine()` and `.superRefine()` for cross-field validation.

---

## 8. Tailwind CSS

### Expected Competency

Engineers must be proficient in utility-first CSS with Tailwind.

### Standards

- **Utility classes** for most styling. Avoid custom CSS unless necessary.
- **Design tokens** are configured in `tailwind.config.ts` (colors, spacing, typography, breakpoints).
- **Component classes** extracted using `@apply` only for truly repetitive patterns (and prefer shadcn/ui components).
- **Responsive design** using Tailwind breakpoint prefixes (`sm:`, `md:`, `lg:`, `xl:`).
- **Dark mode** using `dark:` variant (future-ready).
- **State variants** (`hover:`, `focus:`, `active:`, `disabled:`, `group-hover:`).
- **Animation** using Tailwind's built-in animation utilities.
- **No inline styles** (`style={{}}`) except for dynamic values that can't be expressed with classes.

---

## 9. shadcn/ui

### Expected Competency

Engineers must use shadcn/ui as the primary component library.

### Standards

- **Components are copied, not imported**. shadcn/ui components live in `src/shared/components/ui/` and are customized for the project.
- **Theme customization** is done through CSS variables in `globals.css`.
- **Composition over configuration**. shadcn/ui components are designed to be composed, not configured through massive prop objects.
- **Accessibility is built in**. shadcn/ui components follow WAI-ARIA standards. Do not override accessibility attributes without good reason.
- **Customize by forking**. If a shadcn/ui component doesn't meet requirements, fork it and customize rather than fighting the API.

---

## 10. Component Composition

### Expected Competency

Engineers must understand and apply component composition patterns.

### Standards

- **Compound components** for related components that share implicit state (e.g., `Select.Trigger`, `Select.Content`, `Select.Item`).
- **Slot pattern** using `children` and `render props` for flexible layouts.
- **Polymorphic components** using `as` prop (via `@radix-ui/react-slot` or `as-prop` pattern).
- **Higher-order components** (HOCs) only for cross-cutting concerns (withAuth, withErrorBoundary).
- **Render props** for sharing code between components with flexible rendering.
- **Container/Presentational pattern**: Container handles logic/data, presentational handles rendering.

---

## 11. Custom Hooks

### Expected Competency

Engineers must create custom hooks to encapsulate reusable stateful logic.

### Standards

- **Hooks are the primary abstraction** for reusable logic in React.
- **Each hook has a single responsibility**. If a hook does more than one thing, split it.
- **Hooks return objects** (not arrays) for named access to values and functions.
- **Hooks are fully typed** with explicit return types.
- **Hooks handle cleanup** via `useEffect` return functions.
- **Hooks are tested** with `@testing-library/react-hooks` or `renderHook`.

### Common Hook Patterns

```ts
// usePlaylist.ts
export function usePlaylist(id: string) {
  const query = useQuery({
    queryKey: playlistKeys.detail(id),
    queryFn: () => getPlaylist(id),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deletePlaylist(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: playlistKeys.lists() });
    },
  });

  return {
    playlist: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    deletePlaylist: deleteMutation.mutate,
    isDeleting: deleteMutation.isPending,
  };
}
```

---

## 12. State Management

### Expected Competency

Engineers must understand the state management stratification and choose the right tool for each type of state.

### Standards

| State Type | Tool | When to Use |
|-----------|------|-------------|
| Server state | TanStack Query | All data from the backend |
| URL state | React Router | Filters, pagination, search, selected items |
| Form state | React Hook Form | All form inputs |
| UI state (local) | `useState` | Component-specific UI state |
| UI state (shared) | React Context | Theme, sidebar, toast notifications |
| Global app state | Zustand | Auth user, app settings, cross-feature state |

### Rules

- **Don't put server state in client stores**. TanStack Query handles caching, synchronization, and invalidation.
- **Don't put URL state in React state**. URL params are the source of truth for navigation state.
- **Don't put form state in global stores**. React Hook Form manages form state locally.
- **Don't overuse Context**. Context triggers re-renders for all consumers. Use it sparingly.

---

## 13. API Layer Design

### Expected Competency

Engineers must design a clean API layer that separates concerns and provides type safety.

### Standards

- **API functions** are defined in feature `api/` directories.
- **Each API function** handles one endpoint and returns typed data.
- **Error handling** is done at the API layer, normalizing errors into a standard format.
- **Request/response types** are defined per endpoint.
- **Abort signals** are passed through for request cancellation.
- **No business logic** in API functions. They are pure data access functions.

### API Layer Structure

```
features/playlists/api/
├── client.ts          # Feature-specific Axios instance (if needed)
├── get-playlists.ts   # GET /api/v1/playlists
├── get-playlist.ts    # GET /api/v1/playlists/:id
├── create-playlist.ts # POST /api/v1/playlists
├── update-playlist.ts # PATCH /api/v1/playlists/:id
├── delete-playlist.ts # DELETE /api/v1/playlists/:id
└── types.ts           # Request/response types for playlist API
```

---

## 14. Performance Optimization

### Expected Competency

Engineers must proactively consider performance and know when and how to optimize.

### Standards

- **Measure before optimizing**. Use React DevTools Profiler, Lighthouse, and bundle analysis.
- **Code splitting** at route level with `React.lazy` and `Suspense`.
- **Lazy loading** for images, heavy components, and below-the-fold content.
- **Virtualization** for long lists (react-window or @tanstack/virtual).
- **Debouncing and throttling** for search inputs, resize handlers, and scroll events.
- **Memoization** with `useMemo` and `useCallback` only when profiling shows a benefit.
- **Bundle size awareness**. Monitor third-party imports. Use dynamic imports for large libraries.
- **Image optimization**: Use appropriate formats (WebP, AVIF), responsive sizes, and lazy loading.
- **Font optimization**: Subset fonts, use `font-display: swap`, preload critical fonts.

---

## 15. Accessibility

### Expected Competency

Engineers must build accessible interfaces as a default, not as an afterthought.

### Standards

- **WCAG 2.1 AA** compliance is the minimum standard.
- **Semantic HTML** is the foundation. Use native elements before ARIA.
- **Keyboard navigation**: All interactive elements must be reachable and operable via keyboard.
- **Focus management**: Manage focus for modals, dialogs, and single-page app navigation.
- **Screen reader support**: Use `aria-live` regions for dynamic content, `aria-label` for icon-only buttons.
- **Color contrast**: Meet WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text).
- **Reduced motion**: Respect `prefers-reduced-motion` for animations.
- **Testing**: Use axe-core or Lighthouse for automated accessibility testing.

---

## 16. Responsive Design

### Expected Competency

Engineers must build interfaces that work across mobile, tablet, and desktop.

### Standards

- **Mobile-first** approach. Start with the smallest screen and add complexity for larger screens.
- **Breakpoints** are defined in Tailwind config and used consistently.
- **Touch targets** are at least 44x44px on mobile.
- **Content reflow** without horizontal scroll at any viewport width.
- **Responsive typography** using clamp() or Tailwind's responsive text utilities.
- **Responsive images** using `srcSet` and `sizes` attributes.
- **Test on real devices** or browser DevTools device emulation.

---

## 17. Error Handling

### Expected Competency

Engineers must handle errors at every layer of the application.

### Standards

- **API errors**: Every query and mutation handles error states.
- **Form errors**: Every form displays validation errors inline.
- **Render errors**: Error boundaries catch rendering errors at the route and feature level.
- **Network errors**: Offline detection and retry logic.
- **User-friendly messages**: Map technical errors to human-readable messages.
- **Error recovery**: Provide retry buttons, refetch actions, and clear error dismissal.
- **Logging**: Log errors in development. In production, use a monitoring service.

---

## 18. Loading & Empty States

### Expected Competency

Engineers must design for every state a component can be in.

### Standards

- **Loading state**: Skeleton screens for content, spinners for actions.
- **Empty state**: Meaningful empty state with illustration, message, and call to action.
- **Error state**: Error message with retry action.
- **Success state**: Confirmation for mutations (toast, inline message).
- **Partial data**: Handle cases where some data is available but other data is loading.
- **Optimistic UI**: Show immediate feedback for mutations, with rollback on error.

---

## 19. Testing Mindset

### Expected Competency

Engineers must write tests that provide confidence in the code's correctness.

### Standards

- **Unit tests** for pure functions, utilities, and custom hooks.
- **Component tests** for UI components using `@testing-library/react`.
- **Integration tests** for feature workflows (user logs in, creates playlist, adds videos).
- **Accessibility tests** using `jest-axe` or `@testing-library/jest-dom` matchers.
- **Test behavior, not implementation**. Test what the user sees and does, not internal state.
- **Mock at the network level** using MSW (Mock Service Worker).
- **Coverage goals**: Aim for 80%+ coverage on critical paths. 100% coverage is not the goal; meaningful tests are.

---

## 20. Documentation Standards

### Expected Competency

Engineers must document code and architecture for future contributors.

### Standards

- **README.md** at the project root with setup instructions, architecture overview, and contribution guide.
- **JSDoc comments** for public APIs, complex functions, and non-obvious logic.
- **Component documentation** for shared components (props, usage examples, edge cases).
- **Architecture Decision Records (ADRs)** for significant technical decisions.
- **Inline comments** for complex algorithms, workarounds, and non-obvious behavior.
- **Self-documenting code**: Prefer clear naming over comments. Comments explain "why," not "what."

---

## 21. Refactoring Principles

### Expected Competency

Engineers must recognize when code needs refactoring and execute it safely.

### Standards

- **Boy Scout Rule**: Leave the codebase cleaner than you found it.
- **Small, safe refactors**: Extract functions, rename variables, simplify conditionals.
- **Large refactors**: Plan, communicate, and execute in stages. Never mix refactoring with feature work.
- **Test before refactoring**: Ensure existing tests pass. Add tests for untested code before refactoring.
- **One change at a time**: Refactor for one reason (performance, readability, extensibility). Don't combine concerns.
- **Know when to stop**: Not everything needs to be perfect. Pragmatic improvement is better than perfect paralysis.

---

*This document defines the technical bar for the LearnOS frontend. Every engineer is expected to meet these standards. If you see code that doesn't meet these standards, fix it or flag it. If you find a standard that needs updating, propose a change.*