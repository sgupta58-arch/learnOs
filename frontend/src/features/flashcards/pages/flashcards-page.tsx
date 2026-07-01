import { PageHeader } from '@/common/components/page-header';
import { StatCard } from '@/common/components/stat-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/common/components/ui/card';
import { Button } from '@/common/components/ui/button';
import { Sparkles, ChevronLeft, ChevronRight } from 'lucide-react';

export function FlashcardsPage() {
  return (
    <div>
      <PageHeader
        title="Flashcards"
        description="Review and reinforce your learning with flashcards."
      />

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Due for Review" value="0" icon={<Sparkles className="size-4" />} description="Cards to review" />
        <StatCard title="New Cards" value="0" icon={<Sparkles className="size-4" />} description="Unseen cards" />
        <StatCard title="Mastered" value="0" icon={<Sparkles className="size-4" />} description="Cards learned" />
        <StatCard title="Total Cards" value="0" icon={<Sparkles className="size-4" />} description="In your deck" />
      </div>

      <Card className="mx-auto max-w-lg">
        <CardHeader>
          <CardTitle className="text-base">Card Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
              <Sparkles className="size-8 text-primary" />
            </div>
            <h3 className="text-lg font-medium">No Flashcards Yet</h3>
            <p className="mt-2 text-center text-sm text-muted-foreground">
              Flashcards will be automatically generated from your video transcripts and notes.
              Import playlists and use the AI Tutor to create your first flashcards.
            </p>
            <div className="mt-6 flex items-center gap-4">
              <Button variant="outline" size="sm" disabled>
                <ChevronLeft className="mr-1 size-4" />
                Previous
              </Button>
              <span className="text-xs text-muted-foreground">0 / 0</span>
              <Button variant="outline" size="sm" disabled>
                Next
                <ChevronRight className="ml-1 size-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}