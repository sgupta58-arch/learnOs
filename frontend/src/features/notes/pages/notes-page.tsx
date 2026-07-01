import { PageHeader } from '@/common/components/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/common/components/ui/card';
import { Button } from '@/common/components/ui/button';
import { Input } from '@/common/components/ui/input';
import { StickyNote, Search, Plus, FileText } from 'lucide-react';

export function NotesPage() {
  return (
    <div>
      <PageHeader
        title="Notes"
        description="Capture and organize your learning notes."
        actions={
          <Button size="sm" disabled>
            <Plus className="mr-1 size-4" />
            New Note
          </Button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Notes sidebar */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Search notes..." className="pl-9" disabled />
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-8">
              <FileText className="mb-2 size-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">No notes yet</p>
            </div>
          </CardContent>
        </Card>

        {/* Editor area */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Editor</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-12">
              <StickyNote className="mb-4 size-12 text-muted-foreground" />
              <h3 className="text-lg font-medium">Welcome to Notes</h3>
              <p className="mt-2 max-w-sm text-center text-sm text-muted-foreground">
                Create notes linked to your videos and playlists. Your notes will be searchable
                and can be enhanced with AI-powered summaries and connections.
              </p>
              <div className="mt-6 space-y-2 text-left">
                <p className="text-xs font-medium text-muted-foreground">Coming in a future phase:</p>
                <ul className="list-inside list-disc text-sm text-muted-foreground">
                  <li>Rich markdown editor</li>
                  <li>Link notes to specific video timestamps</li>
                  <li>AI-powered note summaries</li>
                  <li>Full-text search across all notes</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}