# Phase 4: 任务数据库与消息队列基础 - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning

<domain>
## Phase Boundary

建立图片下载任务的基础架构 — SQLite 任务数据库、asyncio.Queue 消息队列、下载消费者 Listener、抖动间隔下载、并发控制。

**In scope:**
- 创建 SQLite 任务数据库表（image_tasks）
- 任务状态管理（pending/downloading/completed/failed）
- 任务重试机制（指数退避）
- 任务优先级支持（高/中/低）
- 实现图片下载消息队列（asyncio.Queue）
- 消息消费者 Listener
- 抖动间隔下载配置
- 并发下载控制
- 任务去重检查

**Out of scope:**
- 定时任务调度（Phase 5）
- 图片存储路径规划（Phase 6）
- 前端图片显示优化（Phase 7）
- 爬虫集成（Phase 8）

</domain>

<decisions>
## Implementation Decisions

### 任务数据模型

- **D-01: 任务状态机** — 四状态设计
  - `pending` → `downloading` → `completed` / `failed`
  - 重试时 `failed` → `pending`
  - 简单清晰，覆盖所有场景

- **D-02: 重试退避策略** — 指数退避
  - 每次重试间隔翻倍：1s, 2s, 4s, 8s...
  - 最大重试次数可配置
  - 避免雪崩效应，业界标准做法

- **D-03: 任务优先级** — 三级优先级
  - `high` / `medium` / `low`
  - 足够灵活又不过度复杂
  - 高优先级任务优先出队

- **D-04: 数据库字段设计**
  - `id` — 主键（自增 INTEGER）
  - `url` — 图片 URL（TEXT，唯一索引）
  - `status` — 任务状态（TEXT，索引）
  - `retry_count` — 重试次数（INTEGER，默认 0）
  - `priority` — 优先级（TEXT，默认 'medium'，索引）
  - `created_at` — 创建时间（TEXT，ISO 格式）
  - `updated_at` — 更新时间（TEXT，ISO 格式）
  - `error_message` — 错误信息（TEXT，可空）

### 队列架构

- **D-05: 消费者数量** — 2-3 个并发消费者
  - 适度并发，平衡下载效率和限流风险
  - 使用 `asyncio.create_task` 创建多个消费者协程

- **D-06: 队列容量** — 有上限（100-500）
  - 有限容量防止内存溢出
  - 队列满时新任务写入数据库等待调度
  - 可通过配置调整

- **D-07: 任务分发策略** — 消费者去重检查
  - 消费者从队列取任务后检查数据库状态
  - 若状态已变（如已被其他消费者处理）则跳过
  - 避免重复下载

### 去重策略

- **D-08: 图片唯一标识** — URL 直接比较
  - 用完整 URL 作为唯一标识
  - 不同 URL = 不同图片
  - 最简单可靠

- **D-09: 去重检查范围** — 检查所有状态
  - 检查所有状态的记录（pending/downloading/completed/failed）
  - pending/downloading 的也算存在
  - 避免重复入队

### Claude's Discretion

- 抖动间隔的具体范围（min_interval, max_interval）
- 并发下载的超时时间
- 错误分类和对应的处理策略
- 数据库文件的具体位置

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 现有架构模式
- `api/main.py` — FastAPI lifespan 管理后台任务启停
- `api/services/file_watcher.py` — 线程安全模式（`threading.Lock`）、asyncio 协程模式
- `api/routers/websocket.py` — ConnectionManager 广播模式、`asyncio.create_task` 并发

### 配置参考
- `api/services/file_watcher.py` — PLATFORMS 列表定义

### Prior Phase Context
- Phase 3: 使用 `asyncio.create_task` 处理并发

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **lifespan 模式**: `api/main.py` 已使用 `@asynccontextmanager` 管理服务启停
- **线程安全**: `file_watcher.py` 使用 `threading.Lock` 保护共享状态
- **asyncio 协程**: 项目已大量使用 asyncio 异步模式

### Established Patterns
- **服务初始化**: 在 lifespan startup 中启动服务，shutdown 中停止
- **单例模式**: `file_watcher = FileWatcherService()` 全局单例
- **日志输出**: `print(f"[ServiceName] message")` 格式

### Integration Points
- 新服务 `image_task_db.py` 需在 lifespan 中初始化
- 新服务 `image_queue.py` 需在 lifespan 中启动消费者
- 新服务 `image_downloader.py` 提供下载函数供消费者调用

### Known Constraints
- 必须使用 asyncio 异步模式（FastAPI 要求）
- 不能阻塞主事件循环
- 需要考虑多消费者竞争同一任务的情况

</code_context>

<specifics>
## Specific Ideas

- 任务表名: `image_tasks`
- 状态枚举: `pending`, `downloading`, `completed`, `failed`
- 优先级枚举: `high`, `medium`, `low`
- 消费者数量: 2-3 个
- 队列容量: 100-500
- 重试策略: 指数退避（1s, 2s, 4s, 8s...）

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-renwu-shujuku-yu-xiaoxi-duilie-jichu*
*Context gathered: 2026-04-23*
