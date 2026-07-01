/**
 * YouTube URL validation utilities.
 *
 * Validates and extracts playlist IDs from various YouTube URL formats.
 */

export interface YouTubeUrlValidation {
  isValid: boolean;
  playlistId?: string;
  error?: string;
}

/**
 * Validates a YouTube playlist URL and extracts the playlist ID.
 *
 * Supported formats:
 * - https://www.youtube.com/playlist?list=PLxxx
 * - https://youtube.com/playlist?list=PLxxx
 * - https://m.youtube.com/playlist?list=PLxxx
 * - https://youtu.be/PLxxx (less common but valid)
 *
 * @param url - The URL to validate
 * @returns Validation result with playlist ID if valid
 */
export function validateYouTubePlaylistUrl(url: string): YouTubeUrlValidation {
  if (!url || url.trim().length === 0) {
    return {
      isValid: false,
      error: 'Please enter a YouTube playlist URL',
    } as const;
  }

  const trimmedUrl = url.trim();

  // Check if it's a valid URL format
  let urlObj: URL;
  try {
    urlObj = new URL(trimmedUrl);
  } catch {
    return {
      isValid: false,
      error: 'Please enter a valid URL (e.g., https://youtube.com/playlist?list=...)',
    };
  }

  // Validate domain
  const validDomains = [
    'www.youtube.com',
    'youtube.com',
    'm.youtube.com',
    'youtu.be',
  ];

  if (!validDomains.includes(urlObj.hostname)) {
    return {
      isValid: false,
      error: 'URL must be from youtube.com or youtu.be',
    };
  }

  // Extract playlist ID from query parameters
  const playlistId = urlObj.searchParams.get('list');

  if (!playlistId) {
    // For youtu.be URLs, the path might contain the playlist ID
    if (urlObj.hostname === 'youtu.be' && urlObj.pathname.length > 1) {
      return {
        isValid: true,
        playlistId: urlObj.pathname.slice(1),
      };
    }

    return {
      isValid: false,
      error: 'URL must contain a playlist ID (list parameter)',
    };
  }

  // Validate playlist ID format (YouTube playlist IDs start with PL, OL, or UU)
  const validPrefixes = ['PL', 'OL', 'UU', 'FL', 'RD', 'LL'];
  const hasValidPrefix = validPrefixes.some((prefix) => playlistId.startsWith(prefix));

  if (!hasValidPrefix && playlistId.length < 10) {
    return {
      isValid: false,
      error: 'Invalid playlist ID format',
    };
  }

  return {
    isValid: true,
    playlistId,
  };
}

/**
 * Example YouTube playlist URLs for help text.
 */
export const EXAMPLE_PLAYLIST_URLS = [
  'https://www.youtube.com/playlist?list=PLrAXtmRdnEQy4QnuGQKx7BjPMH3mSfUwM',
  'https://youtube.com/playlist?list=PLF0gIqUE64mRagHFDNnuK2fmZgR2qWUQh',
  'https://m.youtube.com/playlist?list=PLF0gIqUE64mRagHFDNnuK2fmZgR2qWUQh',
];