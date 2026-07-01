/**
 * Learning service.
 *
 * All backend learning/workspace API calls are defined here.
 * Backend endpoints used:
 * - GET    /videos/progress/{video_id}     → Get video progress
 * - POST   /videos/progress                → Update video progress
 * - GET    /users/me/continue-learning     → Get continue learning data
 */

import { apiClient } from '@/services/api-client';
import type { ApiResponse } from '@/features/auth/types';
import type { VideoProgress, VideoProgressUpdate } from '@/features/learning/types';

export interface ContinueLearningResponse {
  current_video: VideoProgress & {
    video: {
      id: string;
      title: string;
      thumbnail_url: string | null;
      duration_seconds: number | null;
      youtube_video_id: string;
    };
    playlist: {
      id: string;
      title: string;
      thumbnail_url: string | null;
    };
  } | null;
  recently_watched: Array<{
    video: {
      id: string;
      title: string;
      thumbnail_url: string | null;
      duration_seconds: number | null;
      youtube_video_id: string;
    };
    playlist: {
      id: string;
      title: string;
    };
    progress: VideoProgress;
  }>;
}

/** Fetch continue learning data for current user */
export async function getContinueLearning(): Promise<ApiResponse<ContinueLearningResponse>> {
  const response = await apiClient.get<ApiResponse<ContinueLearningResponse>>('/users/me/continue-learning');
  return response.data;
}

/** Get video progress */
export async function getVideoProgress(
  videoId: string,
): Promise<ApiResponse<VideoProgress>> {
  const response = await apiClient.get<ApiResponse<VideoProgress>>(`/videos/progress/${videoId}`);
  return response.data;
}

/** Update video progress */
export async function updateVideoProgress(
  payload: VideoProgressUpdate,
): Promise<ApiResponse<VideoProgress>> {
  const response = await apiClient.post<ApiResponse<VideoProgress>>('/videos/progress', payload);
  return response.data;
}

/** Mark video as completed */
export async function markVideoComplete(
  videoId: string,
  playlistId: string,
): Promise<ApiResponse<VideoProgress>> {
  return updateVideoProgress({
    video_id: videoId,
    playlist_id: playlistId,
    progress_seconds: 0,
    status: 'completed',
  });
}

/** Mark video as in progress */
export async function markVideoInProgress(
  videoId: string,
  playlistId: string,
  progressSeconds: number,
): Promise<ApiResponse<VideoProgress>> {
  return updateVideoProgress({
    video_id: videoId,
    playlist_id: playlistId,
    progress_seconds: progressSeconds,
    status: 'in_progress',
  });
}