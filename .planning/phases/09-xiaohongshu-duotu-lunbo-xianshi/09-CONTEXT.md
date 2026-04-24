# Phase 9: 小红书多图轮播显示 - Context

**Gathered:** 2026-04-24
**Status:** Ready for planning
**Mode:** Auto-generated (autonomous mode)

<domain>
## Phase Boundary

实现小红书卡片多图片显示和轮播交互功能。包括：
- 卡片上显示多图提示（数量角标）
- 点击卡片打开模态框，显示所有图片
- 图片下方圆点指示器，点击可切换
- 自动轮播每3秒切换一次
- 点击卡片后轮播计时器重置

**不包含：** 其他平台的多图显示、图片编辑功能

</domain>

<decisions>
## Implementation Decisions

### 卡片多图显示方式
- **D-01:** 使用单张图片+右下角数量角标（如"1/5"）的方式提示多图
  - 理由：简洁且不破坏现有卡片布局，符合用户对轮播的预期

### 轮播交互方式
- **D-02:** 图片下方圆点指示器，点击可切换
- **D-03:** 左右箭头按钮用于切换图片（已有实现，保留）
- **D-04:** 键盘左右箭头支持切换（已有实现，保留）

### 自动轮播行为
- **D-05:** 每3秒自动切换到下一张图片
- **D-06:** 鼠标悬停在图片上时暂停自动轮播
- **D-07:** 点击卡片（任意位置）后重置轮播计时器
- **D-08:** 轮播到最后一张时，循环回到第一张

### 数据获取方式
- **D-09:** 后端 API 返回所有图片 URL 列表
  - 修改 `format_note_for_response()` 返回 `image_urls` 数组（本地图片路径）
  - 同时保留 `remote_image_urls` 作为后备

### Claude's Discretion
- 轮播动画效果（淡入淡出或滑动）
- 圆点指示器的具体样式和位置
- 加载状态的显示方式

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 现有代码参考
- `MediaCrawler/api/routers/notes.py` — 小红书 API 路由
- `MediaCrawler/viewer/static/js/app.js` — 小红书前端主逻辑
- `MediaCrawler/viewer/static/js/modal.js` — 模态框组件

### 需求文档
- `.planning/REQUIREMENTS.md` — CAROUSEL-01 至 CAROUSEL-06

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `modal.js` 已有图片导航逻辑 (`navigateGallery()`)，可扩展支持自动轮播
- `notes.py` 已有 `get_local_image_count()` 函数获取图片数量
- `format_note_for_response()` 已返回 `local_image_url` 和 `remote_image_url`

### Established Patterns
- 图片懒加载使用 IntersectionObserver
- 模态框使用键盘事件监听（Escape、ArrowLeft、ArrowRight）
- CSS 使用 `.note-card` 和 `.modal-overlay` 命名模式

### Integration Points
- `openNoteModal(note)` — 需要接收完整图片列表
- `format_note_for_response()` — 需要返回所有图片 URL
- 卡片点击事件 — 需要重置轮播计时器

### 关键代码位置
- 后端: `MediaCrawler/api/routers/notes.py:180-236` — `format_note_for_response()`
- 前端: `MediaCrawler/viewer/static/js/modal.js:72-160` — `openNoteModal()`
- 卡片: `MediaCrawler/viewer/static/js/app.js:217-340` — `createNoteCard()`

</code_context>

<specifics>
## Specific Ideas

- 轮播间隔: 3秒（用户明确需求）
- 圆点指示器: 图片下方居中显示
- 自动轮播: 打开模态框即开始，鼠标悬停暂停

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 09-xiaohongshu-duotu-lunbo-xianshi*
*Context gathered: 2026-04-24*
