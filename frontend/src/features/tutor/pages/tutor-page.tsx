import { PageHeader } from '@/common/components/page-header';
import { Card, CardContent } from '@/common/components/ui/card';
import { Button } from '@/common/components/ui/button';
import { Input } from '@/common/components/ui/input';
import { Bot, Send, Sparkles } from 'lucide-react';

export function TutorPage() {
  return (
    <div className="flex h-full flex-col">
      <PageHeader
        title="AI Tutor"
        description="Ask questions about your learning content and get AI-powered answers."
      />

      <Card className="flex-1">
        <CardContent className="flex h-full flex-col items-center justify-center p-6">
          <div className="mx-auto max-w-md text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
              <Bot className="size-8 text-primary" />
            </div>
            <h2 className="text-xl font-semibold">AI Tutor</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Your personal AI learning assistant will be available in a future phase.
              Ask questions, get explanations, and test your knowledge — all powered by your learning content.
            </p>
            <div className="mt-6 space-y-2 text-left">
              <p className="text-xs font-medium text-muted-foreground">Coming features:</p>
              <div className="flex items-center gap-2 text-sm">
                <Sparkles className="size-3.5 text-amber-500" />
                <span>Question answering over your video library</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Sparkles className="size-3.5 text-amber-500" />
                <span>Personalized practice questions</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Sparkles className="size-3.5 text-amber-500" />
                <span>Concept explanations and summaries</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Chat input placeholder */}
      <div className="mt-4">
        <div className="relative">
          <Input
            placeholder="Ask a question about your learning content..."
            className="pr-12"
            disabled
          />
          <Button
            size="icon"
            className="absolute right-1 top-1/2 -translate-y-1/2 size-8"
            disabled
          >
            <Send className="size-4" />
          </Button>
        </div>
        <p className="mt-2 text-center text-xs text-muted-foreground">
          AI Tutor backend will be connected in a future phase.
        </p>
      </div>
    </div>
  );
}