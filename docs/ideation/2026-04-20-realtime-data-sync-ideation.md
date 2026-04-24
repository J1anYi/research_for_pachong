---
date: 2026-04-20
topic: realtime-data-sync
focus: 实现 new_note WebSocket 消息，让 viewer 实时更新爬取数据
---

# Ideation: 实时数据同步

## 问题描述

用户报告：点击爬取后，viewer 页面不会实时更新数据，即使手动刷新也无法获取最新内容。

## Codebase Context

### 项目结构
- **Backend**: FastAPI (`MediaCrawler/api/`)
- **Frontend**: 静态 HTML/JS (`MediaCrawler/viewer/static/`)
- **Data**: JSONL 文件存储 (`data/xhs/jsonl/`)
- **WebSocket**: `/ws/logs` 和 `/ws/status` 两个端点

### 数据流现状
```
POST /api/crawler/start
    → subprocess (main.py)
    → 写入 JSONL 文件
    → Viewer 调用 GET /api/notes
    → 读取 JSONL 文件返回
```

### 问题根源
1. **前端已准备好接收**: `handleWebSocketMessage()` 期望 `new_note` 和 `stats_update` 消息类型
2. **后端从未发送**: WebSocket 只广播日志和状态，从不发送笔记数据
3. **无写入通知**: 爬虫写 JSONL 文件时，FastAPI 主进程完全不知情

### 现有模式可复用
- `crawler_manager.get_log_queue()` - 日志队列
- `log_broadcaster()` - 日志广播后台任务
- `ConnectionManager.broadcast()` - WebSocket 广播管理

## Ranked Ideas

### 1. 实现 `new_note` WebSocket 消息 (已选定)

**Description:**
在 `CrawlerManager` 中添加笔记队列，爬虫完成时发送 `new_note` WebSocket 消息。复用现有的 `log_broadcaster` 模式。

**Rationale:**
- 前端代码已存在处理逻辑，只需后端发送
- 复用现有 WebSocket 基础设施
- 与 log queue 模式一致，代码风格统一

**Downsides:**
- 需要从爬虫输出中解析笔记数据
- 可能需要调整日志输出格式

**Confidence:** 95%

**Complexity:** Low

**Status:** Explored - 待进入 Brainstorm

---

### 2. 扩展 `/ws/status` 载荷

**Description:**
在状态广播中加入 `stats_update` 消息类型，检测笔记数量变化时触发前端刷新。

**Rationale:**
- 改动最小，只需修改一个函数
- 利用现有轮询机制

**Downsides:**
- 不是真正的事件驱动
- 依赖 1 秒轮询间隔

**Confidence:** 90%

**Complexity:** Very Low

**Status:** Unexplored

---

### 3. JSONL 文件监视器

**Description:**
使用 `watchdog` 库监听 `data/xhs/jsonl/` 目录变化，文件追加时解析并发送通知。

**Rationale:**
- 完全解耦，不修改爬虫代码
- 适用于多种数据来源

**Downsides:**
- 需要新依赖
- 文件系统事件可能有延迟

**Confidence:** 85%

**Complexity:** Low-Medium

**Status:** Unexplored

---

### 4. 混合推送 + 拉取

**Description:**
WebSocket 主导，断开时自动降级为轮询 `GET /api/notes`。

**Rationale:**
- 增强系统鲁棒性
- 保证数据最终到达

**Downsides:**
- 增加前端复杂度
- 当前需求可能不需要

**Confidence:** 80%

**Complexity:** Low

**Status:** Unexplored

---

### 5. 游标式增量读取

**Description:**
追踪每个客户端的读取位置，只返回新增的笔记。

**Rationale:**
- 减少数据传输量
- 避免重复读取

**Downsides:**
- 增加状态管理复杂度
- 当前数据量可能不需要

**Confidence:** 70%

**Complexity:** Medium

**Status:** Unexplored

## Rejection Summary

| # | Idea | Reason Rejected |
|---|------|-----------------|
| 1 | 乐观 UI 占位卡片 | 解决感知问题而非根本问题 |
| 2 | 防抖批量更新 | 当前爬取频率不需要 |
| 3 | 事件溯源 + 重放 | 过度设计 |
| 4 | Redis Pub/Sub | 引入新依赖，不需要跨进程通信 |
| 5 | SSE 端点 | 已有 WebSocket，不需第二套机制 |
| 6 | 写入钩子回调 | 需修改爬虫核心代码，风险高 |
| 7 | 笔记广播队列 | 与方案 1 重复，已合并 |

## Session Log

- 2026-04-20: Initial ideation — 12 candidates generated, 5 survived, selected "new_note WebSocket" for implementation
