import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/auth-context';

/**
 * Public route guard.
 *
 * Redirects authenticated users away from login/register pages
 * to the dashboard. This prevents logged-in users from seeing auth forms.
 */
export function PublicRoute() {
  const { isAuthenticated, isInitialized } = useAuth();

  if (!isInitialized) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}