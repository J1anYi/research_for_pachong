# Roadmap: MediaCrawler 图片本地存储与任务队列

**Created:** 2026-04-23
**Project:** MediaCrawler 图片本地存储与任务队列
**Milestone:** v2.0
**Phases:** 5
**Requirements:** 20

---

## Phase 4: 任务数据库与消息队列基础 ✅

**Goal:** 建立图片下载任务的基础架构

**Status:** complete

**Completed:** 2026-04-23

### Requirements

- TASK-01: 创建图片下载任务数据库表（SQLite）
- TASK-02: 任务状态管理
- TASK-03: 任务重试机制
- TASK-04: 任务优先级支持
- QUEUE-01: 实现图片下载消息队列
- QUEUE-02: 消息消费者 Listener
- QUEUE-03: 抖动间隔下载配置
- QUEUE-04: 并发下载控制

### Success Criteria

1. SQLite 数据库表创建成功，包含所有必要字段
2. 任务状态可正确转换（pending → downloading → completed/failed）
3. 失败任务可自动重试，遵循退避策略
4. 消息队列正常工作，消费者能处理消息
5. 下载间隔可配置，避免触发限流

### Technical Approach

1. **数据库设计**
   - 创建 `image_tasks` 表
   - 字段: id, url, status, retry_count, priority, created_at, updated_at, error_message
   - 添加索引: url (unique), status, priority

2. **消息队列**
   - 使用 asyncio.Queue 实现生产者-消费者模式
   - Listener 协程持续从队列取消息
   - 支持 asyncio.create_task 并发消费

3. **抖动间隔**
   - 配置项: min_interval, max_interval
   - random.uniform(min_interval, max_interval) 实现抖动

### Key Files

- `api/services/image_task_db.py` - SQLite 任务数据库 (新建)
- `api/services/image_queue.py` - 消息队列服务 (新建)
- `api/services/image_downloader.py` - 图片下载服务 (新建)

---

## Phase 5: 定时任务调度 ✅

**Goal:** 实现任务监控和自动重试机制

**Status:** complete

**Completed:** 2026-04-23

**Plans:** 3

### Requirements

- SCHED-01: 定时扫描未完成任务
- SCHED-02: 失败任务重试调度
- SCHED-03: 任务超时检测

### Success Criteria

1. 定时任务每 5 分钟扫描一次任务数据库
2. 失败任务超过退避时间后自动重新入队
3. 下载超时（120 秒）的任务自动标记为失败
4. 可配置扫描间隔和超时阈值

### Technical Approach

1. **asyncio 后台任务**
   - 使用 `asyncio.create_task` + `asyncio.sleep` 实现定时循环
   - 不使用 APScheduler（避免额外依赖）
   - 集成到现有 lifespan 管理

2. **超时检测**
   - 查询 `status=downloading` 且 `updated_at < (now - 120秒)` 的任务
   - 调用 `mark_failed()` 标记为失败

3. **重试调度**
   - 查询 `status=pending` 且 `next_retry_at <= now` 的任务
   - 重新入队并清除 `next_retry_at`

### Key Files

- `api/services/image_scheduler.py` - 定时任务调度 (新建)
- `api/services/image_task_db.py` - 添加查询方法 (修改)
- `api/routers/image_queue.py` - 扩展 stats 端点 (修改)
- `api/main.py` - 应用启动时初始化调度器 (修改)

### Plans

| Plan | Wave | Description | Files |
|------|------|-------------|-------|
| 05-01 | 1 | Add DB query methods | image_task_db.py |
| 05-02 | 2 | Create scheduler service | image_scheduler.py, __init__.py |
| 05-03 | 3 | Integrate with FastAPI | main.py, image_queue.py |

### Configuration (User Decisions)

- D-01: 扫描间隔 = 5 分钟
- D-02: 超时阈值 = 120 秒
- D-03: 最大重试 = 5 次
- D-04: 监控方式 = 扩展 /api/image-queue/stats
- D-05: 控制能力 = 仅监控，不控制

---

## Phase 6: 图片存储管理

**Goal:** 实现可靠的图片存储和去重机制

**Status:** pending

### Requirements

- IMG-01: 图片本地存储路径规划
- IMG-02: 图片下载去重
- IMG-03: 图片格式验证
- IMG-04: 存储空间管理

### Success Criteria

1. 图片按 `{data_dir}/{platform}/images/{year}/{month}/{day}/{hash}.jpg` 存储
2. 相同 URL 不会重复下载
3. 无效图片（如 HTML 错误页面）会被检测并删除
4. 存储空间超限时自动清理最旧图片

### Technical Approach

1. **路径规划**
   - 使用 hashlib.md5(url).hexdigest()[:16] 作为文件名
   - 按日期分目录，便于管理

2. **去重**
   - 下载前检查数据库中是否已有相同 URL 的 completed 任务
   - 存在则直接返回本地路径

3. **格式验证**
   - 使用 PIL 验证图片格式
   - 检测文件头 magic bytes

### Key Files

- `api/services/image_storage.py` - 图片存储服务 (新建)
- `api/services/image_task_db.py` - 添加去重查询 (修改)

---

## Phase 7: 前端图片显示优化

**Goal:** 前端优先使用本地图片，提供流畅的图片加载体验

**Status:** pending

### Requirements

- FE-01: API 返回本地图片路径
- FE-02: 前端优先使用本地图片
- FE-03: 本地图片不存在时 fallback 到远程 URL
- FE-04: 图片加载状态显示

### Success Criteria

1. notes API 返回的数据包含 local_image_url 字段
2. 前端图片 src 优先使用本地路径
3. 本地图片加载失败时自动切换到远程 URL
4. 图片加载中显示占位符，加载失败显示错误图标

### Technical Approach

1. **API 修改**
   - 在 format_note_for_response 中检查本地图片是否存在
   - 存在则返回 local_image_url

2. **前端修改**
   - 修改 createNoteCard 使用 local_image_url
   - 添加 onerror 处理 fallback

### Key Files

- `api/routers/notes.py` - 添加 local_image_url 字段 (修改)
- `viewer/static/js/app.js` - 前端图片显示逻辑 (修改)

---

## Phase 8: 爬虫集成

**Goal:** 爬虫自动发布图片下载任务

**Status:** pending

### Requirements

- CRAWL-01: 爬虫发布图片下载任务消息
- CRAWL-02: 支持多平台图片 URL 提取

### Success Criteria

1. 爬虫爬取完成后自动发送图片下载消息
2. 支持小红书、抖音、B站、知乎四个平台
3. 多图笔记能正确发送所有图片任务

### Technical Approach

1. **消息发布**
   - 在爬虫保存数据后调用 image_queue.enqueue(image_url)
   - 异步发送，不阻塞爬虫主流程

2. **多平台适配**
   - 从各平台数据结构中提取图片 URL 列表
   - 统一发送到同一队列

### Key Files

- `media_crawler/` - 各平台爬虫代码 (修改)
- `api/services/image_queue.py` - 提供 enqueue 接口 (修改)

---

## Summary

| Phase | Goal | Requirements | Status |
|-------|------|--------------|--------|
| 4 | 任务数据库与消息队列基础 | 8 | complete ✅ |
| 5 | 定时任务调度 | 3 | complete ✅ |
| 6 | 图片存储管理 | 4 | pending |
| 7 | 前端图片显示优化 | 4 | pending |
| 8 | 爬虫集成 | 2 | pending |

---
*Last updated: 2026-04-23*
