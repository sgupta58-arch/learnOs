import { useRouteError, isRouteErrorResponse, Link } from 'react-router-dom';

/**
 * Generic error page.
 *
 * Catches rendering errors and displays a user-friendly message.
 * Handles both route errors (404, 401, etc.) and unexpected errors.
 */
export function ErrorPage() {
  const error = useRouteError();

  const statusCode = isRouteErrorResponse(error) ? error.status : 500;
  const message = isRouteErrorResponse(error)
    ? error.statusText
    : 'An unexpected error occurred. Please try again.';

  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <h1 className="text-4xl font-bold">{statusCode}</h1>
      <p className="mt-2 text-muted-foreground">{message}</p>
      <Link
        to="/"
        className="mt-6 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
      >
        Go Home
      </Link>
    </div>
  );
}