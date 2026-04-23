---
phase: 05-dingshi-renwu-diaodu
plan: 02
status: complete
completed: 2026-04-23
requirements: [SCHED-01, SCHED-02, SCHED-03]
---

# Plan 05-02: Create ImageSchedulerService

## Summary

Created `ImageSchedulerService` that periodically scans for timeout tasks and retry tasks, using asyncio-based background scheduling.

## Changes

### New Files

| File | Purpose |
|------|---------|
| `MediaCrawler/api/services/image_scheduler.py` | Scheduler service with timeout detection and retry scheduling |

### Modified Files

| File | Changes |
|------|---------|
| `MediaCrawler/api/services/__init__.py` | Added exports for `ImageSchedulerService` and `image_scheduler` |

## Implementation Details

### Configuration Constants

- `SCAN_INTERVAL = 300` (5 minutes per D-01)
- `TIMEOUT_THRESHOLD = 120` (seconds per D-02)

### ImageSchedulerService Class

| Method | Purpose |
|--------|---------|
| `start()` | Creates asyncio.Task for `_scheduler_loop()` |
| `stop()` | Cancels and waits for scheduler task |
| `_scheduler_loop()` | Runs every 5 minutes, handles errors with 60s backoff |
| `_run_scan()` | Coordinates timeout scan, retry scan, and queue loading |
| `_scan_timeout_tasks()` | Finds downloading tasks exceeding 120s, marks as failed |
| `_scan_retry_tasks()` | Clears `next_retry_at` for ready retry tasks |
| `get_stats()` | Returns scheduler status dict |

### Retry Task Flow

The `_scan_retry_tasks()` method does NOT directly enqueue retry tasks. Instead:
1. It clears their `next_retry_at` field using `clear_next_retry_at()`
2. This makes them "regular" pending tasks (`next_retry_at = NULL`)
3. The subsequent `enqueue_from_db()` call in `_run_scan()` picks them up
4. This avoids the problem where `enqueue()` rejects existing URLs

## Verification

- [x] Python syntax check passed
- [x] `SCAN_INTERVAL = 300` present
- [x] `TIMEOUT_THRESHOLD = 120` present
- [x] All required methods exist
- [x] Global singleton `image_scheduler` exported
- [x] `_scan_retry_tasks` uses `clear_next_retry_at()`, not `enqueue()`

## Key Links

| From | To | Via |
|------|-----|-----|
| image_scheduler.py | image_task_db.py | `get_timeout_tasks()`, `get_ready_retry_tasks()`, `clear_next_retry_at()`, `mark_failed()` |
| image_scheduler.py | image_queue.py | `enqueue_from_db()` |

## Next Steps

Plan 05-03 will integrate the scheduler into FastAPI lifespan and extend the stats API.
