# MediaCrawler 多平台社交媒体爬虫

## What This Is

MediaCrawler 是一个多平台社交媒体爬虫项目，支持小红书、抖音、B站、知乎等平台。

## Core Value

**爬虫数据必须实时推送到前端显示，图片必须可靠存储在本地** — 这是用户的核心期望，其他功能都为此服务。

## Current Milestone: v2.0 图片本地存储与任务队列

**Goal:** 实现图片本地存储，通过任务队列机制解决限流和鉴权问题

**Target features:**
- 图片下载任务数据库 (SQLite)
- 消息队列 + Listener 架构 (asyncio.Queue)
- 定时任务扫描重试 (APScheduler)
- 前端优先显示本地图片
- 抖动间隔下载，避免限流
- 重试机制处理失败

## Requirements

### Validated (v1.0)

- ✓ 多平台爬虫功能正常工作 — 小红书、抖音、B站、知乎等
- ✓ 数据存储功能正常 — JSONL/JSON/CSV/Excel/数据库
- ✓ 文件监控服务正常 — watchdog 检测文件变化
- ✓ WebSocket 连接可以建立 — 前后端可以连接
- ✓ WebSocket 端点修复完成 — /ws/status 现在可以接收广播消息
- ✓ 实时数据推送功能完整可用
- ✓ 提醒框优化完成 — 去重、标题显示、显示时间
- ✓ 数据排序与无限滚动完成

### Active (v2.0)

- [ ] 图片下载任务数据库
- [ ] 消息队列架构
- [ ] 定时任务调度
- [ ] 前端图片显示优化

### Out of Scope

- 新增爬虫平台 — 本次只优化现有功能
- 重构前端架构 — 保持现有前端结构
- 热度排序 — v1.0 已延期

## Context

### 技术背景

- **后端**: Python + FastAPI + Uvicorn
- **前端**: 纯 HTML/CSS/JavaScript（无框架）
- **实时通信**: WebSocket
- **文件监控**: watchdog
- **任务数据库**: SQLite (新增)
- **消息队列**: asyncio.Queue (新增)
- **定时任务**: APScheduler (新增)

### v2.0 架构设计

```
爬虫 → 发布图片下载消息 → asyncio.Queue
                              ↓
                         Listener 消费
                              ↓
                    ┌─────────────────────┐
                    │   图片下载任务       │
                    │   (SQLite 记录状态)   │
                    └─────────────────────┘
                              ↓
                    ┌─────────────────────┐
                    │   APScheduler 定时   │
                    │   扫描重试失败任务    │
                    └─────────────────────┘
                              ↓
                         本地存储图片
                              ↓
                    前端优先使用本地路径
```

## Constraints

- **技术栈**: 必须使用现有的 FastAPI + WebSocket 架构
- **兼容性**: 不能破坏现有的爬虫功能
- **平台支持**: 必须支持所有已配置的平台（小红书、抖音、B站、知乎）
- **存储**: 图片存储路径需与现有 data/ 目录结构兼容

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 修改 /ws/status 端点连接到 manager | 让广播消息可以到达前端 | ✓ 修复完成 (v1.0) |
| 添加 type 字段到 crawler_status | 前端需要 type 字段来识别消息类型 | ✓ 修复完成 (v1.0) |
| SQLite 存储任务状态 | 轻量级，无需额外依赖，适合中小规模 | v2.0 |
| asyncio.Queue 消息队列 | Python 原生，简单可靠，适合单进程 | v2.0 |
| APScheduler 定时任务 | Python 内置调度器，支持 interval 和 cron | v2.0 |

---

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-23 after milestone v2.0 initialization*
