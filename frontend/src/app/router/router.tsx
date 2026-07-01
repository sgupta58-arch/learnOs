import { createBrowserRouter } from 'react-router-dom';
import { lazy } from 'react';
import { PublicLayout } from '@/app/layouts/public-layout';
import { DashboardLayout } from '@/app/layouts/dashboard-layout';
import { ProtectedRoute } from '@/features/auth/components/protected-route';
import { PublicRoute } from '@/features/auth/components/public-route';
import { ErrorPage } from '@/features/error/pages/error-page';

/**
 * Lazy-loaded page components for route-level code splitting.
 */
const LoginPage = lazy(() =>
  import('@/features/auth/pages/login-page').then((m) => ({
    default: m.LoginPage,
  })),
);

const RegisterPage = lazy(() =>
  import('@/features/auth/pages/register-page').then((m) => ({
    default: m.RegisterPage,
  })),
);

const DashboardPage = lazy(() =>
  import('@/features/dashboard/pages/dashboard-page').then((m) => ({
    default: m.DashboardPage,
  })),
);

const PlaylistsPage = lazy(() =>
  import('@/features/playlist/pages/playlists-page').then((m) => ({
    default: m.PlaylistsPage,
  })),
);

const PlaylistDetailPage = lazy(() =>
  import('@/features/playlist/pages/playlist-detail-page').then((m) => ({
    default: m.PlaylistDetailPage,
  })),
);

const ImportPage = lazy(() =>
  import('@/features/playlist/pages/import-page').then((m) => ({
    default: m.ImportPage,
  })),
);

const TutorPage = lazy(() =>
  import('@/features/tutor/pages/tutor-page').then((m) => ({
    default: m.TutorPage,
  })),
);

const AnalyticsPage = lazy(() =>
  import('@/features/analytics/pages/analytics-page').then((m) => ({
    default: m.AnalyticsPage,
  })),
);

const ProgressPage = lazy(() =>
  import('@/features/progress/pages/progress-page').then((m) => ({
    default: m.ProgressPage,
  })),
);

const RevisionPage = lazy(() =>
  import('@/features/revision/pages/revision-page').then((m) => ({
    default: m.RevisionPage,
  })),
);

const FlashcardsPage = lazy(() =>
  import('@/features/flashcards/pages/flashcards-page').then((m) => ({
    default: m.FlashcardsPage,
  })),
);

const NotesPage = lazy(() =>
  import('@/features/notes/pages/notes-page').then((m) => ({
    default: m.NotesPage,
  })),
);

const KnowledgeGraphPage = lazy(() =>
  import('@/features/knowledge-graph/pages/knowledge-graph-page').then((m) => ({
    default: m.KnowledgeGraphPage,
  })),
);

const SettingsPage = lazy(() =>
  import('@/features/settings/pages/settings-page').then((m) => ({
    default: m.SettingsPage,
  })),
);

const NotFoundPage = lazy(() =>
  import('@/features/error/pages/not-found-page').then((m) => ({
    default: m.NotFoundPage,
  })),
);

/**
 * Centralized router configuration.
 *
 * Route protection:
 * - PublicRoute: redirects authenticated users to /dashboard
 * - ProtectedRoute: redirects unauthenticated users to /login
 *
 * Features:
 * - Layout routes for shared UI structure
 * - Nested routes for feature organization
 * - Lazy loading at the route level
 * - Error boundaries per route
 * - 404 catch-all route
 */
export const router = createBrowserRouter([
  {
    element: <PublicRoute />,
    children: [
      {
        element: <PublicLayout />,
        errorElement: <ErrorPage />,
        children: [
          {
            path: '/',
            element: <LoginPage />,
          },
          {
            path: '/login',
            element: <LoginPage />,
          },
          {
            path: '/register',
            element: <RegisterPage />,
          },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <DashboardLayout />,
        errorElement: <ErrorPage />,
        children: [
          {
            index: true,
            element: <DashboardPage />,
          },
          {
            path: 'playlists',
            element: <PlaylistsPage />,
          },
          {
            path: 'playlists/:playlistId',
            element: <PlaylistDetailPage />,
          },
          {
            path: 'import',
            element: <ImportPage />,
          },
          {
            path: 'tutor',
            element: <TutorPage />,
          },
          {
            path: 'analytics',
            element: <AnalyticsPage />,
          },
          {
            path: 'progress',
            element: <ProgressPage />,
          },
          {
            path: 'revision',
            element: <RevisionPage />,
          },
          {
            path: 'flashcards',
            element: <FlashcardsPage />,
          },
          {
            path: 'notes',
            element: <NotesPage />,
          },
          {
            path: 'knowledge-graph',
            element: <KnowledgeGraphPage />,
          },
          {
            path: 'settings',
            element: <SettingsPage />,
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);