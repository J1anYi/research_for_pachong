---
phase: 05-dingshi-renwu-diaodu
plan: 01
status: complete
completed: 2026-04-23
requirements: [SCHED-01, SCHED-02, SCHED-03]
---

# Plan 05-01: Add DB Query Methods

## Summary

Added three new database query methods to `ImageTaskDB` class for timeout detection and retry scheduling, and modified `get_pending_task()` to exclude retry tasks waiting for their scheduled time.

## Changes

### Modified Files

| File | Changes |
|------|---------|
| `MediaCrawler/api/services/image_task_db.py` | Added `List` import, modified `get_pending_task()`, added 3 new methods |

### New Methods

1. **`get_timeout_tasks(timeout_seconds: int) -> List[ImageTask]`**
   - Queries tasks where `status = 'downloading'` AND `updated_at < (now - timeout_seconds)`
   - Returns list of tasks that have exceeded the timeout threshold

2. **`get_ready_retry_tasks() -> List[ImageTask]`**
   - Queries tasks where `status = 'pending'` AND `next_retry_at IS NOT NULL` AND `next_retry_at <= now`
   - Ordered by `next_retry_at ASC`
   - Returns list of tasks ready for retry

3. **`clear_next_retry_at(task_id: int) -> None`**
   - Clears `next_retry_at` field, making the task a regular pending task
   - Updates `updated_at` timestamp
   - Uses `self._lock` for thread safety

### Modified Method

**`get_pending_task()`**
- Added condition: `AND (next_retry_at IS NULL OR next_retry_at <= ?)`
- Passes current timestamp as second parameter
- New tasks (`next_retry_at IS NULL`) are picked up immediately
- Retry tasks are only picked up after their scheduled time

## Verification

- [x] Python syntax check passed
- [x] Query contains `next_retry_at IS NULL` condition
- [x] Query contains `next_retry_at <=` condition
- [x] Three new methods exist in `ImageTaskDB` class

## Key Links

| From | To | Via |
|------|-----|-----|
| image_scheduler.py | image_task_db.py | `get_timeout_tasks()`, `get_ready_retry_tasks()`, `clear_next_retry_at()` |
| image_queue.py | image_task_db.py | `get_pending_task()` (now excludes waiting retry tasks) |

## Next Steps

Plan 05-02 will create `ImageSchedulerService` that uses these methods.
