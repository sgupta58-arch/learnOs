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
            path: '/dashboard',
            element: <DashboardPage />,
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