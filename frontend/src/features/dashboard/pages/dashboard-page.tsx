import { useQuery } from '@tanstack/react-query';
import { getPlaylists } from '@/features/playlist/services/playlist-service';
import { PageHeader } from '@/common/components/page-header';
import { StatCard } from '@/common/components/stat-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/common/components/ui/card';
import { ListVideo, Clock, TrendingUp, Target, BookOpen, Zap, Upload, Sparkles } from 'lucide-react';

export function DashboardPage() {
  const { data: playlistData, isLoading } = useQuery({
    queryKey: ['playlists'],
    queryFn: getPlaylists,
  });

  const playlists = playlistData?.data?.items ?? [];

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Welcome back to LearnOS. Here's your learning overview."
      />

      {/* Stats grid */}
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Playlists"
          value={isLoading ? '...' : playlists.length}
          icon={<ListVideo className="size-4" />}
          description="Total learning playlists"
        />
        <StatCard
          title="Learning Time"
          value="0h"
          icon={<Clock className="size-4" />}
          description="Total time watched"
        />
        <StatCard
          title="Study Streak"
          value="0 days"
          icon={<TrendingUp className="size-4" />}
          description="Current streak"
        />
        <StatCard
          title="Daily Goal"
          value="0%"
          icon={<Target className="size-4" />}
          description="Today's progress"
        />
      </div>

      {/* Main content grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent playlists */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Recent Playlists</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 animate-pulse rounded-lg bg-muted" />
                ))}
              </div>
            ) : playlists.length === 0 ? (
              <div className="py-8 text-center">
                <BookOpen className="mx-auto mb-2 size-8 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  No playlists yet. Import your first YouTube playlist to get started.
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {playlists.slice(0, 5).map((playlist) => (
                  <div
                    key={playlist.id}
                    className="flex items-center gap-3 rounded-lg border p-3"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10">
                      <ListVideo className="size-4 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{playlist.title}</p>
                      <p className="text-xs text-muted-foreground">
                        {playlist.source_type} · {new Date(playlist.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick actions & summary */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted/50 cursor-pointer transition-colors">
                <Upload className="size-4 text-primary" />
                <span className="text-sm">Import Playlist</span>
              </div>
              <div className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted/50 cursor-pointer transition-colors">
                <Zap className="size-4 text-amber-500" />
                <span className="text-sm">AI Tutor</span>
              </div>
              <div className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted/50 cursor-pointer transition-colors">
                <Sparkles className="size-4 text-violet-500" />
                <span className="text-sm">Review Flashcards</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Today's Focus</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                No items scheduled for today. Import a playlist or set a revision goal to get started.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}