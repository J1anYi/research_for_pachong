# Phase 5: 定时任务调度 - Research

**Researched:** 2026-04-23
**Domain:** 定时任务调度、任务监控、自动重试机制
**Confidence:** HIGH

## Summary

Phase 5 实现任务监控和自动重试机制，通过定时扫描任务数据库来处理失败任务重试和任务超时检测。基于现有架构模式（FastAPI lifespan + asyncio 后台任务），建议使用 **纯 asyncio 实现** 而非 APScheduler，理由如下：
1. 与现有 `image_queue_service` 的消费者模式一致
2. 无需添加额外依赖
3. 代码更简洁，符合项目约束（用最少的代码解决问题）
4. 单进程场景下 asyncio 已足够

**Primary recommendation:** 创建 `ImageSchedulerService`，使用 `asyncio.create_task` + `asyncio.sleep` 实现定时循环，集成到现有 lifespan 管理中。

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: 扫描间隔** — 5 分钟
- **D-02: 超时阈值** — 120 秒
- **D-03: 最大重试次数** — 5 次（继承自 Phase 4）
- **D-04: 监控方式** — 扩展现有 API（扩展 `/api/image-queue/stats` 端点）
- **D-05: 控制能力** — 仅监控，不控制（不提供暂停/恢复/手动触发 API）

### Claude's Discretion

- APScheduler 的具体配置方式（interval 触发器参数）
- 扫描任务的具体实现逻辑
- 错误处理和日志格式

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SCHED-01 | 定时扫描未完成任务 | 使用 asyncio 定时循环 + `get_pending_task()` |
| SCHED-02 | 失败任务重试调度 | 利用 `next_retry_at` 字段 + `enqueue_from_db()` |
| SCHED-03 | 任务超时检测 | 查询 `status=downloading` 且 `updated_at` 超时的任务 |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| 定时扫描任务 | API/Backend | — | 后台服务运行在 FastAPI 进程中 |
| 超时检测 | API/Backend | Database | 需要查询数据库，但逻辑在服务层 |
| 重试调度 | API/Backend | Queue | 需要将任务重新入队 |
| 状态监控 | API/Backend | — | 通过扩展 stats 端点实现 |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| asyncio | stdlib | 后台任务调度 | Python 原生，与现有架构一致 |
| aiosqlite | 0.21.0 | 异步数据库操作 | 已安装，Phase 4 使用 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| APScheduler | — | — | **不使用**，asyncio 已足够 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| asyncio 定时循环 | APScheduler | APScheduler 更成熟，但增加依赖；asyncio 与现有架构一致，代码更简洁 |

**Installation:**
无需额外安装 — 使用现有依赖。

**Version verification:**
```
aiosqlite==0.21.0 [VERIFIED: uv pip list]
```

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application                          │
│                     (lifespan 管理启停)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ImageSchedulerService                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              _scheduler_loop (asyncio.Task)             │   │
│  │                                                          │   │
│  │   每 5 分钟执行:                                          │   │
│  │   1. scan_timeout_tasks() → 标记超时任务为 failed         │   │
│  │   2. scan_retry_tasks() → 将到期任务重新入队              │   │
│  │   3. enqueue_from_db() → 加载 pending 任务               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐     ┌───────────────────────┐     ┌─────────────────┐
│ ImageTaskDB   │     │ ImageQueueService     │     │ StatsResponse   │
│               │     │                       │     │ (扩展)          │
│ • get_timeout │     │ • enqueue_from_db()   │     │                 │
│ • get_retry   │     │ • enqueue()           │     │ + scheduler_    │
│ • mark_failed │     │                       │     │   status        │
└───────────────┘     └───────────────────────┘     └─────────────────┘
```

### Recommended Project Structure
```
MediaCrawler/api/
├── services/
│   ├── image_scheduler.py    # NEW: 调度器服务
│   ├── image_task_db.py      # MODIFY: 添加查询方法
│   └── __init__.py           # MODIFY: 导出新服务
├── routers/
│   └── image_queue.py        # MODIFY: 扩展 StatsResponse
└── main.py                   # MODIFY: lifespan 集成
```

### Pattern 1: asyncio 后台任务模式
**What:** 使用 `asyncio.create_task` 创建后台协程，配合 `asyncio.sleep` 实现定时循环
**When to use:** 单进程、简单定时任务场景
**Example:**
```python
# Source: 现有 image_queue.py 消费者模式
async def _scheduler_loop(self) -> None:
    """Main scheduler loop - runs every SCAN_INTERVAL seconds."""
    print("[ImageScheduler] Started scheduler loop")
    while self._running:
        try:
            await self._run_scan()
            await asyncio.sleep(self._scan_interval)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[ImageScheduler] Error in scan: {e}")
            await asyncio.sleep(60)  # Backoff on error
    print("[ImageScheduler] Stopped scheduler loop")
```

### Pattern 2: Lifespan 集成模式
**What:** 在 FastAPI lifespan 中启动和停止后台服务
**When to use:** 所有需要在应用启动时初始化的服务
**Example:**
```python
# Source: 现有 api/main.py lifespan 模式
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await image_task_db.init_db()
    await image_downloader.init()
    image_queue_service.start()
    image_scheduler.start()  # NEW
    file_watcher.start(...)
    
    yield
    
    # Shutdown
    image_scheduler.stop()  # NEW
    image_queue_service.stop()
    ...
```

### Anti-Patterns to Avoid
- **使用 APScheduler:** 增加不必要的依赖，与现有架构不一致
- **阻塞主事件循环:** 扫描操作必须是异步的，不能使用 `time.sleep`
- **频繁扫描:** 5 分钟间隔已经足够，不要过度扫描数据库
- **忽略错误:** 扫描出错时应有退避机制，不要立即重试

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| 定时循环 | 自己实现 schedule 逻辑 | `asyncio.sleep()` | 简单可靠，无需额外依赖 |
| 任务去重 | 重新入队前检查 | `get_task_by_url()` | 已有实现 |
| 指数退避 | 自己计算延迟 | `mark_failed()` | 已在 Phase 4 实现 |

**Key insight:** Phase 4 已经实现了大部分基础功能（`mark_failed`、`next_retry_at`），Phase 5 只需要定时触发和超时检测。

## Runtime State Inventory

> 此阶段不涉及重命名/重构/迁移，跳过此部分。

## Common Pitfalls

### Pitfall 1: 竞态条件 — 调度器与消费者冲突
**What goes wrong:** 调度器将任务入队的同时，消费者也在处理同一任务
**Why it happens:** `enqueue_from_db()` 使用 `get_pending_task()` 获取任务，可能与调度器冲突
**How to avoid:** 
- 调度器只处理 `next_retry_at` 到期的任务（已失败的任务）
- `enqueue_from_db()` 只处理 `status=pending` 且 `next_retry_at IS NULL` 的任务
- 使用数据库锁（已有 `self._lock`）
**Warning signs:** 任务被重复处理，队列大小异常增长

### Pitfall 2: 超时检测误判
**What goes wrong:** 正常下载被误判为超时
**Why it happens:** `updated_at` 字段在每次状态更新时都会更新，可能导致误判
**How to avoid:** 
- 只检查 `status=downloading` 的任务
- 超时阈值设为 120 秒（远大于下载超时 30 秒）
- 考虑网络波动，不要设置过短的阈值
**Warning signs:** 大量正常任务被标记为失败

### Pitfall 3: 调度器启动时遗漏任务
**What goes wrong:** 应用重启后，pending 任务没有被加载到队列
**Why it happens:** 调度器启动时没有调用 `enqueue_from_db()`
**How to avoid:** 在调度器启动时调用 `enqueue_from_db()` 加载现有任务
**Warning signs:** 重启后任务不执行，队列始终为空

### Pitfall 4: 关闭时任务丢失
**What goes wrong:** 应用关闭时，正在处理的任务状态不正确
**Why it happens:** 调度器在关闭时没有等待当前扫描完成
**How to avoid:** 
- 使用 `asyncio.CancelledError` 处理取消
- 将 `downloading` 状态的任务重置为 `pending`
**Warning signs:** 关闭后重启，大量任务卡在 `downloading` 状态

## Code Examples

### 调度器服务核心结构

```python
# api/services/image_scheduler.py
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from .image_task_db import TaskStatus, image_task_db
from .image_queue import image_queue_service

# Configuration
SCAN_INTERVAL = 300  # 5 minutes
TIMEOUT_THRESHOLD = 120  # seconds


class ImageSchedulerService:
    """Service that periodically scans tasks for retry and timeout detection."""

    def __init__(self, scan_interval: int = SCAN_INTERVAL, timeout_threshold: int = TIMEOUT_THRESHOLD):
        self._scan_interval = scan_interval
        self._timeout_threshold = timeout_threshold
        self._scheduler_task: Optional[asyncio.Task] = None
        self._running = False
        self._last_scan_at: Optional[datetime] = None

    def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            return
        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        print(f"[ImageScheduler] Started, interval: {self._scan_interval}s, timeout: {self._timeout_threshold}s")

    def stop(self) -> None:
        """Stop the scheduler."""
        if not self._running:
            return
        self._running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                asyncio.get_event_loop().run_until_complete(self._scheduler_task)
            except asyncio.CancelledError:
                pass
        print("[ImageScheduler] Stopped")

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                await self._run_scan()
                self._last_scan_at = datetime.now()
                await asyncio.sleep(self._scan_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[ImageScheduler] Error: {e}")
                await asyncio.sleep(60)  # Backoff

    async def _run_scan(self) -> None:
        """Execute all scan tasks."""
        # 1. Timeout detection
        timeout_count = await self._scan_timeout_tasks()
        # 2. Retry scheduling
        retry_count = await self._scan_retry_tasks()
        # 3. Load pending tasks
        loaded_count = await image_queue_service.enqueue_from_db()
        
        if timeout_count > 0 or retry_count > 0 or loaded_count > 0:
            print(f"[ImageScheduler] Scan result: timeout={timeout_count}, retry={retry_count}, loaded={loaded_count}")

    async def _scan_timeout_tasks(self) -> int:
        """Mark timeout tasks as failed."""
        timeout_tasks = await image_task_db.get_timeout_tasks(self._timeout_threshold)
        for task in timeout_tasks:
            await image_task_db.mark_failed(task.id, "Download timeout")
        return len(timeout_tasks)

    async def _scan_retry_tasks(self) -> int:
        """Enqueue tasks ready for retry."""
        retry_tasks = await image_task_db.get_ready_retry_tasks()
        count = 0
        for task in retry_tasks:
            await image_task_db.update_status(task.id, TaskStatus.PENDING)
            await image_queue_service.enqueue(task.url, task.priority)
            count += 1
        return count

    def get_stats(self) -> dict:
        """Get scheduler status."""
        return {
            "running": self._running,
            "scan_interval": self._scan_interval,
            "timeout_threshold": self._timeout_threshold,
            "last_scan_at": self._last_scan_at.isoformat() if self._last_scan_at else None,
        }


# Global singleton
image_scheduler = ImageSchedulerService()
```

### 数据库服务扩展

```python
# 添加到 api/services/image_task_db.py

async def get_timeout_tasks(self, timeout_seconds: int) -> List[ImageTask]:
    """Get tasks that have been downloading for too long."""
    cutoff = datetime.now() - timedelta(seconds=timeout_seconds)
    async with aiosqlite.connect(self._db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT * FROM image_tasks
            WHERE status = ? AND updated_at < ?
        ''', (TaskStatus.DOWNLOADING.value, cutoff.isoformat()))
        rows = await cursor.fetchall()
        return [self._row_to_task(row) for row in rows]

async def get_ready_retry_tasks(self) -> List[ImageTask]:
    """Get tasks ready for retry (next_retry_at has passed)."""
    now = datetime.now()
    async with aiosqlite.connect(self._db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT * FROM image_tasks
            WHERE status = ? AND next_retry_at IS NOT NULL AND next_retry_at <= ?
            ORDER BY next_retry_at ASC
        ''', (TaskStatus.PENDING.value, now.isoformat()))
        rows = await cursor.fetchall()
        return [self._row_to_task(row) for row in rows]
```

### StatsResponse 扩展

```python
# 修改 api/routers/image_queue.py

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
    # NEW: Scheduler status
    scheduler_running: bool
    scheduler_interval: int
    scheduler_last_scan: Optional[str]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| APScheduler 定时任务 | asyncio 原生后台任务 | Phase 5 设计 | 减少依赖，简化架构 |

**Deprecated/outdated:**
- APScheduler: 不需要，asyncio 已足够满足需求

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `updated_at` 可用于判断下载开始时间 | 超时检测 | 如果其他地方也更新 `updated_at`，可能导致误判 |

**验证:** `image_queue.py` 中 `_process_task()` 在开始下载时调用 `update_status(task.id, TaskStatus.DOWNLOADING)`，这会更新 `updated_at`。所以 `updated_at` 确实是下载开始时间。

## Open Questions

1. **启动时是否需要清理 `downloading` 状态的任务？**
   - What we know: 应用关闭时，正在下载的任务会保持在 `downloading` 状态
   - What's unclear: 是否需要在启动时将这些任务重置为 `pending`
   - Recommendation: 是的，应在调度器启动时调用清理方法，将所有 `downloading` 任务重置为 `pending`，因为它们在应用关闭时没有完成

2. **`enqueue_from_db()` 是否会与重试任务冲突？**
   - What we know: `enqueue_from_db()` 调用 `get_pending_task()` 获取任务
   - What's unclear: 重试任务（有 `next_retry_at`）是否会被 `get_pending_task()` 获取
   - Recommendation: 需要修改 `get_pending_task()` 查询，添加 `AND (next_retry_at IS NULL OR next_retry_at <= ?)` 条件，或者确保调度器处理重试任务后清除 `next_retry_at`

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python asyncio | 后台任务 | ✓ | 3.x stdlib | — |
| aiosqlite | 数据库操作 | ✓ | 0.21.0 | — |
| FastAPI | API 框架 | ✓ | 0.110.2 | — |

**Missing dependencies with no fallback:**
None — 所有依赖已满足。

**Missing dependencies with fallback:**
None

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (已安装) |
| Config file | pyproject.toml |
| Quick run command | `pytest tests/test_image_scheduler.py -x -v` |
| Full suite command | `pytest tests/ -x` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCHED-01 | 定时扫描未完成任务 | unit | `pytest tests/test_image_scheduler.py::test_scan_pending_tasks -x` | Wave 0 |
| SCHED-02 | 失败任务重试调度 | unit | `pytest tests/test_image_scheduler.py::test_retry_scheduling -x` | Wave 0 |
| SCHED-03 | 任务超时检测 | unit | `pytest tests/test_image_scheduler.py::test_timeout_detection -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_image_scheduler.py -x -v`
- **Per wave merge:** `pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_image_scheduler.py` — covers SCHED-01, SCHED-02, SCHED-03
- [ ] `tests/conftest.py` — shared fixtures (if not exists)

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | Pydantic models |
| V6 Cryptography | no | — |

### Known Threat Patterns for Python/FastAPI

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SQL Injection | Tampering | aiosqlite parameterized queries |
| Race Condition | Tampering | asyncio.Lock |

**Security Notes:**
- 调度器不暴露外部 API（仅内部服务），攻击面小
- 使用参数化查询，避免 SQL 注入
- 使用 `asyncio.Lock` 保护并发访问

## Sources

### Primary (HIGH confidence)
- 现有代码分析 — `api/main.py`, `api/services/image_task_db.py`, `api/services/image_queue.py` [VERIFIED]
- REQUIREMENTS.md — Phase 5 需求定义 [VERIFIED]
- CONTEXT.md — 用户决策 [VERIFIED]

### Secondary (MEDIUM confidence)
- Python asyncio 文档 — 后台任务模式 [ASSUMED]

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — 使用现有依赖，无需新增
- Architecture: HIGH — 与现有架构一致
- Pitfalls: HIGH — 基于对现有代码的深入分析

**Research date:** 2026-04-23
**Valid until:** 30 days — 稳定架构
