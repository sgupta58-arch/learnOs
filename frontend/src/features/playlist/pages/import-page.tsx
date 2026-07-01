import { useState, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { importYouTubePlaylist } from '@/features/playlist/services/playlist-service';
import { validateYouTubePlaylistUrl, EXAMPLE_PLAYLIST_URLS } from '@/features/playlist/utils/validate-youtube-url';
import { PageHeader } from '@/common/components/page-header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/common/components/ui/card';
import { Button } from '@/common/components/ui/button';
import { Input } from '@/common/components/ui/input';
import { Label } from '@/common/components/ui/label';
import { Upload, CheckCircle, AlertCircle, Video, Loader2, Play, ListVideo } from 'lucide-react';

type ImportStatus = 'idle' | 'validating' | 'importing' | 'success' | 'error';

export function ImportPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [url, setUrl] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [importStatus, setImportStatus] = useState<ImportStatus>('idle');
  const [importedPlaylist, setImportedPlaylist] = useState<{ id: string; title: string; videosCount: number } | null>(null);

  const mutation = useMutation({
    mutationFn: importYouTubePlaylist,
    onSuccess: (response) => {
      if (response.success && response.data) {
        setImportStatus('success');
        setImportedPlaylist({
          id: response.data.playlist_id,
          title: response.data.title,
          videosCount: response.data.videos_imported,
        });
        // Invalidate all playlist-related queries
        queryClient.invalidateQueries({ queryKey: ['playlists'] });
        queryClient.invalidateQueries({ queryKey: ['continue-learning'] });
      } else {
        setImportStatus('error');
        setErrorMessage(response.message || 'Import failed');
      }
    },
    onError: (error: Error) => {
      setImportStatus('error');
      setErrorMessage(error.message ?? 'Failed to import playlist');
    },
  });

  const validateUrl = useCallback((value: string): boolean => {
    const validation = validateYouTubePlaylistUrl(value);
    if (!validation.isValid) {
      setErrorMessage(validation.error! || 'Invalid URL');
      return false;
    }
    setErrorMessage(null);
    return true;
  }, []);

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setUrl(value);
    if (value.length > 10) {
      validateUrl(value);
    } else {
      setErrorMessage(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!validateUrl(url)) {
      return;
    }

    setImportStatus('importing');
    mutation.mutate(url.trim());
  };

  const handleImportAnother = () => {
    setUrl('');
    setErrorMessage(null);
    setImportStatus('idle');
    setImportedPlaylist(null);
  };

  const handleOpenPlaylist = () => {
    if (importedPlaylist?.id) {
      navigate(`/dashboard/playlists/${importedPlaylist.id}`);
    }
  };

  const handleStartLearning = () => {
    if (importedPlaylist?.id) {
      navigate(`/dashboard/playlists/${importedPlaylist.id}`);
    }
  };

  const isImporting = importStatus === 'importing';
  const isSuccess = importStatus === 'success';
  const urlValidation = url.length > 10 ? validateYouTubePlaylistUrl(url) : null;
  const isUrlValid = urlValidation?.isValid ?? false;

  return (
    <div>
      <PageHeader
        title="Import Playlist"
        description="Import a YouTube playlist to start your learning journey"
      />

      <div className="mx-auto max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Video className="size-5 text-red-500" />
              YouTube Playlist URL
            </CardTitle>
            <CardDescription>
              Paste a YouTube playlist URL below to import all its videos into LearnOS.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isSuccess && importedPlaylist ? (
              /* Success State */
              <div className="space-y-6">
                <div className="flex flex-col items-center justify-center rounded-lg border-2 border-emerald-200 bg-emerald-50 p-8 text-center dark:border-emerald-800 dark:bg-emerald-950">
                  <CheckCircle className="mb-3 size-12 text-emerald-600 dark:text-emerald-400" />
                  <h3 className="mb-1 text-lg font-semibold text-emerald-900 dark:text-emerald-100">
                    Playlist Imported Successfully!
                  </h3>
                  <p className="mb-4 text-sm text-emerald-700 dark:text-emerald-300">
                    {importedPlaylist.title}
                  </p>
                  <div className="flex gap-4 text-sm text-emerald-600 dark:text-emerald-400">
                    <div className="flex items-center gap-1">
                      <ListVideo className="size-4" />
                      <span>{importedPlaylist.videosCount} videos</span>
                    </div>
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <Button onClick={handleStartLearning} className="w-full">
                    <Play className="mr-2 size-4" />
                    Start Learning
                  </Button>
                  <Button onClick={handleOpenPlaylist} variant="outline" className="w-full">
                    <ListVideo className="mr-2 size-4" />
                    View Playlist
                  </Button>
                </div>

                <Button
                  onClick={handleImportAnother}
                  variant="ghost"
                  className="w-full"
                >
                  Import Another Playlist
                </Button>
              </div>
            ) : (
              /* Import Form */
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Error Alert */}
                {errorMessage && importStatus === 'error' && (
                  <div className="flex items-center gap-2 rounded-md bg-destructive/10 p-3 text-sm text-destructive" role="alert">
                    <AlertCircle className="size-4" />
                    {errorMessage}
                  </div>
                )}

                {/* URL Input */}
                <div className="grid gap-2">
                  <Label htmlFor="url">Playlist URL</Label>
                  <Input
                    id="url"
                    type="url"
                    placeholder="https://youtube.com/playlist?list=..."
                    value={url}
                    onChange={handleUrlChange}
                    disabled={isImporting}
                    aria-invalid={!!errorMessage}
                    aria-describedby={errorMessage ? 'url-error' : undefined}
                    className={errorMessage ? 'border-destructive' : ''}
                  />
                  {errorMessage && (
                    <p id="url-error" className="text-sm text-destructive" role="alert">
                      {errorMessage}
                    </p>
                  )}
                </div>

                {/* Import Button */}
                <Button
                  type="submit"
                  className="w-full"
                  disabled={isImporting || !url.trim() || !isUrlValid}
                >
                  {isImporting ? (
                    <>
                      <Loader2 className="mr-2 size-4 animate-spin" />
                      Importing Playlist...
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 size-4" />
                      Import Playlist
                    </>
                  )}
                </Button>

                {/* Help Text */}
                <div className="space-y-2 rounded-lg bg-muted/50 p-3 text-xs text-muted-foreground">
                  <p className="font-medium">Supported URL formats:</p>
                  <ul className="list-inside list-disc space-y-1">
                    <li>https://www.youtube.com/playlist?list=...</li>
                    <li>https://youtube.com/playlist?list=...</li>
                    <li>https://m.youtube.com/playlist?list=...</li>
                  </ul>
                  <p className="mt-2">Example:</p>
                  <code className="block break-all rounded bg-muted p-1 font-mono">
                    {EXAMPLE_PLAYLIST_URLS[0]}
                  </code>
                </div>
              </form>
            )}
          </CardContent>
        </Card>

        {/* Additional Help */}
        {!isSuccess && (
          <div className="mt-6 text-center text-sm text-muted-foreground">
            <p>Import any public YouTube playlist to get started.</p>
            <p className="mt-1">All videos will be available in your learning workspace.</p>
          </div>
        )}
      </div>
    </div>
  );
}
