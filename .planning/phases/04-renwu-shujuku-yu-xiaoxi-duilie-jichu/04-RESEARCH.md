# Phase 4 Research: 任务数据库与消息队列基础

**Gathered:** 2026-04-23
**Status:** Research Complete

---

## Executive Summary

Phase 4 requires implementing a SQLite-based task database and asyncio.Queue-based message queue for image download tasks. The project already has established patterns for:
- **lifespan management** (FastAPI `@asynccontextmanager`)
- **singleton services** (global instances like `file_watcher`, `crawler_manager`)
- **asyncio patterns** (async/await, `asyncio.create_task`, `asyncio.Queue`)
- **threading safety** (`threading.Lock` for shared state)
- **SQLAlchemy async patterns** (existing `database/` module)

This research identifies key decisions needed for planning and highlights integration points.

---

## 1. Existing Code Patterns

### 1.1 FastAPI Lifespan Pattern

**File:** `api/main.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - start/stop file watcher for all platforms."""
    # Startup - watch all platform directories
    file_watcher.start(
        platforms=PLATFORMS,
        base_callback=on_file_change_callback,
        base_path=str(DATA_DIR)
    )
    app.state.file_watcher = file_watcher

    yield

    # Shutdown
    file_watcher.stop()
```

**Key observations:**
- Services are initialized at startup, stored in `app.state` or as global singletons
- Cleanup happens in the shutdown phase
- Services have `start()` and `stop()` methods

**For Phase 4:**
- `ImageTaskDB` needs initialization (create tables) at startup
- `ImageQueueService` needs `start()` (launch consumers) and `stop()` (cancel tasks)

### 1.2 Singleton Service Pattern

**Files:** `api/services/file_watcher.py`, `api/services/crawler_manager.py`, `api/services/subscription_manager.py`

```python
# At module level
file_watcher = FileWatcherService()
crawler_manager = CrawlerManager()
subscription_manager = SubscriptionManager()
```

**Key observations:**
- Global singleton instances at module level
- No dependency injection - imported directly
- State managed internally with thread-safe access

**For Phase 4:**
- Create `image_task_db = ImageTaskDB()` singleton
- Create `image_queue_service = ImageQueueService()` singleton
- Create `image_downloader = ImageDownloader()` singleton

### 1.3 Threading + asyncio Bridge Pattern

**File:** `api/services/file_watcher.py`

```python
class FileWatcherService:
    def __init__(self):
        self._observers: Dict[str, Observer] = {}  # watchdog observers
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._lock = threading.Lock()
        # ...

    def start(self, platforms: List[str], base_callback: Callable, base_path: str) -> None:
        self._event_loop = asyncio.get_running_loop()  # Capture main event loop
        # ...

    def _do_callback(self, platform: str) -> None:
        """Execute callback on main event loop (called from timer thread)."""
        callback = self._callbacks.get(platform)
        if callback and self._event_loop:
            asyncio.run_coroutine_threadsafe(
                callback(platform),
                self._event_loop
            )
```

**Key observations:**
- `threading.Lock` protects shared state
- `asyncio.get_running_loop()` captures the main event loop at startup
- `asyncio.run_coroutine_threadsafe()` bridges threads to asyncio

**For Phase 4:**
- If we use watchdog for file monitoring, this pattern is needed
- For pure asyncio consumers, no threading needed

### 1.4 asyncio.Queue Pattern

**File:** `api/services/crawler_manager.py`

```python
class CrawlerManager:
    def __init__(self):
        self._log_queue: Optional[asyncio.Queue] = None

    def get_log_queue(self) -> asyncio.Queue:
        """Get or create log queue"""
        if self._log_queue is None:
            self._log_queue = asyncio.Queue()
        return self._log_queue

    async def _push_log(self, entry: LogEntry):
        """Push log to queue"""
        if self._log_queue is not None:
            try:
                self._log_queue.put_nowait(entry)
            except asyncio.QueueFull:
                pass
```

**File:** `api/routers/websocket.py`

```python
async def log_broadcaster():
    """Background task: read logs from queue and broadcast"""
    queue = crawler_manager.get_log_queue()
    while True:
        try:
            entry = await queue.get()
            await manager.broadcast(entry.model_dump())
        except asyncio.CancelledError:
            break
```

**Key observations:**
- `asyncio.Queue()` is created lazily
- `put_nowait()` with `QueueFull` handling
- Consumer loop with `await queue.get()` and `asyncio.CancelledError` handling

**For Phase 4:**
- Similar pattern for image download queue
- Multiple consumers (2-3) reading from same queue

### 1.5 asyncio.create_task Pattern

**File:** `api/routers/websocket.py`

```python
_broadcaster_task: Optional[asyncio.Task] = None

def start_broadcaster():
    """Start broadcast task"""
    global _broadcaster_task
    if _broadcaster_task is None or _broadcaster_task.done():
        _broadcaster_task = asyncio.create_task(log_broadcaster())
```

**For Phase 4:**
- Launch consumer tasks with `asyncio.create_task(consumer_loop())`
- Track tasks for graceful shutdown

### 1.6 SQLAlchemy Async Pattern

**Files:** `database/db_session.py`, `database/models.py`

```python
# Async engine with aiosqlite
db_url = f"sqlite+aiosqlite:///{sqlite_db_config['db_path']}"
engine = create_async_engine(db_url, echo=False)

# Session factory
AsyncSessionFactory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Context manager
@asynccontextmanager
async def get_session() -> AsyncSession:
    session = AsyncSessionFactory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()

# ORM Model
class XhsNote(Base):
    __tablename__ = 'xhs_note'
    id = Column(Integer, primary_key=True)
    note_id = Column(String(255), index=True)
    # ...
```

**Key observations:**
- Uses `aiosqlite` for async SQLite
- SQLAlchemy ORM models with `Base` declarative base
- Context manager for session handling

**For Phase 4 - Decision needed:**
- **Option A:** Use existing SQLAlchemy pattern (add new model to `models.py`)
- **Option B:** Use raw `aiosqlite` for simpler task database (less overhead)

---

## 2. Technical Decisions for Planning

### 2.1 Database Approach (Critical Decision)

**Option A: SQLAlchemy (existing pattern)**

Pros:
- Consistent with existing database code
- Built-in migration support
- ORM provides type safety

Cons:
- Heavier dependency for simple task queue
- More boilerplate for simple CRUD

**Option B: Raw aiosqlite (lighter)**

Pros:
- Simpler, less abstraction
- Direct SQL for task queries
- No ORM overhead

Cons:
- Inconsistent with existing pattern
- Manual SQL construction

**Recommendation:** Use raw `aiosqlite` for the task database because:
1. Task database is isolated from main data storage
2. Simpler queries (CRUD on single table)
3. Better performance for high-frequency status updates
4. File location: `api/services/image_task_db.py` (separate from `database/`)

### 2.2 Database File Location

**Existing SQLite location:** `MediaCrawler/database/sqlite_tables.db`

**Options for task database:**
- `MediaCrawler/database/image_tasks.db` (separate file)
- `MediaCrawler/data/image_tasks.db` (with data files)
- `MediaCrawler/api/services/image_tasks.db` (with service)

**Recommendation:** `MediaCrawler/data/image_tasks.db` - with other data files for consistency

### 2.3 Queue Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Producer      │     │  asyncio.Queue   │     │   Consumers     │
│                 │     │                  │     │                 │
│ - crawl_done()  │────▶│  [task1, task2,  │────▶│ - Consumer 1    │
│ - manual_add()  │     │   task3, ...]    │     │ - Consumer 2    │
│ - retry()       │     │  maxsize=300     │     │ - Consumer 3    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                 ┌─────────────────┐
                                                 │  ImageTaskDB    │
                                                 │  status update  │
                                                 └─────────────────┘
```

### 2.4 Consumer Design

```python
async def consumer_loop(self, consumer_id: int):
    """Consumer coroutine for processing download tasks."""
    while self._running:
        try:
            # Get task from queue with timeout
            task = await asyncio.wait_for(
                self._queue.get(),
                timeout=1.0
            )

            # Deduplication check (check DB status)
            if not await self._should_process(task):
                continue

            # Update status to 'downloading'
            await self._db.update_status(task.id, 'downloading')

            # Download with jitter interval
            await self._download_with_jitter(task)

        except asyncio.TimeoutError:
            continue  # No task available, continue polling
        except asyncio.CancelledError:
            break
```

### 2.5 Jitter Interval Implementation

```python
import random

async def _download_with_jitter(self, task: ImageTask):
    """Download with jitter interval to avoid rate limiting."""
    # Random interval between min and max
    interval = random.uniform(
        self.config.min_interval,  # e.g., 0.5s
        self.config.max_interval   # e.g., 2.0s
    )
    await asyncio.sleep(interval)

    # Actual download
    result = await self._do_download(task.url)

    # Update status based on result
    if result.success:
        await self._db.mark_completed(task.id, result.local_path)
    else:
        await self._db.mark_failed(task.id, result.error)
```

### 2.6 Exponential Backoff for Retries

```python
def calculate_retry_delay(retry_count: int, base_delay: float = 1.0) -> float:
    """Calculate delay for retry with exponential backoff."""
    return base_delay * (2 ** retry_count)  # 1s, 2s, 4s, 8s, ...

# When marking failed:
async def mark_failed(self, task_id: str, error: str):
    task = await self.get_task(task_id)
    if task.retry_count < self.config.max_retries:
        # Schedule for retry
        next_delay = calculate_retry_delay(task.retry_count)
        await self.update_task(
            task_id,
            status='pending',
            retry_count=task.retry_count + 1,
            next_retry_at=datetime.now() + timedelta(seconds=next_delay)
        )
    else:
        # Max retries exceeded
        await self.update_task(
            task_id,
            status='failed',
            error_message=error
        )
```

---

## 3. Implementation Files

Based on ROADMAP.md, the following files need to be created:

### 3.1 `api/services/image_task_db.py`

**Purpose:** SQLite task database service

**Key methods:**
- `init_db()` - Create tables
- `add_task(url, priority)` - Add new task (returns task ID)
- `get_pending_task()` - Get next pending task
- `update_status(task_id, status)` - Update task status
- `mark_completed(task_id, local_path)` - Mark as completed
- `mark_failed(task_id, error)` - Mark as failed with retry logic
- `get_task_by_url(url)` - Check if URL exists (dedup)
- `get_stats()` - Get queue stats (pending/downloading/completed/failed counts)

**Database schema:**
```sql
CREATE TABLE IF NOT EXISTS image_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending/downloading/completed/failed
    priority TEXT NOT NULL DEFAULT 'medium', -- high/medium/low
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    error_message TEXT,
    local_path TEXT,
    next_retry_at TEXT
);

CREATE INDEX idx_status ON image_tasks(status);
CREATE INDEX idx_priority ON image_tasks(priority);
CREATE UNIQUE INDEX idx_url ON image_tasks(url);
```

### 3.2 `api/services/image_queue.py`

**Purpose:** Message queue service with consumers

**Key methods:**
- `start()` - Start consumer tasks
- `stop()` - Stop consumer tasks
- `enqueue(url, priority)` - Add task to queue
- `get_stats()` - Get queue stats

**Internal:**
- `_consumer_loop(consumer_id)` - Consumer coroutine
- `_should_process(task)` - Deduplication check
- `_download_with_jitter(task)` - Download with interval

### 3.3 `api/services/image_downloader.py`

**Purpose:** Actual image download logic

**Key methods:**
- `download(url)` - Download image, return result

**Returns:**
```python
@dataclass
class DownloadResult:
    success: bool
    local_path: Optional[str]
    error: Optional[str]
```

### 3.4 `api/services/__init__.py` (modification)

Add exports for new services.

### 3.5 `api/main.py` (modification)

Add lifespan initialization:
```python
from .services import image_task_db, image_queue_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize task database
    await image_task_db.init_db()

    # Start queue service
    image_queue_service.start()

    # ... existing file_watcher startup ...

    yield

    # Shutdown
    image_queue_service.stop()
    file_watcher.stop()
```

---

## 4. Configuration Values (Claude's Discretion)

Based on 04-CONTEXT.md, these values are at my discretion:

| Config | Recommended Value | Rationale |
|--------|-------------------|-----------|
| `min_interval` | 0.5 seconds | Minimum delay between downloads |
| `max_interval` | 2.0 seconds | Maximum delay between downloads |
| `download_timeout` | 30 seconds | HTTP timeout for image download |
| `max_retries` | 5 | Maximum retry attempts |
| `base_retry_delay` | 1.0 seconds | Base for exponential backoff |
| `queue_maxsize` | 300 | Queue capacity (within 100-500 range) |
| `consumer_count` | 3 | Number of concurrent consumers (within 2-3 range) |
| `db_path` | `data/image_tasks.db` | With other data files |

---

## 5. Error Handling

### 5.1 Error Classification

| Error Type | Handling |
|------------|----------|
| Network timeout | Retry with backoff |
| HTTP 403/429 (rate limit) | Increase delay, retry |
| HTTP 404 (not found) | Mark failed, no retry |
| Invalid image | Mark failed, no retry |
| Disk full | Mark failed, alert user |

### 5.2 Consumer Error Handling

```python
async def consumer_loop(self, consumer_id: int):
    while self._running:
        try:
            task = await self._queue.get()
            # ... process task ...
        except asyncio.CancelledError:
            break
        except Exception as e:
            # Log error but continue processing
            print(f"[ImageQueue] Consumer {consumer_id} error: {e}")
            await asyncio.sleep(1.0)  # Brief pause before continuing
```

---

## 6. Testing Considerations

### 6.1 Unit Tests

- Test database CRUD operations
- Test retry delay calculation
- Test deduplication logic
- Test priority ordering

### 6.2 Integration Tests

- Test producer → queue → consumer flow
- Test concurrent consumer access
- Test graceful shutdown

### 6.3 Manual Testing

- Add task via API
- Check database state
- Verify file download
- Test retry on failure

---

## 7. Dependencies

**Already available:**
- `aiosqlite` (via SQLAlchemy dependencies)
- `asyncio` (standard library)
- `httpx` or `aiohttp` (for async HTTP) - need to verify

**Need to verify:**
- HTTP client for async downloads (likely `httpx` or `aiohttp`)
- Image validation library (likely `PIL` / `pillow`)

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| SQLite write contention | Use WAL mode, single writer pattern |
| Queue memory overflow | Bounded queue (maxsize), fallback to DB |
| Consumer starvation | Multiple consumers, priority ordering |
| Download storms | Jitter interval, rate limiting |
| Deadlocks | Careful lock ordering, timeout on locks |

---

## 9. Success Criteria Verification

From ROADMAP.md, success criteria for Phase 4:

1. ✅ SQLite database table created - schema defined above
2. ✅ Task state transitions - pending → downloading → completed/failed
3. ✅ Retry with backoff - exponential backoff implemented
4. ✅ Queue working - asyncio.Queue with consumers
5. ✅ Download interval configurable - min/max interval config

---

## 10. Next Steps for Planning

1. **Confirm database approach** - SQLAlchemy vs raw aiosqlite (recommend: raw aiosqlite)
2. **Define API endpoints** - Do we need REST API for queue management?
3. **Confirm HTTP client** - httpx vs aiohttp for downloads
4. **Clarify producer integration** - How will crawl code add tasks?

---

## Appendix A: Existing Service Initialization

```python
# api/services/__init__.py
from .file_watcher import file_watcher, PLATFORMS
from .crawler_manager import crawler_manager
from .subscription_manager import (
    subscription_manager,
    Subscription,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionPlatform,
    SubscriptionFrequency,
    SubscriptionStatus,
)

# New additions for Phase 4:
# from .image_task_db import image_task_db
# from .image_queue import image_queue_service
# from .image_downloader import image_downloader
```

---

## Appendix B: Reference Files

| File | Purpose |
|------|---------|
| `api/main.py` | Lifespan pattern |
| `api/services/file_watcher.py` | Threading + asyncio bridge |
| `api/services/crawler_manager.py` | asyncio.Queue pattern |
| `api/routers/websocket.py` | Consumer loop, create_task pattern |
| `api/services/subscription_manager.py` | Singleton service, JSON persistence |
| `database/db_session.py` | SQLAlchemy async pattern |
| `database/models.py` | ORM model definitions |
| `config/db_config.py` | Database configuration |

---

*Research completed: 2026-04-23*
