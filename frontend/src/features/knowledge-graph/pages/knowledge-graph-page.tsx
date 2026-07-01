import { PageHeader } from '@/common/components/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/common/components/ui/card';
import { Input } from '@/common/components/ui/input';
import { Share2, Search, ZoomIn, ZoomOut } from 'lucide-react';

export function KnowledgeGraphPage() {
  return (
    <div>
      <PageHeader
        title="Knowledge Graph"
        description="Visualize connections between concepts in your learning library."
      />

      <div className="grid gap-6 lg:grid-cols-4">
        {/* Graph visualization */}
        <Card className="lg:col-span-3">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Graph View</CardTitle>
            <div className="flex items-center gap-1">
              <button className="rounded-md p-1.5 text-muted-foreground hover:bg-muted" title="Zoom in">
                <ZoomIn className="size-4" />
              </button>
              <button className="rounded-md p-1.5 text-muted-foreground hover:bg-muted" title="Zoom out">
                <ZoomOut className="size-4" />
              </button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-16">
              <Share2 className="mb-4 size-16 text-muted-foreground/40" />
              <h3 className="text-lg font-medium">Knowledge Graph</h3>
              <p className="mt-2 max-w-md text-center text-sm text-muted-foreground">
                The Knowledge Graph visualizes how concepts in your learning library connect to each other.
                It will automatically build as you import content and use AI-powered analysis.
              </p>
              <div className="mt-6 space-y-2 text-left">
                <p className="text-xs font-medium text-muted-foreground">Coming in a future phase:</p>
                <ul className="list-inside list-disc text-sm text-muted-foreground">
                  <li>Automatic concept extraction from video transcripts</li>
                  <li>Interactive graph visualization with zoom and pan</li>
                  <li>Click a concept to see all related videos</li>
                  <li>Discover prerequisite relationships between topics</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Info panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Search concepts..." className="pl-9" disabled />
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-8">
              <p className="text-center text-sm text-muted-foreground">
                Select a node in the graph to see details about a concept.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}