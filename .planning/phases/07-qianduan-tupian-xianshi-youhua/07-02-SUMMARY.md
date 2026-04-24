# Plan 07-02 Summary: 前端图片显示逻辑

**Status:** ✅ Complete
**Date:** 2026-04-23

---

## Changes Made

### Modified createNoteCard() function

**File:** `MediaCrawler/viewer/static/js/app.js`

1. **Determine image URLs - prefer local, fallback to remote:**
   ```javascript
   const localUrl = note.local_image_url;
   const remoteUrl = note.remote_image_url;
   const primaryUrl = localUrl || remoteUrl;
   ```

2. **Store URLs for fallback mechanism:**
   ```javascript
   if (localUrl && remoteUrl) {
       img.dataset.localUrl = localUrl;
       img.dataset.remoteUrl = remoteUrl;
       img.dataset.fallbackUsed = 'false';
   }
   ```

3. **Fallback handler:**
   ```javascript
   img.onerror = function() {
       if (this.dataset.remoteUrl && this.dataset.fallbackUsed === 'false') {
           console.log('[XHS] Local image failed, falling back to remote:', this.dataset.remoteUrl);
           this.dataset.fallbackUsed = 'true';
           this.src = this.dataset.remoteUrl;
       } else {
           // Show placeholder
       }
   };
   ```

---

## Verification

```bash
grep -n "localUrl\|remoteUrl\|fallbackUsed" MediaCrawler/viewer/static/js/app.js
```

---

## Success Criteria Met

- [x] 前端优先使用本地图片
- [x] 本地图片加载失败时自动切换到远程 URL
- [x] 不会出现无限循环 (fallbackUsed flag prevents this)
