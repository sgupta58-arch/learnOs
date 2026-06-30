"""Constants for YouTube platform integration."""

# YouTube API constants
YOUTUBE_API_MAX_RESULTS = 500  # Maximum number of videos to fetch per playlist
YOUTUBE_API_RETRY_ATTEMPTS = 3  # Number of retry attempts for API calls
YOUTUBE_API_RETRY_DELAY = 1  # Delay between retry attempts in seconds

# YouTube URL patterns
YOUTUBE_PLAYLIST_URL_PATTERNS = [
    "https://www.youtube.com/playlist?list=",
    "https://youtube.com/playlist?list=",
    "https://m.youtube.com/playlist?list=",
]

YOUTUBE_VIDEO_URL_PATTERNS = [
    "https://www.youtube.com/watch?v=",
    "https://youtube.com/watch?v=",
    "https://m.youtube.com/watch?v=",
    "https://youtu.be/",
]

# Error messages
ERROR_MESSAGES = {
    "invalid_playlist_url": "Invalid YouTube playlist URL",
    "playlist_not_found": "YouTube playlist not found",
    "private_playlist": "Cannot access private playlist",
    "quota_exceeded": "YouTube API quota exceeded",
    "auth_failed": "YouTube API authentication failed",
    "network_timeout": "Network timeout while fetching playlist data",
    "duplicate_playlist": "Playlist already exists in your library",
}

# Status constants
PLAYLIST_STATUSES = {
    "PUBLIC": "public",
    "PRIVATE": "private",
    "UNLISTED": "unlisted",
}

# Source type constants
SOURCE_TYPES = {
    "YOUTUBE": "youtube",
}