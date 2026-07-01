import { PageHeader } from '@/common/components/page-header';
import { StatCard } from '@/common/components/stat-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/common/components/ui/card';
import { Calendar, CheckCircle2, Clock, ListTodo } from 'lucide-react';

export function RevisionPage() {
  return (
    <div>
      <PageHeader
        title="Revision Planner"
        description="Plan and track your revision schedule."
      />

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Today's Revision" value="0" icon={<Clock className="size-4" />} description="Items due today" />
        <StatCard title="Upcoming" value="0" icon={<Calendar className="size-4" />} description="Next 7 days" />
        <StatCard title="Completed" value="0" icon={<CheckCircle2 className="size-4" />} description="Total revised" />
        <StatCard title="Total Planned" value="0" icon={<ListTodo className="size-4" />} description="All revision items" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Revision Calendar</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8">
            <Calendar className="mb-2 size-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              Revision planning will be available in a future phase.
              Track what you've learned and schedule reviews using spaced repetition.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}