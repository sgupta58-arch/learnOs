/**
 * Resources panel component for the learning workspace.
 *
 * Features:
 * - Empty state with helpful message
 * - Ready for future PDFs, links, attachments
 * - Clean, minimal UI
 *
 * Backend integration: Future phase
 */

import { FileText, ExternalLink, Paperclip, Plus } from 'lucide-react';
import { Button } from '@/common/components/ui/button';
import { cn } from '@/common/utils/cn';

interface ResourcesPanelProps {
  /** Current video ID */
  videoId?: string;
  /** Additional CSS classes */
  className?: string;
}

export function ResourcesPanel({
  className = '',
}: ResourcesPanelProps) {
  return (
    <div className={cn('flex h-full flex-col', className)}>
      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Paperclip className="size-5" />
            <h3 className="font-semibold">Resources</h3>
          </div>
          <Button variant="ghost" size="icon" disabled title="Add resource (coming soon)">
            <Plus className="size-4" />
          </Button>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Supplementary materials for this video.
        </p>
      </div>

      {/* Empty state */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center">
          <div className="mx-auto mb-4 flex size-16 items-center justify-center rounded-full bg-muted">
            <FileText className="size-8 text-muted-foreground" />
          </div>
          <h4 className="mb-2 text-sm font-medium">No resources yet</h4>
          <p className="mb-4 max-w-sm text-sm text-muted-foreground">
            Resources like PDFs, links, and attachments will appear here. This feature is coming soon.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-2 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <ExternalLink className="size-3" />
              Links
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <FileText className="size-3" />
              PDFs
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Paperclip className="size-3" />
              Attachments
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}