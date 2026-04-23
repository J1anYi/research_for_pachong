---
phase: 05-dingshi-renwu-diaodu
plan: 03
status: complete
completed: 2026-04-23
requirements: [SCHED-01, SCHED-02, SCHED-03]
---

# Plan 05-03: Integrate with FastAPI

## Summary

Integrated ImageSchedulerService into FastAPI application lifespan and extended the stats API to include scheduler status.

## Changes

### Modified Files

| File | Changes |
|------|---------|
| `MediaCrawler/api/main.py` | Added `image_scheduler` import, start() and stop() in lifespan |
| `MediaCrawler/api/routers/image_queue.py` | Extended `StatsResponse`, updated `get_queue_stats()` |

## Implementation Details

### StatsResponse Extension

Added three new fields:
- `scheduler_running: bool` — Whether the scheduler is running
- `scheduler_interval: int` — Scan interval in seconds (300)
- `scheduler_last_scan: Optional[str]` — ISO timestamp of last scan

### Lifespan Integration

**Startup order:**
1. `image_task_db.init_db()` — Initialize database
2. `image_downloader.init()` — Initialize downloader
3. `image_queue_service.start()` — Start queue consumers
4. `image_scheduler.start()` — Start scheduler
5. `file_watcher.start()` — Start file watcher

**Shutdown order:**
1. `image_scheduler.stop()` — Stop scheduler
2. `image_queue_service.stop()` — Stop queue consumers
3. `image_downloader.close()` — Close downloader
4. `file_watcher.stop()` — Stop file watcher

## Verification

- [x] Python syntax check passed for both files
- [x] `image_scheduler.start()` present in lifespan
- [x] `image_scheduler.stop()` present in lifespan
- [x] `StatsResponse` has `scheduler_running`, `scheduler_interval`, `scheduler_last_scan` fields
- [x] `get_queue_stats()` calls `image_scheduler.get_stats()`

## Key Links

| From | To | Via |
|------|-----|-----|
| main.py | image_scheduler.py | `image_scheduler.start()`, `image_scheduler.stop()` |
| image_queue.py | image_scheduler.py | `image_scheduler.get_stats()` |

## API Response Example

```json
{
  "queue_size": 0,
  "max_size": 300,
  "consumer_count": 3,
  "running": true,
  "pending": 0,
  "downloading": 0,
  "completed": 10,
  "failed": 2,
  "scheduler_running": true,
  "scheduler_interval": 300,
  "scheduler_last_scan": "2026-04-23T12:00:00.000000"
}
```
