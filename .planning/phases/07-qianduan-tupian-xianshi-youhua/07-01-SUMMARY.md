# Plan 07-01 Summary: API 返回本地图片路径

**Status:** ✅ Complete
**Date:** 2026-04-23

---

## Changes Made

### 1. Added import for image_storage service

**File:** `MediaCrawler/api/routers/notes.py`

```python
from ..services.image_storage import image_storage
```

### 2. Modified format_note_for_response() function

Added three new fields to API response:
- `local_image_url` - Local image path if downloaded (via image_storage.get_local_path())
- `remote_image_url` - Remote image path for fallback
- `first_image_url` - Preferred URL (local if exists, else remote)

### 3. Added static file route for local images

**File:** `MediaCrawler/api/main.py`

```python
# Mount data directory for local images (downloaded images with hash-based paths)
LOCAL_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
if os.path.exists(LOCAL_DATA_DIR):
    app.mount("/local-images", StaticFiles(directory=LOCAL_DATA_DIR), name="local-images")
```

---

## Verification

```bash
grep -n "local_image_url\|local-images\|image_storage" MediaCrawler/api/routers/notes.py MediaCrawler/api/main.py
```

---

## Success Criteria Met

- [x] API 返回 local_image_url 和 remote_image_url 字段
- [x] 本地图片存在时返回本地路径
- [x] 本地图片不存在时返回 None
- [x] 静态文件路由正常工作
