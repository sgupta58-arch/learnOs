import { RouterProvider } from 'react-router-dom';
import { AppProviders } from '@/app/providers/app-providers';
import { router } from '@/app/router/router';

/**
 * Root application component.
 *
 * Composes global providers and routing.
 * React Router's createBrowserRouter handles lazy loading internally.
 */
export function App() {
  return (
    <AppProviders>
      <RouterProvider router={router} />
    </AppProviders>
  );
}