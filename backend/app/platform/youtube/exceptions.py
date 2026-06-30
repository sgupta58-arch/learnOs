"""Custom exceptions for YouTube platform integration."""


class YouTubeAPIError(Exception):
    """Base exception for YouTube API errors.
    
    Why this exception exists: To provide a common base class for all YouTube API-related
    errors, allowing for consistent error handling throughout the application.
    
    Why it belongs to the exceptions layer: This is a domain-specific exception that
    represents API integration issues, separate from application business logic.
    
    How future Transcript Generation will use it: Will catch API errors when
    attempting to fetch transcripts for videos.
    
    How future AI Tutor will use it: Will catch API errors when analyzing
    video content for AI recommendations.
    """
    pass


class YouTubeAuthError(YouTubeAPIError):
    """Exception raised when YouTube API authentication fails.
    
    Why this exception exists: To specifically handle authentication issues with
    the YouTube API, allowing for targeted error handling and user feedback.
    
    Why it belongs to the exceptions layer: This is a specific type of API error
    that requires different handling than general API errors.
    
    How future Transcript Generation will use it: Will catch auth errors when
    attempting to fetch transcripts for videos.
    
    How future AI Tutor will use it: Will catch auth errors when analyzing
    video content for AI recommendations.
    """
    pass


class YouTubeQuotaExceededError(YouTubeAPIError):
    """Exception raised when YouTube API quota is exceeded.
    
    Why this exception exists: To specifically handle rate limiting issues with
    the YouTube API, allowing for proper backoff and user feedback.
    
    Why it belongs to the exceptions layer: This is a specific type of API error
    that requires different handling than general API errors.
    
    How future Transcript Generation will use it: Will catch quota errors when
    attempting to fetch transcripts for multiple videos.
    
    How future AI Tutor will use it: Will catch quota errors when analyzing
    large volumes of video content for AI recommendations.
    """
    pass


class InvalidURLException(Exception):
    """Exception raised when a YouTube URL is invalid or unsupported.
    
    Why this exception exists: To provide specific error handling for invalid
    YouTube URLs, allowing for better user feedback and error messages.
    
    Why it belongs to the exceptions layer: This is a domain-specific exception
    that represents input validation issues.
    
    How future Transcript Generation will use it: Will validate video URLs
    before attempting to fetch transcripts.
    
    How future AI Tutor will use it: Will validate content URLs before
    analyzing them for AI recommendations.
    """
    pass