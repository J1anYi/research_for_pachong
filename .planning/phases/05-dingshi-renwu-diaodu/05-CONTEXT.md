# Phase 5: 定时任务调度 - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning

<domain>
## Phase Boundary

实现任务监控和自动重试机制 — 定时扫描未完成任务、失败任务重试调度、任务超时检测。

**In scope:**
- 定时扫描任务数据库（扫描 pending/downloading 状态任务）
- 失败任务重试调度（检查 next_retry_at 时间）
- 任务超时检测（标记超时的 downloading 任务为 failed）
- 调度器状态监控（通过扩展 /api/image-queue/stats 端点）

**Out of scope:**
- 手动调度控制 API（暂停/恢复/触发）
- 前端调度器管理界面
- 分布式任务调度（单进程足够）

</domain>

<decisions>
## Implementation Decisions

### 调度器配置

- **D-01: 扫描间隔** — 5 分钟
  - 平衡频率和数据库负载
  - 足够及时处理失败任务
  - 不会过度查询数据库

- **D-02: 超时阈值** — 120 秒
  - 标准超时，容忍较慢的网络
  - downloading 状态超过 120 秒视为超时
  - 超时任务自动标记为 failed

- **D-03: 最大重试次数** — 5 次（继承自 Phase 4）
  - 已在 `mark_failed()` 中实现
  - 指数退避：1s, 2s, 4s, 8s, 16s

### 监控与控制

- **D-04: 监控方式** — 扩展现有 API
  - 扩展 `/api/image-queue/stats` 端点
  - 添加调度器状态信息（运行状态、上次扫描时间、下次扫描时间）
  - 不创建新的独立端点

- **D-05: 控制能力** — 仅监控，不控制
  - 不提供暂停/恢复 API
  - 不提供手动触发 API
  - 调度器自动运行，通过 lifespan 管理

### Claude's Discretion

- APScheduler 的具体配置方式（interval 触发器参数）
- 扫描任务的具体实现逻辑
- 错误处理和日志格式

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 现有架构模式
- `api/main.py` — FastAPI lifespan 管理后台任务启停
- `api/services/image_task_db.py` — 任务数据库服务（已实现 mark_failed, get_pending_task）
- `api/services/image_queue.py` — 消息队列服务（已实现 enqueue_from_db）
- `api/routers/image_queue.py` — 现有 /api/image-queue/stats 端点

### Prior Phase Context
- Phase 4: 任务数据库与消息队列基础
  - `image_tasks` 表包含 `next_retry_at` 字段
  - `mark_failed()` 实现指数退避重试
  - 3 个消费者协程已运行
  - 抖动间隔 0.5-2.0 秒已配置

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **lifespan 模式**: `api/main.py` 已使用 `@asynccontextmanager` 管理服务启停
- **image_task_db**: 已有 `get_pending_task()`, `update_status()`, `mark_failed()` 方法
- **image_queue_service**: 已有 `enqueue_from_db()` 方法可复用
- **StatsResponse**: 现有 Pydantic 模型可扩展

### Established Patterns
- **服务初始化**: 在 lifespan startup 中启动服务，shutdown 中停止
- **单例模式**: 全局单例服务实例
- **日志输出**: `print(f"[ServiceName] message")` 格式

### Integration Points
- 新服务 `image_scheduler.py` 需在 lifespan 中初始化
- 扩展 `StatsResponse` 模型添加调度器状态字段
- 调度器需要访问 `image_task_db` 查询任务状态

### Known Constraints
- 必须使用 asyncio 异步模式（FastAPI 要求）
- 不能阻塞主事件循环
- APScheduler 需使用 AsyncIOScheduler

</code_context>

<specifics>
## Specific Ideas

- 调度器服务名: `ImageSchedulerService`
- 扫描间隔: 5 分钟
- 超时阈值: 120 秒
- 最大重试: 5 次（继承自 Phase 4）
- 监控端点: 扩展 `/api/image-queue/stats`

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-dingshi-renwu-diaodu*
*Context gathered: 2026-04-23*
