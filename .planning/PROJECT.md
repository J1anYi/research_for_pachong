# MediaCrawler 多平台社交媒体爬虫

## What This Is

MediaCrawler 是一个多平台社交媒体爬虫项目,支持小红书、抖音、B站、知乎等平台。

## Core Value

**爬虫数据必须实时推送到前端显示,图片必须可靠存储在本地** — 这是用户的核心期望,其他功能都为此服务。

## Current State

**Latest Release:** v2.0 (2026-04-24)

### What's Been Delivered

**v2.0 - 图片本地存储与任务队列** ✅
- 图片下载任务数据库 (SQLite)
- 消息队列 + Listener 架构 (asyncio.Queue)
- 定时任务扫描重试 (asyncio 后台任务)
- 前端优先显示本地图片
- 抖动间隔下载,避免限流
- 重试机制处理失败
- 小红书爬虫自动提交图片下载任务

**v1.0 - 前端体验优化** ✅
- WebSocket 实时数据推送
- 提醒框去重和优化
- 无限滚动加载
- 数据排序和 localStorage 持久化

### Current Features

- ✅ 多平台爬虫功能正常工作 — 小红书、抖音、B站、知乎等
- ✅ 数据存储功能正常 — JSONL/JSON/CSV/Excel/数据库
- ✅ 文件监控服务正常 — watchdog 检测文件变化
- ✅ WebSocket 实时数据推送
- ✅ 图片本地存储与任务队列 (小红书平台已集成)

## Next Milestone Goals

**v3.0:** 待规划

### Potential Features

1. **多平台图片下载支持**
   - 扩展至抖音、B站、知乎
   - 统一图片 URL 提取逻辑

2. **监控告警系统**
   - 存储空间告警
   - 任务失败告警
   - 队列积压告警

3. **性能优化**
   - 图片缩略图生成
   - CDN 上传支持
   - 批量下载优化

## Context

### 技术背景

- **后端**: Python + FastAPI + Uvicorn
- **前端**: 纯 HTML/CSS/JavaScript（无框架）
- **实时通信**: WebSocket
- **文件监控**: watchdog
- **任务数据库**: SQLite
- **消息队列**: asyncio.Queue
- **定时任务**: asyncio 后台任务

### 已归档里程碑

- [v2.0: 图片本地存储与任务队列](./milestones/v2.0-ROADMAP.md) — 2026-04-24
- [v1.0: 前端体验优化](./milestones/v1.0-ROADMAP.md) — 2026-04-22

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
| SQLite 存储任务状态 | 轻量级,无需额外依赖,适合中小规模 | ✓ 验证成功 (v2.0) |
| asyncio.Queue 消息队列 | Python 原生,简单可靠,适合单进程 | ✓ 验证成功 (v2.0) |
| asyncio 后台任务调度 | 不使用 APScheduler,减少依赖 | ✓ 验证成功 (v2.0) |

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
*Last updated: 2026-04-24 after milestone v2.0 completion*
