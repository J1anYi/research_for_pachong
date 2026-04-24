# Phase 11: B站视频下载功能 - Context

**Gathered:** 2026-04-24
**Status:** Ready for planning
**Mode:** Auto-generated (autonomous mode)

<domain>
## Phase Boundary

实现B站视频手动下载，支持大视频分片和断点续传。包括：
- B站视频卡片显示下载按钮
- 点击按钮开始下载，显示进度
- 大视频（>50MB）自动分片下载
- 中断后可继续下载（断点续传）
- 下载失败自动重试

**不包含：** 其他平台视频下载、自动下载功能

</domain>

<decisions>
## Implementation Decisions

### 下载架构
- **D-01:** 复用 v2.0 的任务队列架构 (image_task_db.py)
- **D-02:** 创建 video_task_db.py 管理视频下载任务
- **D-03:** 使用 yt-dlp 进行视频下载

### 分片策略
- **D-04:** 大视频阈值：50MB
- **D-05:** 分片大小：10MB per chunk
- **D-06:** 断点续传：记录已下载字节范围

### 前端交互
- **D-07:** 下载按钮：B站视频卡片上显示
- **D-08:** 进度显示：百分比 + 进度条
- **D-09:** 状态管理：下载中、暂停、完成、失败

### Claude's Discretion
- 具体的 UI 样式
- 错误处理逻辑
- 重试策略细节

</decisions>

<canonical_refs>
## Canonical References

### 现有代码参考
- `MediaCrawler/api/services/image_task_db.py` — 任务数据库架构
- `MediaCrawler/viewer/static/js/bilibili-app.js` — B站前端
- `MediaCrawler/api/routers/bilibili.py` — B站 API

### 需求文档
- `.planning/REQUIREMENTS.md` — VIDEO-01 至 VIDEO-10

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `image_task_db.py` 的 SQLite 数据库架构
- `asyncio.Queue` 消息队列
- 定时任务扫描机制

### Integration Points
- B站视频卡片需要添加下载按钮
- 需要新的 API 端点管理视频任务
- WebSocket 用于实时进度推送

</code_context>

<specifics>
## Specific Ideas

- 下载按钮样式：参考现有的卡片交互
- 进度条：使用 CSS 动画效果
- 断点续传：使用 Range header

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 11-bilibili-shipin-xiazai-gongneng*
*Context gathered: 2026-04-24*
