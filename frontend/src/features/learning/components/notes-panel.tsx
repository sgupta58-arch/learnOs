/**
 * Notes panel component for the learning workspace.
 *
 * Features:
 * - Rich text editor placeholder
 * - Save button (disabled, ready for backend)
 * - Markdown preview placeholder
 * - Timestamp linking (future)
 * - Auto-save indicator (future)
 *
 * Backend integration: Future phase
 */

import { FileText, Save, Eye } from 'lucide-react';
import { Button } from '@/common/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/common/components/ui/tabs';
import { Textarea } from '@/common/components/ui/textarea';
import { cn } from '@/common/utils/cn';

interface NotesPanelProps {
  /** Current video ID for timestamp linking */
  videoId?: string;
  /** Current video timestamp */
  currentTime?: number;
  /** Additional CSS classes */
  className?: string;
}

export function NotesPanel({
  currentTime = 0,
  className = '',
}: NotesPanelProps) {
  const formatTimestamp = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={cn('flex h-full flex-col', className)}>
      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center gap-2">
          <FileText className="size-5" />
          <h3 className="font-semibold">Notes</h3>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Take notes while watching. Notes will sync with video timestamps.
        </p>
      </div>

      {/* Tabs: Editor / Preview */}
      <Tabs value="editor" className="flex-1 flex flex-col">
        <TabsList className="mx-4 mt-4">
          <TabsTrigger value="editor" className="gap-2">
            <Eye className="size-4" />
            Editor
          </TabsTrigger>
          <TabsTrigger value="preview" disabled>
            Preview
          </TabsTrigger>
        </TabsList>

        {/* Editor Tab */}
        <TabsContent value="editor" className="flex-1 flex flex-col mt-0">
          <div className="flex-1 p-4">
            <Textarea
              placeholder="Start taking notes...

# Tips:
- Use markdown formatting
- Press Ctrl+Shift+T to insert timestamp
- Notes auto-save as you type (coming soon)"
              className="h-full resize-none font-mono text-sm"
              aria-label="Notes editor"
            />
          </div>

          {/* Timestamp insertion hint */}
          <div className="border-t p-3 text-sm text-muted-foreground">
            💡 Press <kbd className="rounded bg-muted px-1.5 py-0.5 text-xs font-mono">Ctrl</kbd> +{' '}
            <kbd className="rounded bg-muted px-1.5 py-0.5 text-xs font-mono">Shift</kbd> +{' '}
            <kbd className="rounded bg-muted px-1.5 py-0.5 text-xs font-mono">T</kbd> to insert timestamp{' '}
            {formatTimestamp(currentTime)}
          </div>

          {/* Actions */}
          <div className="border-t p-4">
            <div className="flex items-center justify-between">
              <p className="text-xs text-muted-foreground">
                Last saved: <span className="italic">Never</span>
              </p>
              <Button disabled className="gap-2">
                <Save className="size-4" />
                Save Note
              </Button>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">
              Note saving will be available in a future update.
            </p>
          </div>
        </TabsContent>

        {/* Preview Tab (placeholder) */}
        <TabsContent value="preview" className="flex-1 p-4">
          <div className="flex h-full items-center justify-center rounded-lg border-2 border-dashed">
            <div className="text-center">
              <Eye className="mx-auto size-12 text-muted-foreground" />
              <p className="mt-2 text-sm font-medium">Markdown Preview</p>
              <p className="text-sm text-muted-foreground">
                Preview will be available once notes are saved.
              </p>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}