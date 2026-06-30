"""YouTube platform integration layer.

This package contains all YouTube-specific integrations, including:
- YouTube API client
- URL parsing utilities
- Pydantic schemas for YouTube data
- Custom exceptions for YouTube errors
- Constants for YouTube configuration

Why this layer exists: To isolate YouTube API dependencies from the rest of the application,
making it easier to test, maintain, and potentially add other content sources in the future.

Architecture pattern: The platform layer is separate from services, allowing services to
remain platform-agnostic. Each platform should implement a consistent interface:
1. Parser: Extract IDs from URLs
2. Client: Fetch data from the platform
3. Schemas: Define data structures
4. Exceptions: Handle platform-specific errors
5. Constants: Configure platform behavior

How future Transcript Generation will use it: Will use the YouTube client to fetch
video metadata and potentially transcripts from YouTube's API.

How future AI Tutor will use it: Will use the YouTube client to fetch video metadata
and potentially closed captions for AI analysis.
"""