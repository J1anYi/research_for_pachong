# Plan 03 Summary: 后端发送新增数据和标题信息

**Date:** 2026-04-22
**Status:** Completed
**Branch:** feat/zhihu-data-viewer

---

## Tasks Completed

### Task 1: 扩展 DataUpdateMessage schema
- **Commit:** 78f46ef
- **File:** `api/schemas/crawler.py`
- **Changes:**
  - Added `new_count: int = 0` field
  - Added `titles: list[str] = []` field

### Task 2: 添加平台记录计数追踪
- **Commit:** 9e67a7a
- **File:** `api/routers/websocket.py`
- **Changes:**
  - Added `_previous_counts: dict[str, int] = {}` for tracking
  - Added `set_previous_count()` function
  - Added `get_previous_count()` function
  - Added `calculate_new_count()` function

### Task 3: 添加获取最新记录的 API 函数
- **Commit:** 4bfa4d7
- **File:** `api/routers/notes.py`
- **Changes:**
  - Added `import aiofiles` for async file operations
  - Added `get_recent_notes()` function - retrieves most recent notes with titles
  - Added `get_platform_notes_count()` function - counts total notes for platform

### Task 4: 修改 broadcast_platform_update 包含新记录信息
- **Commit:** b3b308a
- **File:** `api/routers/websocket.py`
- **Changes:**
  - Modified `broadcast_platform_update()` to import helper functions
  - Calculate `new_count` using `get_platform_notes_count` and `calculate_new_count`
  - Retrieve `titles` using `get_recent_notes()`
  - Include both fields in `DataUpdateMessage` broadcast

---

## Acceptance Criteria Verification

| Criteria | Status | Verification |
|----------|--------|--------------|
| `DataUpdateMessage` includes `new_count` field | ✅ | `grep -n "new_count" api/schemas/crawler.py` returns line 115 |
| `DataUpdateMessage` includes `titles` field | ✅ | `grep -n "titles" api/schemas/crawler.py` returns line 116 |
| `_previous_counts` defined | ✅ | Line 65 in websocket.py |
| `calculate_new_count` function exists | ✅ | Line 78 in websocket.py |
| `get_recent_notes` function exists | ✅ | Line 313 in notes.py |
| `get_platform_notes_count` function exists | ✅ | Line 376 in notes.py |
| `broadcast_platform_update` includes new_count and titles | ✅ | Verified via grep |

---

## Technical Details

### Data Flow
1. File watcher detects change → calls `broadcast_platform_update(platform)`
2. `get_platform_notes_count()` reads current total
3. `calculate_new_count()` compares with stored previous count
4. `get_recent_notes()` fetches titles of newest records
5. `DataUpdateMessage` is broadcast with complete information

### New Dependencies
- `aiofiles` for async file reading (already in project requirements)

---

## Related Requirements
- BUG-03: 通知显示固定数字而非实际增量
- NOTIF-01: WebSocket 消息应包含新增数据和标题信息
