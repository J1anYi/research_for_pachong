---
wave: 1
depends_on: []
files_modified:
  - api/services/image_task_db.py (新建)
  - api/services/__init__.py (修改)
  - api/main.py (修改)
autonomous: true
requirements:
  - TASK-01
  - TASK-02
  - TASK-03
  - TASK-04
  - QUEUE-01
  - QUEUE-02
  - QUEUE-03
  - QUEUE-04
---

# Phase 4: 任务数据库与消息队列基础

**Goal:** 建立图片下载任务的基础架构 — SQLite 任务数据库、asyncio.Queue 消息队列、下载消费者 Listener、抖动间隔下载、并发控制。

**Success Criteria:**
1. SQLite 数据库表创建成功，包含所有必要字段
2. 任务状态可正确转换（pending → downloading → completed/failed）
3. 失败任务可自动重试，遵循指数退避策略
4. 消息队列正常工作，消费者能处理消息
5. 下载间隔可配置，避免触发限流

**must_haves:**
- `image_tasks` 表存在且结构正确
- 任务 CRUD 操作正常
- 队列能接收和分发任务
- 消费者能处理下载任务
- 抖动间隔配置生效
- 并发控制有效

---

## Task 1: 创建 SQLite 任务数据库服务

<read_first>
- api/services/file_watcher.py (单例模式、服务初始化模式)
- api/services/crawler_manager.py (asyncio.Lock、日志格式)
- api/main.py (lifespan 集成方式)
- api/services/__init__.py (导出模式)
</read_first>

<action>
创建 `api/services/image_task_db.py`，实现 SQLite 任务数据库服务：

1. **数据类定义**：
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ImageTask:
    id: int
    url: str
    status: TaskStatus
    priority: TaskPriority
    retry_count: int
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    local_path: Optional[str] = None
    next_retry_at: Optional[datetime] = None
```

2. **ImageTaskDB 类**：
```python
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "image_tasks.db"

class ImageTaskDB:
    def __init__(self, db_path: Path = DB_PATH):
        self._db_path = db_path
        self._lock = asyncio.Lock()

    async def init_db(self) -> None:
        """Create tables and indexes"""
        # 确保 data 目录存在
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS image_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    error_message TEXT,
                    local_path TEXT,
                    next_retry_at TEXT
                )
            ''')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_status ON image_tasks(status)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_priority ON image_tasks(priority)')
            await db.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_url ON image_tasks(url)')
            await db.commit()
        print(f"[ImageTaskDB] Database initialized at {self._db_path}")

    async def add_task(self, url: str, priority: TaskPriority = TaskPriority.MEDIUM) -> int:
        """Add new task, returns task ID. Raises if URL already exists."""
        now = datetime.now().isoformat()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                cursor = await db.execute('''
                    INSERT INTO image_tasks (url, status, priority, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (url, TaskStatus.PENDING.value, priority.value, now, now))
                await db.commit()
                return cursor.lastrowid

    async def get_task_by_url(self, url: str) -> Optional[ImageTask]:
        """Get task by URL for deduplication check"""
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('SELECT * FROM image_tasks WHERE url = ?', (url,))
            row = await cursor.fetchone()
            return self._row_to_task(row) if row else None

    async def get_pending_task(self) -> Optional[ImageTask]:
        """Get next pending task ordered by priority (high > medium > low)"""
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute('''
                    SELECT * FROM image_tasks
                    WHERE status = ?
                    ORDER BY
                        CASE priority
                            WHEN 'high' THEN 0
                            WHEN 'medium' THEN 1
                            WHEN 'low' THEN 2
                        END,
                        created_at ASC
                    LIMIT 1
                ''', (TaskStatus.PENDING.value,))
                row = await cursor.fetchone()
                return self._row_to_task(row) if row else None

    async def update_status(self, task_id: int, status: TaskStatus, error_message: Optional[str] = None) -> None:
        """Update task status"""
        now = datetime.now().isoformat()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                if error_message:
                    await db.execute('''
                        UPDATE image_tasks SET status = ?, updated_at = ?, error_message = ?
                        WHERE id = ?
                    ''', (status.value, now, error_message, task_id))
                else:
                    await db.execute('''
                        UPDATE image_tasks SET status = ?, updated_at = ?
                        WHERE id = ?
                    ''', (status.value, now, task_id))
                await db.commit()

    async def mark_completed(self, task_id: int, local_path: str) -> None:
        """Mark task as completed with local path"""
        now = datetime.now().isoformat()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute('''
                    UPDATE image_tasks
                    SET status = ?, updated_at = ?, local_path = ?
                    WHERE id = ?
                ''', (TaskStatus.COMPLETED.value, now, local_path, task_id))
                await db.commit()

    async def mark_failed(self, task_id: int, error: str, max_retries: int = 5) -> None:
        """Mark task as failed, schedule retry with exponential backoff if under max retries"""
        now = datetime.now()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute('SELECT retry_count FROM image_tasks WHERE id = ?', (task_id,))
                row = await cursor.fetchone()
                retry_count = row['retry_count'] if row else 0

                if retry_count < max_retries:
                    # Schedule for retry with exponential backoff
                    next_delay = 2 ** retry_count  # 1s, 2s, 4s, 8s...
                    next_retry_at = now + timedelta(seconds=next_delay)
                    await db.execute('''
                        UPDATE image_tasks
                        SET status = ?, updated_at = ?, error_message = ?,
                            retry_count = retry_count + 1, next_retry_at = ?
                        WHERE id = ?
                    ''', (TaskStatus.PENDING.value, now.isoformat(), error, next_retry_at.isoformat(), task_id))
                else:
                    # Max retries exceeded
                    await db.execute('''
                        UPDATE image_tasks
                        SET status = ?, updated_at = ?, error_message = ?
                        WHERE id = ?
                    ''', (TaskStatus.FAILED.value, now.isoformat(), error, task_id))
                await db.commit()

    async def get_stats(self) -> dict:
        """Get queue statistics"""
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute('''
                SELECT status, COUNT(*) as count FROM image_tasks GROUP BY status
            ''')
            rows = await cursor.fetchall()
            stats = {TaskStatus.PENDING.value: 0, TaskStatus.DOWNLOADING.value: 0,
                     TaskStatus.COMPLETED.value: 0, TaskStatus.FAILED.value: 0}
            for row in rows:
                stats[row[0]] = row[1]
            return stats

    def _row_to_task(self, row: aiosqlite.Row) -> ImageTask:
        """Convert database row to ImageTask"""
        return ImageTask(
            id=row['id'],
            url=row['url'],
            status=TaskStatus(row['status']),
            priority=TaskPriority(row['priority']),
            retry_count=row['retry_count'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            error_message=row['error_message'],
            local_path=row['local_path'],
            next_retry_at=datetime.fromisoformat(row['next_retry_at']) if row['next_retry_at'] else None
        )

# Global singleton
image_task_db = ImageTaskDB()
```

3. **修改 `api/services/__init__.py`**：
```python
from .image_task_db import ImageTaskDB, ImageTask, TaskStatus, TaskPriority, image_task_db

__all__ = [
    # ... existing exports ...
    "ImageTaskDB", "ImageTask", "TaskStatus", "TaskPriority", "image_task_db",
]
```

4. **修改 `api/main.py` lifespan**：
```python
from .services import file_watcher, image_task_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize task database
    await image_task_db.init_db()

    # Start file watcher
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
</action>

<acceptance_criteria>
- 文件 `api/services/image_task_db.py` 存在
- 运行 `grep -n "class ImageTaskDB" api/services/image_task_db.py` 输出包含类定义
- 运行 `grep -n "image_task_db = ImageTaskDB" api/services/image_task_db.py` 输出包含单例定义
- 运行 `grep -n "CREATE TABLE IF NOT EXISTS image_tasks" api/services/image_task_db.py` 输出包含建表语句
- 运行 `grep -n "image_task_db" api/services/__init__.py` 输出包含导出
- 运行 `grep -n "await image_task_db.init_db" api/main.py` 输出包含初始化调用
- 启动服务后 `data/image_tasks.db` 文件存在
</acceptance_criteria>

---

## Task 2: 创建图片下载服务

<read_first>
- api/services/image_task_db.py (刚创建的任务数据库)
- api/services/crawler_manager.py (日志格式参考)
</read_first>

<action>
创建 `api/services/image_downloader.py`，实现图片下载功能：

```python
# -*- coding: utf-8 -*-
"""
Image download service for downloading images from URLs.
"""
import asyncio
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from datetime import datetime

import httpx


# Default download directory
DOWNLOAD_DIR = Path(__file__).parent.parent.parent / "data" / "downloads"

# Configuration
DOWNLOAD_TIMEOUT = 30.0  # seconds
MIN_INTERVAL = 0.5  # seconds
MAX_INTERVAL = 2.0  # seconds


@dataclass
class DownloadResult:
    success: bool
    local_path: Optional[str] = None
    error: Optional[str] = None


class ImageDownloader:
    """Service for downloading images with jitter interval."""

    def __init__(
        self,
        download_dir: Path = DOWNLOAD_DIR,
        timeout: float = DOWNLOAD_TIMEOUT,
        min_interval: float = MIN_INTERVAL,
        max_interval: float = MAX_INTERVAL
    ):
        self._download_dir = download_dir
        self._timeout = timeout
        self._min_interval = min_interval
        self._max_interval = max_interval
        self._client: Optional[httpx.AsyncClient] = None

    async def init(self) -> None:
        """Initialize the downloader - create directory and HTTP client."""
        self._download_dir.mkdir(parents=True, exist_ok=True)
        self._client = httpx.AsyncClient(
            timeout=self._timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        print(f"[ImageDownloader] Initialized, download dir: {self._download_dir}")

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def download(self, url: str) -> DownloadResult:
        """
        Download an image from URL.

        Args:
            url: The image URL to download

        Returns:
            DownloadResult with success status, local path, or error message
        """
        if not self._client:
            return DownloadResult(success=False, error="Downloader not initialized")

        try:
            response = await self._client.get(url)
            response.raise_for_status()

            # Generate filename from URL hash
            url_hash = hashlib.md5(url.encode()).hexdigest()[:16]

            # Determine extension from content-type
            content_type = response.headers.get("content-type", "")
            ext = self._get_extension(content_type)

            # Create dated subdirectory
            now = datetime.now()
            date_dir = self._download_dir / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
            date_dir.mkdir(parents=True, exist_ok=True)

            # Save file
            filename = f"{url_hash}{ext}"
            file_path = date_dir / filename

            with open(file_path, "wb") as f:
                f.write(response.content)

            print(f"[ImageDownloader] Downloaded: {url} -> {file_path}")
            return DownloadResult(success=True, local_path=str(file_path))

        except httpx.TimeoutException:
            error = f"Timeout downloading {url}"
            print(f"[ImageDownloader] {error}")
            return DownloadResult(success=False, error=error)
        except httpx.HTTPStatusError as e:
            error = f"HTTP {e.response.status_code} for {url}"
            print(f"[ImageDownloader] {error}")
            return DownloadResult(success=False, error=error)
        except Exception as e:
            error = f"Error downloading {url}: {str(e)}"
            print(f"[ImageDownloader] {error}")
            return DownloadResult(success=False, error=error)

    def _get_extension(self, content_type: str) -> str:
        """Get file extension from content-type."""
        content_type = content_type.lower()
        if "jpeg" in content_type or "jpg" in content_type:
            return ".jpg"
        elif "png" in content_type:
            return ".png"
        elif "gif" in content_type:
            return ".gif"
        elif "webp" in content_type:
            return ".webp"
        return ".jpg"  # Default to jpg

    def get_jitter_interval(self) -> float:
        """Get random interval for jitter."""
        import random
        return random.uniform(self._min_interval, self._max_interval)


# Global singleton
image_downloader = ImageDownloader()
```

修改 `api/services/__init__.py`：
```python
from .image_downloader import ImageDownloader, DownloadResult, image_downloader

__all__ = [
    # ... existing exports ...
    "ImageDownloader", "DownloadResult", "image_downloader",
]
```

修改 `api/main.py` lifespan：
```python
from .services import file_watcher, image_task_db, image_downloader

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize task database
    await image_task_db.init_db()

    # Initialize image downloader
    await image_downloader.init()

    # Start file watcher
    file_watcher.start(
        platforms=PLATFORMS,
        base_callback=on_file_change_callback,
        base_path=str(DATA_DIR)
    )
    app.state.file_watcher = file_watcher

    yield

    # Shutdown
    await image_downloader.close()
    file_watcher.stop()
```
</action>

<acceptance_criteria>
- 文件 `api/services/image_downloader.py` 存在
- 运行 `grep -n "class ImageDownloader" api/services/image_downloader.py` 输出包含类定义
- 运行 `grep -n "async def download" api/services/image_downloader.py` 输出包含下载方法
- 运行 `grep -n "image_downloader" api/services/__init__.py` 输出包含导出
- 运行 `grep -n "await image_downloader.init" api/main.py` 输出包含初始化调用
- 运行 `grep -n "await image_downloader.close" api/main.py` 输出包含关闭调用
</acceptance_criteria>

---

## Task 3: 创建消息队列服务

<read_first>
- api/services/image_task_db.py (任务数据库)
- api/services/image_downloader.py (下载服务)
- api/services/crawler_manager.py (asyncio.Queue 模式)
- api/routers/websocket.py (create_task、消费者模式)
- api/main.py (lifespan 集成)
</read_first>

<action>
创建 `api/services/image_queue.py`，实现消息队列服务：

```python
# -*- coding: utf-8 -*-
"""
Image download queue service with multiple consumers.
"""
import asyncio
import random
from typing import Optional, List
from pathlib import Path

from .image_task_db import ImageTask, TaskStatus, TaskPriority, image_task_db
from .image_downloader import image_downloader


# Configuration
QUEUE_MAX_SIZE = 300
CONSUMER_COUNT = 3


class ImageQueueService:
    """
    Service that manages an asyncio.Queue for image download tasks
    and runs multiple consumer coroutines.

    Thread Safety:
    - Uses asyncio.Lock for task status updates
    - Consumers are asyncio.Tasks running on the event loop
    """

    def __init__(
        self,
        queue_size: int = QUEUE_MAX_SIZE,
        consumer_count: int = CONSUMER_COUNT
    ):
        self._queue_size = queue_size
        self._consumer_count = consumer_count
        self._queue: Optional[asyncio.Queue] = None
        self._consumers: List[asyncio.Task] = []
        self._running = False

    @property
    def queue_size(self) -> int:
        """Current queue size."""
        if self._queue is None:
            return 0
        return self._queue.qsize()

    def start(self) -> None:
        """Start the queue service - create queue and launch consumers."""
        if self._running:
            return

        self._queue = asyncio.Queue(maxsize=self._queue_size)
        self._running = True

        # Launch consumer tasks
        for i in range(self._consumer_count):
            consumer = asyncio.create_task(self._consumer_loop(i))
            self._consumers.append(consumer)

        print(f"[ImageQueue] Started with {self._consumer_count} consumers, queue size: {self._queue_size}")

    def stop(self) -> None:
        """Stop the queue service - cancel all consumers."""
        if not self._running:
            return

        self._running = False

        # Cancel all consumers
        for consumer in self._consumers:
            consumer.cancel()

        # Wait for consumers to finish
        for consumer in self._consumers:
            try:
                asyncio.get_event_loop().run_until_complete(consumer)
            except asyncio.CancelledError:
                pass

        self._consumers.clear()
        self._queue = None
        print("[ImageQueue] Stopped")

    async def enqueue(self, url: str, priority: TaskPriority = TaskPriority.MEDIUM) -> bool:
        """
        Add a URL to the download queue.

        Args:
            url: The image URL to download
            priority: Task priority (high/medium/low)

        Returns:
            True if task was queued, False if already exists or queue full
        """
        # Check if URL already exists in database
        existing = await image_task_db.get_task_by_url(url)
        if existing:
            print(f"[ImageQueue] URL already exists: {url}")
            return False

        try:
            # Add to database first
            task_id = await image_task_db.add_task(url, priority)

            # Create task object for queue
            task = ImageTask(
                id=task_id,
                url=url,
                status=TaskStatus.PENDING,
                priority=priority,
                retry_count=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            # Add to queue (non-blocking)
            self._queue.put_nowait(task)
            print(f"[ImageQueue] Enqueued: {url} (priority: {priority.value})")
            return True

        except Exception as e:
            # URL already exists (unique constraint)
            print(f"[ImageQueue] Failed to enqueue {url}: {e}")
            return False

    async def enqueue_from_db(self) -> int:
        """
        Load pending tasks from database into queue.

        Returns:
            Number of tasks loaded
        """
        if self._queue is None:
            return 0

        count = 0
        while self._queue.qsize() < self._queue_size:
            task = await image_task_db.get_pending_task()
            if task is None:
                break

            # Update status to downloading (will be reset by consumer)
            await image_task_db.update_status(task.id, TaskStatus.DOWNLOADING)

            try:
                self._queue.put_nowait(task)
                count += 1
            except asyncio.QueueFull:
                # Reset status if queue is full
                await image_task_db.update_status(task.id, TaskStatus.PENDING)
                break

        if count > 0:
            print(f"[ImageQueue] Loaded {count} tasks from database")
        return count

    def get_stats(self) -> dict:
        """Get queue statistics."""
        return {
            "queue_size": self.queue_size,
            "max_size": self._queue_size,
            "consumer_count": self._consumer_count,
            "running": self._running
        }

    async def _consumer_loop(self, consumer_id: int) -> None:
        """
        Consumer coroutine for processing download tasks.

        Args:
            consumer_id: Consumer identifier for logging
        """
        print(f"[ImageQueue] Consumer {consumer_id} started")

        while self._running:
            try:
                # Get task from queue with timeout
                task = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=1.0
                )

                # Process the task
                await self._process_task(task, consumer_id)

            except asyncio.TimeoutError:
                # No task available, continue polling
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[ImageQueue] Consumer {consumer_id} error: {e}")
                await asyncio.sleep(1.0)

        print(f"[ImageQueue] Consumer {consumer_id} stopped")

    async def _process_task(self, task: ImageTask, consumer_id: int) -> None:
        """
        Process a download task.

        Args:
            task: The task to process
            consumer_id: Consumer identifier for logging
        """
        print(f"[ImageQueue] Consumer {consumer_id} processing task {task.id}: {task.url}")

        # Update status to downloading
        await image_task_db.update_status(task.id, TaskStatus.DOWNLOADING)

        # Apply jitter interval
        interval = image_downloader.get_jitter_interval()
        await asyncio.sleep(interval)

        # Download the image
        result = await image_downloader.download(task.url)

        if result.success:
            await image_task_db.mark_completed(task.id, result.local_path)
            print(f"[ImageQueue] Consumer {consumer_id} completed task {task.id}")
        else:
            await image_task_db.mark_failed(task.id, result.error)
            print(f"[ImageQueue] Consumer {consumer_id} failed task {task.id}: {result.error}")


# Global singleton
image_queue_service = ImageQueueService()
```

修改 `api/services/__init__.py`：
```python
from .image_queue import ImageQueueService, image_queue_service

__all__ = [
    # ... existing exports ...
    "ImageQueueService", "image_queue_service",
]
```

修改 `api/main.py` lifespan：
```python
from .services import file_watcher, image_task_db, image_downloader, image_queue_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize task database
    await image_task_db.init_db()

    # Initialize image downloader
    await image_downloader.init()

    # Start queue service (launches consumers)
    image_queue_service.start()

    # Start file watcher
    file_watcher.start(
        platforms=PLATFORMS,
        base_callback=on_file_change_callback,
        base_path=str(DATA_DIR)
    )
    app.state.file_watcher = file_watcher

    yield

    # Shutdown
    image_queue_service.stop()
    await image_downloader.close()
    file_watcher.stop()
```
</action>

<acceptance_criteria>
- 文件 `api/services/image_queue.py` 存在
- 运行 `grep -n "class ImageQueueService" api/services/image_queue.py` 输出包含类定义
- 运行 `grep -n "async def enqueue" api/services/image_queue.py` 输出包含入队方法
- 运行 `grep -n "async def _consumer_loop" api/services/image_queue.py` 输出包含消费者方法
- 运行 `grep -n "image_queue_service" api/services/__init__.py` 输出包含导出
- 运行 `grep -n "image_queue_service.start" api/main.py` 输出包含启动调用
- 运行 `grep -n "image_queue_service.stop" api/main.py` 输出包含停止调用
- 运行 `grep -n "CONSUMER_COUNT = 3" api/services/image_queue.py` 输出包含并发数配置
- 运行 `grep -n "QUEUE_MAX_SIZE = 300" api/services/image_queue.py` 输出包含队列容量配置
</acceptance_criteria>

---

## Task 4: 创建队列管理 API 路由

<read_first>
- api/services/image_queue.py (队列服务)
- api/services/image_task_db.py (任务数据库)
- api/routers/crawler.py (路由模式参考)
- api/schemas/__init__.py (schema 定义模式)
</read_first>

<action>
创建 `api/routers/image_queue.py`，提供队列管理 API：

```python
# -*- coding: utf-8 -*-
"""
Image queue management API routes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from ..services import image_queue_service, image_task_db
from ..services.image_task_db import TaskPriority


router = APIRouter(prefix="/image-queue", tags=["image-queue"])


class EnqueueRequest(BaseModel):
    """Request to enqueue an image download task."""
    url: str
    priority: Optional[str] = Field(default="medium", description="high, medium, or low")


class EnqueueResponse(BaseModel):
    """Response for enqueue request."""
    success: bool
    message: str


class StatsResponse(BaseModel):
    """Response for queue stats."""
    queue_size: int
    max_size: int
    consumer_count: int
    running: bool
    pending: int
    downloading: int
    completed: int
    failed: int


@router.post("/enqueue", response_model=EnqueueResponse)
async def enqueue_download(request: EnqueueRequest):
    """
    Add an image URL to the download queue.

    Args:
        request: The enqueue request with URL and optional priority

    Returns:
        EnqueueResponse indicating success or failure
    """
    # Validate priority
    try:
        priority = TaskPriority(request.priority.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority: {request.priority}. Must be one of: high, medium, low"
        )

    success = await image_queue_service.enqueue(request.url, priority)

    if success:
        return EnqueueResponse(success=True, message=f"Enqueued: {request.url}")
    else:
        return EnqueueResponse(success=False, message=f"URL already exists or queue full: {request.url}")


@router.get("/stats", response_model=StatsResponse)
async def get_queue_stats():
    """
    Get queue statistics.

    Returns:
        StatsResponse with queue and task counts
    """
    queue_stats = image_queue_service.get_stats()
    db_stats = await image_task_db.get_stats()

    return StatsResponse(
        queue_size=queue_stats["queue_size"],
        max_size=queue_stats["max_size"],
        consumer_count=queue_stats["consumer_count"],
        running=queue_stats["running"],
        pending=db_stats.get("pending", 0),
        downloading=db_stats.get("downloading", 0),
        completed=db_stats.get("completed", 0),
        failed=db_stats.get("failed", 0)
    )


@router.post("/load-from-db")
async def load_from_database():
    """
    Load pending tasks from database into queue.

    Returns:
        Number of tasks loaded
    """
    count = await image_queue_service.enqueue_from_db()
    return {"loaded": count}
```

修改 `api/main.py` 注册路由：
```python
from .routers import crawler_router, data_router, websocket_router, notes_router, zhihu_router, bilibili_router, douyin_router, subscriptions_router, trends_router, image_queue_router

# ... in route registration section:
app.include_router(image_queue_router, prefix="/api")
```

修改 `api/routers/__init__.py`：
```python
from .image_queue import router as image_queue_router

__all__ = [
    # ... existing exports ...
    "image_queue_router",
]
```
</action>

<acceptance_criteria>
- 文件 `api/routers/image_queue.py` 存在
- 运行 `grep -n "router = APIRouter" api/routers/image_queue.py` 输出包含路由定义
- 运行 `grep -n "async def enqueue_download" api/routers/image_queue.py` 输出包含入队端点
- 运行 `grep -n "async def get_queue_stats" api/routers/image_queue.py` 输出包含统计端点
- 运行 `grep -n "image_queue_router" api/main.py` 输出包含路由注册
- 运行 `grep -n "image_queue_router" api/routers/__init__.py` 输出包含导出
- 访问 `http://localhost:8080/docs` 能看到 `/api/image-queue/enqueue` 和 `/api/image-queue/stats` 端点
</acceptance_criteria>

---

## Verification

### Manual Testing Steps

1. **启动服务**：
   ```bash
   cd MediaCrawler
   uv run uvicorn api.main:app --port 8080 --reload
   ```

2. **验证数据库初始化**：
   ```bash
   ls data/image_tasks.db
   ```

3. **测试入队**：
   ```bash
   curl -X POST http://localhost:8080/api/image-queue/enqueue \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com/image.jpg", "priority": "high"}'
   ```

4. **检查队列状态**：
   ```bash
   curl http://localhost:8080/api/image-queue/stats
   ```

5. **验证下载**：
   - 使用真实图片 URL 测试下载
   - 检查 `data/downloads/` 目录下是否生成文件

### Automated Checks

```bash
# Check all files exist
test -f api/services/image_task_db.py && echo "OK: image_task_db.py"
test -f api/services/image_downloader.py && echo "OK: image_downloader.py"
test -f api/services/image_queue.py && echo "OK: image_queue.py"
test -f api/routers/image_queue.py && echo "OK: image_queue router"

# Check key implementations
grep -q "CREATE TABLE IF NOT EXISTS image_tasks" api/services/image_task_db.py && echo "OK: DB schema"
grep -q "async def _consumer_loop" api/services/image_queue.py && echo "OK: consumer loop"
grep -q "image_queue_service.start()" api/main.py && echo "OK: lifespan start"
grep -q "image_queue_service.stop()" api/main.py && echo "OK: lifespan stop"
```

---

## Notes

- 使用 `aiosqlite` 而非 SQLAlchemy ORM，因为任务数据库独立且查询简单
- 队列容量 300，消费者数量 3，可根据实际负载调整
- 抖动间隔 0.5-2.0 秒，避免触发平台限流
- 指数退避重试：1s, 2s, 4s, 8s... 最大 5 次重试
- 优先级排序：high > medium > low，同级按创建时间排序
