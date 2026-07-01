/**
 * Playlist service.
 *
 * All backend playlist API calls are defined here.
 * Backend endpoints used:
 * - GET    /playlists       → List user playlists
 * - GET    /playlists/{id}  → Get playlist detail
 * - POST   /playlists       → Create playlist (manual)
 * - PATCH  /playlists/{id}  → Update playlist
 * - DELETE /playlists/{id}  → Delete playlist
 * - POST   /playlists/import/youtube?source_url=... → Import YouTube playlist
 */

import { apiClient } from '@/services/api-client';
import type { ApiResponse } from '@/features/auth/types';

export interface Playlist {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  source_type: string;
  source_url: string | null;
  thumbnail_url: string | null;
  status: string;
  target_completion_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface PlaylistListResponse {
  items: Playlist[];
  total: number;
  skip: number;
  limit: number;
}

export interface YouTubeImportResult {
  playlist_id: string;
  title: string;
  videos_imported: number;
}

export interface Video {
  id: string;
  playlist_id: string;
  youtube_video_id: string;
  title: string;
  description: string | null;
  thumbnail_url: string | null;
  channel_name: string | null;
  duration_seconds: number | null;
  position: number | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

/** Fetch playlists for current user */
export async function getPlaylists(): Promise<ApiResponse<PlaylistListResponse>> {
  const response = await apiClient.get<ApiResponse<PlaylistListResponse>>('/playlists');
  return response.data;
}

/** Fetch a single playlist by ID */
export async function getPlaylist(id: string): Promise<ApiResponse<Playlist>> {
  const response = await apiClient.get<ApiResponse<Playlist>>(`/playlists/${id}`);
  return response.data;
}

/** Delete a playlist */
export async function deletePlaylist(id: string): Promise<ApiResponse<Playlist>> {
  const response = await apiClient.delete<ApiResponse<Playlist>>(`/playlists/${id}`);
  return response.data;
}

/** Import a YouTube playlist from URL */
export async function importYouTubePlaylist(
  sourceUrl: string,
): Promise<ApiResponse<YouTubeImportResult>> {
  const response = await apiClient.post<ApiResponse<YouTubeImportResult>>(
    `/playlists/import/youtube?source_url=${encodeURIComponent(sourceUrl)}`,
  );
  return response.data;
}

/** Fetch videos for a playlist */
export async function getPlaylistVideos(
  playlistId: string,
): Promise<Video[]> {
  const response = await apiClient.get<Video[]>(
    `/videos?playlist_id=${playlistId}`,
  );
  return response.data;
}