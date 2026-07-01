import { PageHeader } from '@/common/components/page-header';
import { StatCard } from '@/common/components/stat-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/common/components/ui/card';
import { BarChart3, Clock, TrendingUp, Target, BookOpen } from 'lucide-react';

export function AnalyticsPage() {
  return (
    <div>
      <PageHeader
        title="Analytics"
        description="Track your learning patterns and effectiveness."
      />

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Learning Time" value="0h" icon={<Clock className="size-4" />} description="All time" />
        <StatCard title="Videos Completed" value="0" icon={<BookOpen className="size-4" />} description="Across all playlists" />
        <StatCard title="Study Streak" value="0 days" icon={<TrendingUp className="size-4" />} description="Current streak" />
        <StatCard title="Completion Rate" value="0%" icon={<Target className="size-4" />} description="Overall progress" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Weekly Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end justify-between gap-2" style={{ height: 120 }}>
              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
                <div key={day} className="flex flex-1 flex-col items-center gap-1">
                  <div
                    className="w-full rounded-md bg-primary/20"
                    style={{ height: `${Math.random() * 60 + 10}px` }}
                  />
                  <span className="text-xs text-muted-foreground">{day}</span>
                </div>
              ))}
            </div>
            <p className="mt-4 text-center text-xs text-muted-foreground">
              Analytics data will be available once you start learning.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Learning Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-8">
              <BarChart3 className="mb-2 size-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                Import playlists and watch videos to see your learning distribution.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}