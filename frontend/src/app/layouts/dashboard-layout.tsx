import { Outlet } from 'react-router-dom';

/**
 * Dashboard layout for authenticated pages.
 *
 * Provides the main application shell with navigation structure.
 * Placeholder for future sidebar, header, and user menu components.
 */
export function DashboardLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b">
        <div className="container mx-auto flex h-14 items-center px-4">
          <span className="text-lg font-semibold">LearnOS</span>
        </div>
      </header>
      <div className="flex flex-1">
        <aside className="hidden w-64 border-r md:block">
          <nav className="space-y-1 p-4">
            <span className="text-sm text-muted-foreground">
              Navigation placeholder
            </span>
          </nav>
        </aside>
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}