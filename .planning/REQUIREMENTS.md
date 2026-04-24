# Requirements: MediaCrawler 图片本地存储与任务队列

**Defined:** 2026-04-23
**Core Value:** 图片可靠存储在本地，前端能正常显示图片

## v1 Requirements (Completed)

### Bug 修复

- [x] **BUG-01**: 修复右上角"刷新"按钮点击无反应问题 ✅
- [x] **BUG-02**: 修复提醒框一直弹出的问题 ✅
- [x] **BUG-03**: 修复数据统计一直显示"新增 340 条数据"的问题 ✅

### 提醒框优化

- [x] **NOTIF-01**: 提醒框显示更新的内容标题 ✅
- [x] **NOTIF-02**: 提醒框维持时间延长 ✅
- [x] **NOTIF-03**: 提醒框去重 ✅

### 数据展示优化

- [x] **DATA-01**: 最新爬取的数据前置显示 ✅
- [x] **DATA-02**: 添加卡片排序功能 ✅
- [x] **DATA-03**: 数据更新时平滑滚动到新数据位置 ✅

## v2.0 Requirements

### 任务管理

- [ ] **TASK-01**: 创建图片下载任务数据库表（SQLite）- 包含 url, status, retry_count, created_at, updated_at 字段
- [ ] **TASK-02**: 任务状态管理 - 支持 pending, downloading, completed, failed 四种状态
- [ ] **TASK-03**: 任务重试机制 - 最大重试次数配置，指数退避策略
- [ ] **TASK-04**: 任务优先级支持 - 高优先级任务优先处理

### 消息队列

- [ ] **QUEUE-01**: 实现图片下载消息队列（asyncio.Queue）- 线程安全的消息传递
- [ ] **QUEUE-02**: 消息消费者 Listener - 从队列取出消息，执行下载
- [ ] **QUEUE-03**: 抖动间隔下载配置 - 可配置最小/最大间隔，避免限流
- [ ] **QUEUE-04**: 并发下载控制 - 可配置最大并发数

### 定时任务

- [ ] **SCHED-01**: 定时扫描未完成任务（APScheduler）- 定期检查 pending 和 failed 状态任务
- [ ] **SCHED-02**: 失败任务重试调度 - 超过退避时间后重新加入队列
- [ ] **SCHED-03**: 任务超时检测 - 下载超时自动标记为失败

### 图片存储

- [ ] **IMG-01**: 图片本地存储路径规划 - 按平台/日期组织目录结构
- [ ] **IMG-02**: 图片下载去重 - 同一 URL 不重复下载，使用 URL hash 判断
- [ ] **IMG-03**: 图片格式验证 - 下载后验证是否为有效图片
- [ ] **IMG-04**: 存储空间管理 - 可配置最大存储空间，LRU 清理

### 前端集成

- [ ] **FE-01**: API 返回本地图片路径 - notes API 返回 local_image_url 字段
- [ ] **FE-02**: 前端优先使用本地图片 - 检查 local_image_url 是否存在
- [ ] **FE-03**: 本地图片不存在时 fallback 到远程 URL - 保证图片始终能显示
- [ ] **FE-04**: 图片加载状态显示 - 加载中/加载失败状态提示

### 爬虫集成

- [ ] **CRAWL-01**: 爬虫发布图片下载任务消息 - 爬取完成后发送图片 URL 到队列 (Phase 8: 小红书)
- [ ] **CRAWL-02**: 支持多平台图片 URL 提取 - 小红书(Phase 8)、抖音/B站/知乎(Future)

## Future Requirements

### 增强功能

- **ENH-01**: 图片缩略图生成 - 减少前端加载时间
- **ENH-02**: 图片水印添加 - 版权保护
- **ENH-03**: CDN 上传 - 云存储备份

## Out of Scope

| Feature | Reason |
|---------|--------|
| 视频下载 | 本次只处理图片，视频下载更复杂 |
| 分布式任务队列 | 单进程 asyncio.Queue 足够，不需要 Celery/RabbitMQ |
| 实时进度推送 | 后续版本考虑 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TASK-01 | Phase 4 | Pending |
| TASK-02 | Phase 4 | Pending |
| TASK-03 | Phase 4 | Pending |
| TASK-04 | Phase 4 | Pending |
| QUEUE-01 | Phase 4 | Pending |
| QUEUE-02 | Phase 4 | Pending |
| QUEUE-03 | Phase 4 | Pending |
| QUEUE-04 | Phase 4 | Pending |
| SCHED-01 | Phase 5 | Pending |
| SCHED-02 | Phase 5 | Pending |
| SCHED-03 | Phase 5 | Pending |
| IMG-01 | Phase 6 | Pending |
| IMG-02 | Phase 6 | Pending |
| IMG-03 | Phase 6 | Pending |
| IMG-04 | Phase 6 | Pending |
| FE-01 | Phase 7 | Pending |
| FE-02 | Phase 7 | Pending |
| FE-03 | Phase 7 | Pending |
| FE-04 | Phase 7 | Pending |
| CRAWL-01 | Phase 8 | Pending |
| CRAWL-02 | Phase 8 | Pending |

**Coverage:**
- v1 requirements: 9 total (all completed)
- v2.0 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-23*
*Last updated: 2026-04-23 after milestone v2.0 initialization*
