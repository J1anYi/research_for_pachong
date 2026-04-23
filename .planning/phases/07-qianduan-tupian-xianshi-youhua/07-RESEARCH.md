# Phase 7: 前端图片显示优化 - Research

**Phase:** 07
**Date:** 2026-04-23

---

## 现有实现分析

### API 端 (notes.py)

**当前实现:**
- `format_note_for_response()` 返回笔记数据
- `first_image_url` 字段格式: `/images/{note_id}/0.jpg`
- 使用 `get_local_image_count()` 检查本地图片数量
- 没有使用 ImageStorageService 的 `get_local_path()` 方法

**需要修改:**
- 添加 `local_image_url` 字段
- 使用 `image_storage.get_local_path(url, platform)` 检查图片是否已下载
- 返回本地路径或远程 URL

### 前端端 (app.js)

**当前实现:**
```javascript
function createNoteCard(note) {
    if (note.first_image_url) {
        const img = document.createElement('img');
        img.dataset.src = note.first_image_url;
        img.onerror = () => {
            img.style.display = 'none';
            // 显示占位符
        };
    }
}
```

**需要修改:**
- 优先使用 `local_image_url`
- 添加 fallback 机制：本地失败 → 远程 URL
- 添加加载状态显示

---

## 技术方案

### FE-01: API 返回本地图片路径

**方案:**
1. 在 `format_note_for_response()` 中添加 `local_image_url` 字段
2. 使用 `image_storage.get_local_path(image_url, "xhs")` 检查本地图片
3. 如果存在，返回 `/local-images/{path}` 格式的 URL
4. 否则返回原始远程 URL

**关键点:**
- 需要添加静态文件路由服务本地图片
- 路径格式: `/local-images/{platform}/images/{year}/{month}/{day}/{hash}.jpg`

### FE-02: 前端优先使用本地图片

**方案:**
```javascript
const img = document.createElement('img');
if (note.local_image_url) {
    img.dataset.src = note.local_image_url;
    img.dataset.fallbackUrl = note.first_image_url; // 远程 fallback
} else {
    img.dataset.src = note.first_image_url;
}
```

### FE-03: 本地图片不存在时 fallback

**方案:**
```javascript
img.onerror = () => {
    if (img.dataset.fallbackUrl && img.src !== img.dataset.fallbackUrl) {
        img.src = img.dataset.fallbackUrl; // 尝试远程 URL
    } else {
        // 显示错误占位符
    }
};
```

### FE-04: 图片加载状态显示

**方案:**
- 添加 CSS 类 `.image-loading`, `.image-loaded`, `.image-error`
- 使用 `onload` 和 `onerror` 事件切换状态
- 加载中显示骨架屏或 spinner

---

## 文件依赖

| 文件 | 修改内容 |
|------|----------|
| `api/routers/notes.py` | 添加 local_image_url 字段 |
| `api/main.py` | 添加本地图片静态路由 |
| `viewer/static/js/app.js` | 修改 createNoteCard 函数 |
| `viewer/static/css/style.css` | 添加加载状态样式 |

---

## 依赖关系

Phase 7 依赖 Phase 6 的 ImageStorageService:
- `image_storage.get_local_path(url, platform)` - 查找本地图片
- `image_storage.get_storage_path()` - 生成存储路径

---

## RESEARCH COMPLETE
