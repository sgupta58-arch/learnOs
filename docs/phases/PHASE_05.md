# LearnOS — Phase 5: Video Progress Tracking Foundation

## 1. Overview

**Purpose:** Phase 5 introduces the **Video Progress Tracking** system — the persistent, user-specific record of how every user interacts with every imported video.

**Why this phase exists:** This is the point where LearnOS stops being a "YouTube playlist importer" and becomes a **real learning platform**. Everything in future phases — Learning Sessions, AI Tutor, RAG, quizzes, notes, revision, recommendations, analytics — will depend on the data produced here. Without a reliable progress tracking foundation, none of the intelligent learning features can function.

**Future phases depending on this data:**

```
Video Progress
        ↓
Learning Sessions
        ↓
Transcript Processing
        ↓
Notes
        ↓
Flashcards
        ↓
Quiz Engine
        ↓
AI Tutor
        ↓
Adaptive Revision
        ↓
Knowledge Graph
        ↓
Analytics
```

**Key principles:**
- One progress record per user per video (enforced by unique constraint).
- The system remembers start state, playback position, watch time, completion percentage, and completion state.
- All business rules are enforced in the service layer.
- The repository layer performs CRUD only — no business logic.
- Routes remain thin — no SQL, no business logic.

---

## 2. Milestone Documentation

### Milestone 5.1 — VideoProgress Model

**What it does:** Defines the `VideoProgress` SQLAlchemy model representing a single user's progress on a single video.

**Why it belongs in the model layer:** This is a persistence-only class. It defines database columns, constraints, and relationships. Business logic belongs in the service layer.

**Files created:**
- `backend/app/models/video_progress.py` — The `VideoProgress` model class
- Modified: `backend/app/models/enums.py` — Added `VideoProgressStatus` enum
- Modified: `backend/app/models/__init__.py` — Exported new model and enum
- Modified: `backend/app/models/user.py` — Added `video_progress` relationship
- Modified: `backend/app/models/video.py` — Added `progress_records` relationship

**Responsibilities:**
- Define `__tablename__ = "video_progress"`
- Define foreign keys: `user_id`, `video_id` (both CASCADE on delete)
- Define progress fields: `status`, `completion_percentage`, `last_position_seconds`, `watch_time_seconds`
- Define timestamps: `first_started_at`, `last_watched_at`, `completed_at`
- Define unique constraint: `(user_id, video_id)`
- Define index on `status` for efficient filtering
- Inherit audit fields (`created_at`, `updated_at`, `deleted_at`) from `BaseModel`

**Future extensibility:**
- New progress fields can be added as columns without breaking existing records.
- The `VideoProgressStatus` enum can be extended with new states.
- Additional unique constraints or indexes can be added as query patterns evolve.

---

### Milestone 5.2 — Alembic Migration

**What it does:** Creates the `video_progress` table in the database with proper indexes, foreign keys, cascade deletes, and unique constraints.

**Files created:**
- `backend/alembic/versions/005_create_video_progress_table.py`

**Migration details:**
- Revision: `005`
- Down revision: `004`
- Creates table `video_progress` with all columns from the model
- Creates indexes: `ix_video_progress_user_id`, `ix_video_progress_video_id`, `ix_video_progress_status`, `ix_video_progress_deleted_at`
- Creates foreign keys: `user_id -> users.id (CASCADE)`, `video_id -> videos.id (CASCADE)`
- Creates unique constraint: `uq_user_video_progress` on `(user_id, video_id)`
- Supports both `upgrade()` and `downgrade()`

**Future extensibility:**
- Additional indexes can be added in subsequent migrations if new query patterns emerge.
- The table can be extended with new columns via additional migrations.

---

### Milestone 5.3 — Progress Schemas

**What it does:** Defines Pydantic v2 schemas for request validation, response serialization, and progress summaries.

**Files created:**
- `backend/app/schemas/progress.py` — All progress schemas
- Modified: `backend/app/schemas/__init__.py` — Exported new schemas

**Schemas defined:**

| Schema | Purpose |
|--------|---------|
| `ProgressBase` | Shared base fields with validation (completion_percentage 0–100, position/watch_time >= 0) |
| `ProgressCreateSchema` | Schema for creating a new progress record |
| `ProgressUpdateSchema` | Schema for updating progress (all fields optional, validated) |
| `ProgressResponseSchema` | Full response schema including all timestamps |
| `ProgressSummarySchema` | Aggregated progress summary (NOT analytics) |

**Validation rules:**
- `completion_percentage`: 0.0–100.0 (ge=0.0, le=100.0)
- `last_position_seconds`: >= 0 (ge=0)
- `watch_time_seconds`: >= 0 (ge=0)

**Future extensibility:**
- New fields can be added to schemas without breaking backward compatibility (all update fields are optional).
- Additional computed fields can be added to `ProgressSummarySchema`.

---

### Milestone 5.4 — VideoProgressRepository

**What it does:** Provides database access for `VideoProgress` entities implementing CRUD operations and progress-specific queries.

**Files created:**
- `backend/app/repositories/video_progress.py` — The `VideoProgressRepository` class

**Repository methods:**

| Method | Responsibility | Used By |
|--------|---------------|---------|
| `get_by_user_and_video(user_id, video_id)` | Get single progress record by composite key | Service |
| `list_by_playlist(user_id, playlist_id)` | Get all progress records for a user's playlist | Service |
| `list_by_user(user_id)` | Get all progress records for a user | Service |
| `count_completed(user_id, playlist_id)` | Count completed videos in a playlist | Service aggregation |
| `count_in_progress(user_id, playlist_id)` | Count in-progress videos in a playlist | Service aggregation |
| `sum_watch_time(user_id, playlist_id)` | Sum watch time for a user's playlist | Service aggregation |
| `avg_completion(user_id, playlist_id)` | Average completion for a user's playlist | Service aggregation |
| `exists_by_user_and_video(user_id, video_id)` | Efficient existence check | Service |

**What the repository does NOT do:**
- No business logic
- No calculations
- No validation beyond what SQLAlchemy enforces
- No status transitions
- No ownership checks

**Future extensibility:**
- Additional query methods can be added as new features (e.g., transcripts, AI analysis) need data.
- Aggregation methods can be extended with additional grouping or filtering.

---

### Milestone 5.5 — VideoProgressService

**What it does:** Contains all business rules for video progress tracking. This is the most important milestone — the service ensures data integrity.

**Files created:**
- `backend/app/services/video_progress.py` — The `VideoProgressService` class

**Service methods:**

| Method | Purpose |
|--------|---------|
| `get_or_create(user_id, video_id)` | Get existing progress or auto-create a new one |
| `get_progress(user_id, video_id)` | Get progress with ownership validation |
| `update_progress(user_id, video_id, payload)` | Update progress with all business rules |
| `mark_completed(user_id, video_id)` | Convenience method to mark video as completed |
| `resume_playback(user_id, video_id)` | Get last position for resuming playback |
| `get_playlist_progress(user_id, playlist_id)` | Aggregated playlist progress summary |
| `get_user_progress(user_id)` | All progress records for a user |

**Business rules enforced:**

1. **Video must exist** — Before creating or updating progress, the video is verified.
2. **Auto-creation** — Progress record is created on first interaction if none exists.
3. **watch_time cannot decrease** — Prevents replay manipulation (critical for accurate analytics).
4. **completion_percentage clamped 0–100** — Validated by Pydantic, enforced by service.
5. **Status transitions:**

   ```
   NOT_STARTED
        ↓  (on any activity: watch_time > 0, or explicit status update)
   IN_PROGRESS
        ↓  (on explicit COMPLETED status, or completion_percentage == 100)
   COMPLETED
   ```

6. **completed_at set only first time** — Once set, it never changes. This preserves the original completion timestamp.
7. **first_started_at set on first interaction** — Records when the user first engaged with the video.
8. **last_watched_at updated on every interaction** — Provides current "last seen" timestamp.
9. **Ownership validation** — Every operation verifies the progress record belongs to the requesting user.
10. **Auto-transition at 100%** — If `completion_percentage` reaches 100, status auto-transitions to COMPLETED.
11. **Auto-transition on activity** — If there's any watch time but status is still NOT_STARTED, it transitions to IN_PROGRESS.

**How future phases will use it:**
- **Learning Sessions:** Will call `resume_playback()` at session start, `update_progress()` periodically.
- **AI Tutor:** Will call `get_playlist_progress()` to personalize tutoring based on completion.
- **Analytics:** Will call `get_user_progress()` and aggregation methods to compute insights.

---

### Milestone 5.6 — API Endpoints

**What it does:** Exposes REST endpoints for progress operations. Routes are thin — they parse requests, call the service, and serialize responses.

**Files created:**
- `backend/app/api/v1/progress.py` — Progress API routes
- Modified: `backend/app/api/v1/router.py` — Registered progress router

**Endpoints:**

| Method | Path | Purpose |
|--------|------|---------|
| `PATCH` | `/api/v1/videos/{video_id}/progress` | Update video progress |
| `GET` | `/api/v1/videos/{video_id}/progress` | Get video progress |
| `GET` | `/api/v1/playlists/{playlist_id}/progress` | Get playlist progress summary |
| `GET` | `/api/v1/users/me/progress` | Get all user progress |

**What routes do NOT do:**
- No SQL queries
- No business logic
- No calculations
- No data transformation (beyond response serialization)

---

### Milestone 5.7 — Progress Aggregation

**What it does:** Implements service methods that compute playlist-level and user-level progress summaries.

**Aggregation methods (in `VideoProgressService`):**

| Method | Returns |
|--------|---------|
| `get_playlist_progress()` | `ProgressSummarySchema` with total, completed, in_progress, not_started counts, total watch time, average completion, estimated remaining time |
| `get_user_progress()` | `list[ProgressResponseSchema]` — all progress records for a user |

**IMPORTANT:** This is NOT analytics. It returns raw computed summaries. Analytics (charts, dashboards, trends) will be built in a future phase.

**How future phases will use it:**
- **Analytics:** Will consume `ProgressSummarySchema` data to compute learning insights.
- **AI Tutor:** Will use completion data to determine which topics need reinforcement.
- **Recommendation Engine:** Will use watch time and completion rates to recommend content.

---

### Milestone 5.8 — Dependency Injection

**What it does:** Wires the repository and service into the FastAPI dependency injection system, following the same pattern as existing dependencies.

**Files created:**
- `backend/app/dependencies/video_progress.py` — Dependency factories

**Dependency chain:**

```
get_db (session)
    ↓
get_video_progress_repository (VideoProgressRepository)
    ↓
get_video_progress_service (VideoProgressService)
    └── VideoRepository (for video lookups)
```

**Why this pattern:** Maintains the existing Clean Architecture approach. Each layer is independently testable. Dependencies can be overridden for testing.

---

### Milestone 5.9 — Tests

**What it does:** Comprehensive test suite covering models, repository, service, and API routes.

**Files created:**
- `backend/tests/test_video_progress_model.py` — Model tests (6 tests)
- `backend/tests/test_video_progress_repository.py` — Repository tests (11 tests)
- `backend/tests/test_video_progress_service.py` — Service tests (16 tests)
- `backend/tests/test_video_progress_api.py` — API tests (11 tests)

**Total: 44 tests**

---

## 3. Files Created

| File | Responsibility |
|------|---------------|
| `backend/app/models/video_progress.py` | VideoProgress SQLAlchemy model |
| `backend/app/schemas/progress.py` | Pydantic schemas for progress data |
| `backend/app/repositories/video_progress.py` | Database access for VideoProgress |
| `backend/app/services/video_progress.py` | All business logic for progress tracking |
| `backend/app/api/v1/progress.py` | Thin REST API routes for progress operations |
| `backend/app/dependencies/video_progress.py` | Dependency injection factories |
| `backend/alembic/versions/005_create_video_progress_table.py` | Database migration |
| `backend/tests/test_video_progress_model.py` | Model unit tests |
| `backend/tests/test_video_progress_repository.py` | Repository integration tests |
| `backend/tests/test_video_progress_service.py` | Service unit tests |
| `backend/tests/test_video_progress_api.py` | API integration tests |
| `docs/phases/PHASE_05.md` | This documentation file |

**Files modified:**

| File | Change |
|------|--------|
| `backend/app/models/enums.py` | Added `VideoProgressStatus` enum |
| `backend/app/models/__init__.py` | Exported new model and enum |
| `backend/app/models/user.py` | Added `video_progress` relationship |
| `backend/app/models/video.py` | Added `progress_records` relationship |
| `backend/app/schemas/__init__.py` | Exported new schemas |
| `backend/app/api/v1/router.py` | Registered progress router |

---

## 4. Database Changes

### New Table: `video_progress`

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | UUID | PK, default uuid4 | Primary key |
| `user_id` | UUID | FK → users.id (CASCADE), NOT NULL, INDEX | User who owns the progress |
| `video_id` | UUID | FK → videos.id (CASCADE), NOT NULL, INDEX | Video being tracked |
| `status` | String(50) | NOT NULL, DEFAULT 'not_started', INDEX | Progress status enum |
| `completion_percentage` | Float | NOT NULL, DEFAULT 0.0 | Percentage watched (0–100) |
| `last_position_seconds` | Integer | NOT NULL, DEFAULT 0 | Last playback position |
| `watch_time_seconds` | Integer | NOT NULL, DEFAULT 0 | Total time watched |
| `first_started_at` | DateTime(tz) | NULLABLE | First interaction timestamp |
| `last_watched_at` | DateTime(tz) | NULLABLE | Most recent interaction timestamp |
| `completed_at` | DateTime(tz) | NULLABLE | First completion timestamp |
| `created_at` | DateTime(tz) | NOT NULL, server_default now() | Record creation timestamp |
| `updated_at` | DateTime(tz) | NOT NULL, server_default now() | Record update timestamp |
| `deleted_at` | DateTime(tz) | NULLABLE | Soft delete timestamp |

**Indexes:**

| Name | Columns | Purpose |
|------|---------|---------|
| `ix_video_progress_user_id` | `user_id` | Fast lookup by user |
| `ix_video_progress_video_id` | `video_id` | Fast lookup by video |
| `ix_video_progress_status` | `status` | Fast filtering by status |
| `ix_video_progress_deleted_at` | `deleted_at` | Soft delete support |

**Constraints:**

| Name | Type | Columns |
|------|------|---------|
| PK | Primary Key | `id` |
| FK (user) | Foreign Key | `user_id` → `users.id` (CASCADE) |
| FK (video) | Foreign Key | `video_id` → `videos.id` (CASCADE) |
| `uq_user_video_progress` | Unique | `(user_id, video_id)` |

**Relationship Diagram:**

```
users (1) ──── (N) video_progress (N) ──── (1) videos
```

**Migration details:**
- Revision: `005`
- Down revision: `004`
- Full `upgrade()` and `downgrade()` support

---

## 5. API Endpoints

### PATCH `/api/v1/videos/{video_id}/progress`

**Purpose:** Update the current user's progress for a specific video.

**Authentication:** Required (placeholder until auth is wired)

**Request body:** `ProgressUpdateSchema`
```json
{
  "status": "in_progress",
  "completion_percentage": 50.0,
  "last_position_seconds": 120,
  "watch_time_seconds": 120
}
```

All fields are optional. Only provided fields are updated.

**Response:** `ProgressResponseSchema` (200)
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "video_id": "uuid",
  "status": "in_progress",
  "completion_percentage": 50.0,
  "last_position_seconds": 120,
  "watch_time_seconds": 120,
  "first_started_at": "2026-06-30T12:00:00Z",
  "last_watched_at": "2026-06-30T12:00:00Z",
  "completed_at": null,
  "created_at": "2026-06-30T12:00:00Z",
  "updated_at": "2026-06-30T12:00:00Z"
}
```

**Error responses:**
- 400: Bad request (e.g., video not found, invalid data)
- 422: Validation error (e.g., completion_percentage > 100)

**Business rules applied:**
- Auto-creates progress record if none exists
- watch_time cannot decrease
- Status transitions follow: NOT_STARTED → IN_PROGRESS → COMPLETED
- completed_at set only first time
- first_started_at set on first interaction
- last_watched_at updated on every interaction

---

### GET `/api/v1/videos/{video_id}/progress`

**Purpose:** Get the current user's progress for a specific video.

**Authentication:** Required (placeholder until auth is wired)

**Response:** `ProgressResponseSchema` (200)

**Error responses:**
- 404: Video or progress record not found

---

### GET `/api/v1/playlists/{playlist_id}/progress`

**Purpose:** Get an aggregated progress summary for a playlist.

**Authentication:** Required (placeholder until auth is wired)

**Response:** `ProgressSummarySchema` (200)
```json
{
  "total_videos": 10,
  "completed_videos": 3,
  "in_progress_videos": 2,
  "not_started_videos": 5,
  "total_watch_time_seconds": 3600,
  "average_completion_percentage": 30.0,
  "estimated_remaining_seconds": 5400
}
```

**Error responses:**
- 404: Playlist not found or access denied

**Note:** This is NOT analytics. It returns raw computed summaries.

---

### GET `/api/v1/users/me/progress`

**Purpose:** Get all progress records for the current user.

**Authentication:** Required (placeholder until auth is wired)

**Response:** `list[ProgressResponseSchema]` (200)

Returns an empty list if the user has no progress records.

---

## 6. Architecture Review

### Clean Architecture Compliance

```
Routes (api/v1/progress.py)
    ↓  Thin — no SQL, no business logic
Services (services/video_progress.py)
    ↓  All business logic, orchestration
Repositories (repositories/video_progress.py)
    ↓  CRUD only — no business logic
Database (via SQLAlchemy + Alembic)
```

### Verification Checklist

| Layer | Requirement | Status |
|-------|------------|--------|
| Routes | Contain no SQL | ✅ |
| Routes | Contain no business logic | ✅ |
| Repositories | Contain no business logic | ✅ |
| Repositories | CRUD-only operations | ✅ |
| Services | Contain all business rules | ✅ |
| DI | Follows existing pattern | ✅ |
| Naming | Consistent with existing code | ✅ |
| Architecture | No regressions introduced | ✅ |

### Specific Checks

- **Routes contain no SQL:** All routes in `progress.py` delegate to `VideoProgressService`.
- **Repositories contain no business logic:** `VideoProgressRepository` only performs SELECT, INSERT, UPDATE, soft_delete operations. No status transitions, no calculations.
- **Services contain all business logic:** `VideoProgressService` enforces all 11 business rules (status transitions, watch_time protection, completed_at immutability, auto-creation, ownership validation).
- **Dependency Injection:** Uses the same pattern as `video.py`, `playlist.py` — `Depends(get_db)` → repository → service.
- **Model is persistence-only:** `VideoProgress` only defines columns, constraints, relationships. No methods with business logic.

---

## 7. Testing

### Test Coverage

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_video_progress_model.py` | 6 | Model creation, defaults, unique constraint, cascade delete, enums, repr |
| `test_video_progress_repository.py` | 11 | Create, get_by_user_and_video, list_by_playlist, list_by_user, count queries, aggregation, soft delete filtering |
| `test_video_progress_service.py` | 16 | get_or_create, get_progress, update_progress (watch time, transitions, auto-complete, auto-in-progress), mark_completed, resume_playback, aggregation, ownership, edge cases |
| `test_video_progress_api.py` | 11 | PATCH success, GET success, GET playlist summary, GET user progress, validation errors, not found, empty results, schema validation |
| **Total** | **44** | |

### Important Edge Cases Tested

1. **completion_percentage > 100** — Rejected by Pydantic validation (422 in API, ValueError in schema)
2. **completion_percentage = 100** — Auto-transitions to COMPLETED status
3. **watch_time cannot decrease** — Service ignores lower values
4. **completed_at only set first time** — Immutable after initial set
5. **first_started_at set on first interaction** — Timestamp captured once
6. **Ownership validation** — ForbiddenException raised for wrong user
7. **Video not found** — NotFoundException raised
8. **Progress not found** — NotFoundException raised
9. **Empty user progress** — Returns empty list, not error
10. **Soft delete filtering** — Deleted records excluded from queries
11. **Duplicate progress records prevented** — Unique constraint enforced

### How to Run Tests

```bash
# Run all progress tests
cd backend
poetry run pytest tests/test_video_progress_model.py -v
poetry run pytest tests/test_video_progress_repository.py -v
poetry run pytest tests/test_video_progress_service.py -v
poetry run pytest tests/test_video_progress_api.py -v

# Run all tests
poetry run pytest -v
```

---

## 8. Future Integration

### Data Flow: Phase 5 → All Future Phases

```
Video Progress (Phase 5)
        │
        ├──→ Learning Sessions (Phase 6)
        │      • Resume playback from last position
        │      • Update progress during session
        │      • Mark completed at session end
        │
        ├──→ Transcript Processing (Phase 7)
        │      • Process unprocessed videos first
        │      • Skip completed videos
        │
        ├──→ Notes (Phase 8)
        │      • Context-aware note creation based on position
        │      • Notes linked to specific video segments
        │
        ├──→ Flashcards (Phase 9)
        │      • Generate cards for in-progress videos
        │      • Spaced repetition based on completion
        │
        ├──→ Quiz Engine (Phase 10)
        │      • Generate quizzes from in-progress content
        │      • Track quiz performance by video
        │
        ├──→ AI Tutor (Phase 11)
        │      • Personalize tutoring based on progress
        │      • Focus on incomplete or struggling areas
        │
        ├──→ Adaptive Revision (Phase 12)
        │      • Review older completed videos
        │      • Spaced repetition based on watch time
        │
        ├──→ Knowledge Graph (Phase 13)
        │      • Visualize learning journey
        │      • Show completed vs pending topics
        │
        └──→ Analytics (Phase 14)
               • Learning velocity (videos/time)
               • Completion rates
               • Watch time trends
               • Playlist completion forecasts
```

### Integration Patterns

**How future phases will consume progress data:**

1. **Direct service injection:** Future services will inject `VideoProgressService` via dependency injection to query and update progress data.
2. **Repository reuse:** Future repositories can use `VideoProgressRepository` if they need direct database access (for batch operations or complex queries).
3. **Schema reuse:** Future schemas will use `ProgressResponseSchema` and `ProgressSummarySchema` as embedded fields in their own response schemas.

**Example integration (Learning Sessions):**

```python
class LearningSession:
    def __init__(self, progress_service: VideoProgressService):
        self.progress_service = progress_service
    
    async def start_session(self, user_id, video_id):
        # Resume from last position
        progress = await self.progress_service.resume_playback(user_id, video_id)
        
        # Create session record with start position
        return LearningSession(
            user_id=user_id,
            video_id=video_id,
            start_position=progress.last_position_seconds,
        )
    
    async def end_session(self, user_id, video_id, end_position, watch_time):
        # Update progress with final position
        await self.progress_service.update_progress(
            user_id=user_id,
            video_id=video_id,
            payload=ProgressUpdateSchema(
                last_position_seconds=end_position,
                watch_time_seconds=watch_time,
            ),
        )
```

---

## 9. Key Design Decisions

### Why a separate VideoProgress model was introduced

**Decision:** Progress is stored in its own `video_progress` table, not as columns on the `videos` table.

**Rationale:**
- **Separation of concerns:** `videos` represents content; `video_progress` represents user interaction. These are fundamentally different concepts.
- **Scalability:** A video may have many users watching it. Storing progress on the `videos` table would require multiple columns per user or complex denormalization.
- **Performance:** Progress queries (per user, per playlist) don't interfere with video content queries.
- **Flexibility:** Future progress-related fields can be added without touching the `videos` table.

### Why progress is not stored on the Video model

**Decision:** Each `VideoProgress` record is a separate entity with its own primary key.

**Rationale:**
- **One progress record per user per video:** The unique constraint `(user_id, video_id)` ensures exactly one record per pair. This is cleaner than having user-specific columns on the video.
- **Cascade deletes:** When a user or video is deleted, all associated progress records are automatically cleaned up.
- **Soft delete support:** Progress records can be soft-deleted independently of videos.

### Why completion_percentage is stored

**Decision:** `completion_percentage` is stored as a float (0.0–100.0) rather than computed from `watch_time_seconds / duration_seconds`.

**Rationale:**
- **User-controlled completion:** Users may mark videos as complete without watching the entire duration (e.g., they already know the content).
- **Partial watching:** A user may watch 100% of a video but skip sections.
- **Decoupling:** Video duration can change (e.g., re-uploaded with different length). Storing completion independently avoids inconsistencies.
- **Accuracy:** Floating point precision allows for granular progress tracking (0.1% increments).

### Why timestamps are required

**Decision:** Three separate timestamps: `first_started_at`, `last_watched_at`, `completed_at`.

**Rationale:**
- **`first_started_at`:** Captures when the user first engaged. Critical for computing "time to completion" metrics.
- **`last_watched_at`:** Updated on every interaction. Provides "last seen" for session management and activity tracking.
- **`completed_at`:** Set only once on first completion. Immutable — preserves the original completion timestamp even if the user re-watches.

### Why business rules belong in the service layer

**Decision:** All business rules (status transitions, watch_time protection, completion immutability) are enforced in `VideoProgressService`, not in the model or repository.

**Rationale:**
- **Testability:** Business rules in the service layer can be unit-tested with mocked repositories.
- **Separation of concerns:** The model defines structure; the repository handles persistence; the service handles behavior.
- **Consistency:** All entry points (API routes, future services, CLI commands) go through the same service, ensuring consistent rule enforcement.
- **Flexibility:** Business rules can change without modifying the database schema or the repository interface.

### Why aggregation is in the service, not repository

**Decision:** `get_playlist_progress()` in `VideoProgressService` orchestrates multiple repository calls and computes the summary.

**Rationale:**
- The service owns the "what does playlist progress mean" business logic.
- The repository provides raw data (counts, sums, averages); the service combines them into a meaningful summary.
- The repository remains a CRUD layer — it doesn't know about "playlists" or "progress summaries."

---

## 10. Completion Checklist

- ✅ **Model** — `VideoProgress` model with all fields, constraints, relationships
- ✅ **Migration** — Alembic migration 005 with indexes, FKs, unique constraint
- ✅ **Schemas** — Pydantic v2 schemas with validation (0–100%, >= 0 position/time)
- ✅ **Repository** — `VideoProgressRepository` with CRUD and aggregation methods
- ✅ **Service** — `VideoProgressService` with all business rules (transitions, immutability, ownership, auto-creation)
- ✅ **Routes** — 4 thin REST endpoints delegating to service
- ✅ **Dependencies** — Dependency injection wired following existing pattern
- ✅ **Tests** — 44 tests covering model, repository, service, API, and edge cases
- ✅ **Documentation** — This file (`docs/phases/PHASE_05.md`)
- ✅ **Architecture Review** — Clean Architecture maintained: routes thin, repositories CRUD-only, services contain business logic, DI unchanged

---

*This document is the official engineering handoff for Phase 5. It serves as the foundation for all future learning features.*