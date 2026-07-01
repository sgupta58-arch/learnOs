import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { importYouTubePlaylist } from '@/features/playlist/services/playlist-service';
import { PageHeader } from '@/common/components/page-header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/common/components/ui/card';
import { Button } from '@/common/components/ui/button';
import { Input } from '@/common/components/ui/input';
import { Label } from '@/common/components/ui/label';
import { Upload, CheckCircle, AlertCircle, Video } from 'lucide-react';

export function ImportPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [url, setUrl] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: importYouTubePlaylist,
    onSuccess: (response) => {
      if (response.success) {
        queryClient.invalidateQueries({ queryKey: ['playlists'] });
      } else {
        setErrorMessage(response.message || 'Import failed');
      }
    },
    onError: (error: Error) => {
      setErrorMessage(error.message || 'Failed to import playlist');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    if (!url.trim()) return;
    mutation.mutate(url.trim());
  };

  return (
    <div>
      <PageHeader title="Import Playlist" description="Import a YouTube playlist to start learning" />

      <div className="mx-auto max-w-lg">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Video className="size-5 text-red-500" />
              YouTube Playlist URL
            </CardTitle>
            <CardDescription>
              Paste a YouTube playlist URL to import all its videos into LearnOS.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {errorMessage && (
                <div className="flex items-center gap-2 rounded-md bg-destructive/10 p-3 text-sm text-destructive" role="alert">
                  <AlertCircle className="size-4" />
                  {errorMessage}
                </div>
              )}

              {mutation.isSuccess && mutation.data?.success && (
                <div className="flex items-center gap-2 rounded-md bg-emerald-50 p-3 text-sm text-emerald-700" role="alert">
                  <CheckCircle className="size-4" />
                  Successfully imported "{mutation.data.data?.title}" ({mutation.data.data?.videos_imported} videos)
                </div>
              )}

              <div className="grid gap-2">
                <Label htmlFor="url">Playlist URL</Label>
                <Input
                  id="url"
                  type="url"
                  placeholder="https://youtube.com/playlist?list=..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={mutation.isPending}
                />
              </div>

              <Button type="submit" className="w-full" disabled={mutation.isPending || !url.trim()}>
                {mutation.isPending ? (
                  <>Importing...</>
                ) : (
                  <>
                    <Upload className="mr-2 size-4" />
                    Import Playlist
                  </>
                )}
              </Button>

              {mutation.isSuccess && (
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => navigate('/dashboard/playlists')}
                >
                  View My Playlists
                </Button>
              )}
            </form>
          </CardContent>
        </Card>

        <div className="mt-6 text-center text-xs text-muted-foreground">
          <p>Enter the full URL of any public YouTube playlist.</p>
          <p>The playlist and all its videos will be imported to your library.</p>
        </div>
      </div>
    </div>
  );
}