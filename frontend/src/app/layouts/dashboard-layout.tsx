import { useState } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/context/auth-context';
import { cn } from '@/common/utils/cn';
import {
  LayoutDashboard,
  ListVideo,
  Upload,
  Bot,
  BarChart3,
  TrendingUp,
  Calendar,
  Sparkles,
  StickyNote,
  Share2,
  Settings,
  Menu,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Bell,
  Search,
  User,
} from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon: typeof LayoutDashboard;
}

const navigation: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Playlists', href: '/dashboard/playlists', icon: ListVideo },
  { label: 'Import Playlist', href: '/dashboard/import', icon: Upload },
  { label: 'AI Tutor', href: '/dashboard/tutor', icon: Bot },
  { label: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
  { label: 'Progress', href: '/dashboard/progress', icon: TrendingUp },
  { label: 'Revision Planner', href: '/dashboard/revision', icon: Calendar },
  { label: 'Flashcards', href: '/dashboard/flashcards', icon: Sparkles },
  { label: 'Notes', href: '/dashboard/notes', icon: StickyNote },
  { label: 'Knowledge Graph', href: '/dashboard/knowledge-graph', icon: Share2 },
  { label: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export function DashboardLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const currentPage = navigation.find((item) => {
    if (item.href === '/dashboard') return location.pathname === '/dashboard';
    return location.pathname.startsWith(item.href);
  });

  return (
    <div className="flex min-h-screen bg-background">
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex flex-col border-r bg-card transition-all duration-200 md:static',
          sidebarOpen ? 'w-60' : 'w-16',
          mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
        )}
      >
        {/* Sidebar header */}
        <div className={cn('flex h-14 items-center border-b px-4', sidebarOpen ? 'justify-between' : 'justify-center')}>
          {sidebarOpen ? (
            <>
              <Link to="/dashboard" className="text-lg font-bold tracking-tight">
                LearnOS
              </Link>
              <button
                onClick={() => setSidebarOpen(false)}
                className="rounded-md p-1 text-muted-foreground hover:bg-muted"
              >
                <ChevronLeft className="size-4" />
              </button>
            </>
          ) : (
            <button
              onClick={() => setSidebarOpen(true)}
              className="rounded-md p-1 text-muted-foreground hover:bg-muted"
            >
              <ChevronRight className="size-4" />
            </button>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 overflow-y-auto p-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = item.href === '/dashboard'
              ? location.pathname === '/dashboard'
              : location.pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                to={item.href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                  !sidebarOpen && 'justify-center px-2',
                )}
                title={!sidebarOpen ? item.label : undefined}
              >
                <Icon className="size-4 shrink-0" />
                {sidebarOpen && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Sidebar footer */}
        <div className="border-t p-2">
          <button
            onClick={handleLogout}
            className={cn(
              'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground transition-colors',
              !sidebarOpen && 'justify-center px-2',
            )}
            title={!sidebarOpen ? 'Logout' : undefined}
          >
            <LogOut className="size-4 shrink-0" />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main area */}
      <div className="flex flex-1 flex-col">
        {/* Top navigation */}
        <header className="flex h-14 items-center gap-4 border-b bg-card px-4">
          <button
            onClick={() => setMobileOpen(true)}
            className="rounded-md p-1 text-muted-foreground hover:bg-muted md:hidden"
          >
            <Menu className="size-5" />
          </button>

          <div className="flex items-center gap-2">
            {currentPage && (
              <>
                <currentPage.icon className="size-5 text-muted-foreground" />
                <h2 className="text-sm font-medium">{currentPage.label}</h2>
              </>
            )}
          </div>

          <div className="flex-1" />

          <button className="rounded-md p-1.5 text-muted-foreground hover:bg-muted">
            <Search className="size-4" />
          </button>
          <button className="rounded-md p-1.5 text-muted-foreground hover:bg-muted">
            <Bell className="size-4" />
          </button>
          <button className="rounded-md p-1.5 text-muted-foreground hover:bg-muted">
            <User className="size-4" />
          </button>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}