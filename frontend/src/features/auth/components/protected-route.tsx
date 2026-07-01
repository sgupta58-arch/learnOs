import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/auth-context';

/**
 * Protected route guard.
 *
 * Redirects unauthenticated users to the login page.
 * Shows a loading state while auth is being initialized
 * to prevent flashing the login page on refresh.
 */
export function ProtectedRoute() {
  const { isAuthenticated, isInitialized } = useAuth();

  // Wait for session restoration to complete before deciding
  if (!isInitialized) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}