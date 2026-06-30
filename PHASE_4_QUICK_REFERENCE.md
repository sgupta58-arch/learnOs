# Phase 4 Quick Reference Guide

## Files Created/Modified

### Models
- ✅ `/backend/app/models/video.py` - Video persistence model

### Database
- ✅ `/backend/alembic/versions/004_create_videos_table.py` - Migration

### Schemas
- ✅ `/backend/app/schemas/video.py` - Pydantic validation schemas

### Repositories
- ✅ `/backend/app/repositories/video.py` - Data access layer

### Services
- ✅ `/backend/app/services/video.py` - Video business logic
- ✅ `/backend/app/services/youtube_import.py` - Import orchestration

### Platform Layer (YouTube)
- ✅ `/backend/app/platform/__init__.py` - Platform layer docs
- ✅ `/backend/app/platform/youtube/__init__.py` - YouTube package
- ✅ `/backend/app/platform/youtube/client.py` - YouTube API client
- ✅ `/backend/app/platform/youtube/parser.py` - URL parsing utilities
- ✅ `/backend/app/platform/youtube/schemas.py` - YouTube data schemas
- ✅ `/backend/app/platform/youtube/exceptions.py` - Custom exceptions
- ✅ `/backend/app/platform/youtube/constants.py` - Configuration

### API
- ✅ `/backend/app/api/v1/playlists.py` - Updated with import route
- ✅ `/backend/app/api/v1/videos.py` - Video endpoints (pre-existing)

### Dependencies
- ✅ `/backend/app/dependencies/youtube_import.py` - Service injection
- ✅ `/backend/app/core/config.py` - Added YOUTUBE_API_KEY

### Tests
- ✅ `/backend/tests/test_youtube_import_service.py` - Updated
- ✅ `/backend/tests/test_youtube_url_parser.py` - URL parser tests (20 cases)
- ✅ `/backend/tests/test_youtube_client.py` - Client tests (15+ cases)

### Configuration
- ✅ `/backend/pyproject.toml` - Added google-api-python-client

---

## API Endpoints

### Import YouTube Playlist
```
POST /api/v1/playlists/import/youtube
Authorization: Bearer <jwt_token>

Request:
{
    "source_url": "https://www.youtube.com/playlist?list=PLxxx"
}

Response:
{
    "success": true,
    "data": {
        "playlist_id": "uuid",
        "title": "Playlist Name",
        "videos_imported": 42
    },
    "message": "YouTube playlist imported successfully"
}
```

### List Videos in Playlist
```
GET /api/v1/videos?playlist_id=uuid
Authorization: Bearer <jwt_token>

Response:
[
    {
        "id": "uuid",
        "playlist_id": "uuid",
        "youtube_video_id": "dQw4w9WgXcQ",
        "title": "Video Title",
        "description": "...",
        "thumbnail_url": "https://...",
        "channel_name": "Channel",
        "duration_seconds": 300,
        "position": 1,
        "published_at": "2023-01-01T00:00:00Z",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "deleted_at": null
    }
]
```

---

## Environment Configuration

Add to `.env`:
```
YOUTUBE_API_KEY=your_youtube_api_key_here
```

Get YouTube API key from:
1. Go to Google Cloud Console
2. Create a project
3. Enable YouTube Data API v3
4. Create API key credentials

---

## Clean Architecture Principles Applied

| Layer | Responsibility | Location |
|-------|----------------|----------|
| API | HTTP request/response handling | `/api/v1/` |
| Service | Business logic orchestration | `/services/` |
| Repository | Database operations | `/repositories/` |
| Model | Domain entities | `/models/` |
| Schema | Input/output validation | `/schemas/` |
| Platform | External integrations | `/platform/` |

---

## Testing

Run URL parser tests:
```bash
poetry run pytest tests/test_youtube_url_parser.py -v
```

Run YouTube client tests:
```bash
poetry run pytest tests/test_youtube_client.py -v
```

Run import service tests:
```bash
poetry run pytest tests/test_youtube_import_service.py -v
```

Run all Phase 4 tests:
```bash
poetry run pytest tests/test_youtube_* -v
```

---

## Key Features

✅ **URL Validation**: Supports multiple YouTube URL formats
- `https://www.youtube.com/playlist?list=...`
- `https://youtube.com/playlist?list=...`
- `https://m.youtube.com/playlist?list=...`

✅ **API Integration**: Fetches from YouTube Data API v3
- Playlist metadata (title, description, video count)
- All videos with metadata (title, duration, thumbnail)
- Automatic pagination handling
- Error handling with retries

✅ **Database Operations**: Efficient persistence
- Single playlist creation
- Bulk video insertion
- Soft-delete support
- Automatic timestamp tracking

✅ **Error Handling**: Comprehensive error scenarios
- Invalid URLs
- Private playlists
- API quota exceeded
- Authentication failures
- Network timeouts

✅ **Testing**: Full test coverage
- URL parser validation
- YouTube client API calls (mocked)
- Service orchestration
- Error scenarios

---

## Future Phases

### Phase 5: PDF Import
Add support for importing PDFs:
- Create `platform/pdf/` directory
- Implement PDF parser and client
- Add API routes for PDF import

### Phase 6: Transcript Generation
Generate transcripts for videos:
- Extend Video model with transcript fields
- Create TranscriptService
- Add API routes for transcript management

### Phase 7: AI Tutor
AI-powered learning features:
- Personalized recommendations
- Content analysis
- Learning path optimization

---

## Troubleshooting

### Import Error: No module named 'googleapiclient'
```bash
poetry install
```

### API Error: Invalid API Key
- Verify YOUTUBE_API_KEY in .env
- Check YouTube API is enabled in Google Cloud Console
- Ensure API key has permission for YouTube Data API v3

### API Error: Playlist Not Found
- Verify playlist URL is correct
- Ensure playlist is public or unlisted (not private)
- Check playlist ID with browser before importing

### API Error: Quota Exceeded
- YouTube API has daily quotas
- Wait before retrying
- Consider using API quota limits in config

---

## Code Examples

### Parse a YouTube URL

```python
from app.platform.youtube.parser import YouTubeURLParser

url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
playlist_id, source_url = YouTubeURLParser.parse_playlist_url(url)
# Returns: ("PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf", "https://...")
```

### Fetch Playlist Metadata

```python
from app.platform.youtube.client import YouTubeClient

client = YouTubeClient(api_key="your_key")
metadata = await client.fetch_playlist_metadata("PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf")
print(f"Title: {metadata.title}")
print(f"Videos: {metadata.video_count}")
```

### Import Playlist via Service

```python
from app.services.youtube_import import YouTubePlaylistImportService

service = YouTubePlaylistImportService(
    playlist_repository=playlist_repo,
    video_repository=video_repo,
    youtube_client=youtube_client,
    url_parser=url_parser
)

playlist, videos = await service.import_playlist(
    user_id=user_uuid,
    url="https://www.youtube.com/playlist?list=..."
)
print(f"Imported {len(videos)} videos into {playlist.title}")
```

---

## Database Schema

```sql
CREATE TABLE videos (
    id UUID PRIMARY KEY,
    playlist_id UUID NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    youtube_video_id VARCHAR(64) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description VARCHAR(5000),
    thumbnail_url VARCHAR(2048),
    channel_name VARCHAR(255),
    duration_seconds INTEGER,
    position INTEGER,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE INDEX ix_videos_playlist_id,
    UNIQUE INDEX ix_videos_youtube_video_id,
    INDEX ix_videos_position,
    INDEX ix_videos_deleted_at
);
```

---

Last Updated: 2024-06-29
Status: COMPLETE ✅