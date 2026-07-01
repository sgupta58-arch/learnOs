import { PageHeader } from '@/common/components/page-header';
import { StatCard } from '@/common/components/stat-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/common/components/ui/card';
import { TrendingUp, BookOpen, Clock, Target, CheckCircle2, BarChart3 } from 'lucide-react';

export function ProgressPage() {
  return (
    <div>
      <PageHeader
        title="Progress"
        description="Track your learning journey across all courses."
      />

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Videos Completed" value="0" icon={<BookOpen className="size-4" />} description="Total completed" />
        <StatCard title="Completion Rate" value="0%" icon={<Target className="size-4" />} description="Overall" />
        <StatCard title="Study Time" value="0h" icon={<Clock className="size-4" />} description="Total" />
        <StatCard title="Streak" value="0 days" icon={<TrendingUp className="size-4" />} description="Current" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Current Courses</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-8">
              <CheckCircle2 className="mb-2 size-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                No courses in progress. Import a playlist to get started.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Milestones</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-8">
              <BarChart3 className="mb-2 size-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                Milestones will appear as you complete videos and playlists.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}