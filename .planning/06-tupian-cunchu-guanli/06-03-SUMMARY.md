# Phase 6 Plan 03 Summary

**Plan:** Integrate ImageStorageService into ImageDownloader
**Status:** ✅ Complete
**Date:** 2026-04-23

---

## What Was Done

Modified `MediaCrawler/api/services/image_downloader.py` to integrate with ImageStorageService:

### Changes Made

1. **Added Imports:**
   ```python
   from .image_storage import image_storage
   from .image_task_db import image_task_db, TaskStatus
   ```

2. **Updated Method Signature:**
   ```python
   async def download(self, url: str, platform: str = "xhs") -> DownloadResult:
   ```

3. **Added Deduplication Check:**
   - Query `image_task_db.get_completed_task_by_url()` before downloading
   - Return existing path if already downloaded successfully

4. **Integrated Storage Path Generation:**
   - Replaced manual hash calculation with `image_storage.get_storage_path()`
   - Path follows pattern: `{data_dir}/{platform}/images/{year}/{month}/{day}/{hash}.jpg`

5. **Added Image Validation:**
   - Call `image_storage.validate_image()` after download
   - Delete invalid files (HTML error pages, etc.)
   - Rename file if detected extension differs

6. **Added Cleanup Trigger:**
   - Call `image_storage.cleanup_by_size(platform)` after successful download
   - Remove oldest files when storage exceeds 5GB limit

### Download Flow

```
download(url, platform)
  │
  ├─► Check deduplication (get_completed_task_by_url)
  │     └─► If exists: return existing path
  │
  ├─► HTTP GET request
  │
  ├─► Get storage path (get_storage_path)
  │
  ├─► Save file
  │
  ├─► Validate image (validate_image)
  │     └─► If invalid: delete, return error
  │
  ├─► Rename if extension differs
  │
  └─► Cleanup old files (cleanup_by_size)
        └─► Return success
```

---

## Verification

```bash
$ python -m py_compile MediaCrawler/api/services/image_downloader.py
image_downloader.py: syntax OK
```

---

## Files Modified

| File | Action |
|------|--------|
| `MediaCrawler/api/services/image_downloader.py` | Modified |
