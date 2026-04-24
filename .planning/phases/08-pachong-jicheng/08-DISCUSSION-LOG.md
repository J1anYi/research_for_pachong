# Phase 8: 爬虫集成 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-24
**Phase:** 08-pachong-jicheng
**Areas discussed:** 集成架构, 异步处理, 错误处理, 平台范围, 多图处理, 视频处理

---

## 集成架构

| Option | Description | Selected |
|--------|-------------|----------|
| 存储层集成 | 在 update_xhs_note 等存储函数中，数据保存后立即发送图片任务。优点：统一入口，所有存储方式都受益 | ✓ |
| 爬虫层集成 | 在爬虫 core.py 获取数据后立即发送。优点：更早提交任务；缺点：需要修改每个爬虫 | |
| 事件驱动集成 | 创建独立的集成服务，监听数据保存事件。优点：解耦；缺点：增加复杂度 | |

**User's choice:** 存储层集成
**Notes:** 统一入口，所有存储方式（csv/json/jsonl/db）都受益

---

## 异步处理

| Option | Description | Selected |
|--------|-------------|----------|
| fire-and-forget | 不阻塞爬虫主流程，即使队列满也不影响数据保存。适合生产环境 | ✓ |
| await 直接等待 | 等待 enqueue 完成，确保任务入队。可能轻微阻塞爬虫 | |

**User's choice:** fire-and-forget
**Notes:** 使用 `asyncio.create_task` 实现非阻塞调用

---

## 错误处理

| Option | Description | Selected |
|--------|-------------|----------|
| 记录日志继续 | enqueue 失败只记录日志，不影响爬虫主流程。图片下载是辅助功能 | ✓ |
| 重试入队 | 失败时重试几次。可能影响爬虫性能 | |

**User's choice:** 记录日志继续
**Notes:** 图片下载是辅助功能，不应影响爬虫主功能

---

## 平台范围

| Option | Description | Selected |
|--------|-------------|----------|
| 仅小红书 | 先完成小红书集成，验证后再扩展其他平台。降低风险 | ✓ |
| 所有平台一起 | 同时修改所有平台存储代码。工作量大 | |

**User's choice:** 仅小红书
**Notes:** 先验证单平台集成，降低风险

---

## 多图处理

| Option | Description | Selected |
|--------|-------------|----------|
| 逐个入队 | 每个图片 URL 独立入队，并行下载。适合大多数场景 | ✓ |
| 批量入队 | 所有图片作为一组入队。需要新增批量接口 | |

**User's choice:** 逐个入队
**Notes:** 遍历 image_list，逐个调用 enqueue

---

## 视频处理

| Option | Description | Selected |
|--------|-------------|----------|
| 忽略视频 | 本 Phase 仅处理图片，视频下载作为后续 Phase | ✓ |
| 同时处理视频 | 视频 URL 也入队。需要扩展下载服务支持视频 | |

**User's choice:** 忽略视频
**Notes:** 本 Phase 仅处理图片，视频下载更复杂

---

## Claude's Discretion

- 具体的代码实现细节（由 planner 和 executor 决定）
- 日志格式和级别
- 是否需要添加配置开关

## Deferred Ideas

- 抖音集成 — 待小红书验证后
- B站集成 — 待小红书验证后
- 知乎集成 — 待小红书验证后
- 视频下载功能 — 需要 Phase 9 或后续版本
