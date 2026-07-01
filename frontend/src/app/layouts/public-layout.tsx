import { Outlet } from 'react-router-dom';

/**
 * Public layout for unauthenticated pages (login, register, landing).
 *
 * Provides a minimal wrapper with no sidebar or authentication requirements.
 * Can be extended with a public header/footer in future phases.
 */
export function PublicLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}