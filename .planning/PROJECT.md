# MediaCrawler 实时数据推送修复

## What This Is

MediaCrawler 是一个多平台社交媒体爬虫项目，支持小红书、抖音、B站、知乎等平台。

本次工作目标是**修复实时数据推送功能**，让爬取的数据能够实时显示在前端界面上。之前 WebSocket 推送一直不成功，现已修复核心问题。

## Core Value

**爬虫数据必须实时推送到前端显示** — 这是用户的核心期望，其他功能都为此服务。

## Requirements

### Validated

- ✓ 多平台爬虫功能正常工作 — 小红书、抖音、B站、知乎等
- ✓ 数据存储功能正常 — JSONL/JSON/CSV/Excel/数据库
- ✓ 文件监控服务正常 — watchdog 检测文件变化
- ✓ WebSocket 连接可以建立 — 前后端可以连接
- ✓ WebSocket 端点修复完成 — /ws/status 现在可以接收广播消息

### Active

- [ ] 验证实时数据推送功能完整可用
- [ ] 确认所有平台（小红书、抖音、B站、知乎）都能正常推送
- [ ] 测试前端通知弹窗显示正确

### Out of Scope

- 新增爬虫平台 — 本次只修复现有平台的推送功能
- 重构前端架构 — 保持现有前端结构
- 性能优化 — 先确保功能正确

## Context

### 技术背景

- **后端**: Python + FastAPI + Uvicorn
- **前端**: 纯 HTML/CSS/JavaScript（无框架）
- **实时通信**: WebSocket
- **文件监控**: watchdog

### 问题根因

WebSocket 端点配置不匹配：
- 前端 WSClient 连接到 `/api/ws/status`
- 但 `/ws/status` 端点没有连接到 `ConnectionManager`
- 导致 `broadcast_platform_update()` 发送的消息无法到达前端

### 修复方案

让 `/ws/status` 端点连接到 `ConnectionManager`，使其可以接收广播消息。

## Constraints

- **技术栈**: 必须使用现有的 FastAPI + WebSocket 架构
- **兼容性**: 不能破坏现有的爬虫功能
- **平台支持**: 必须支持所有已配置的平台（小红书、抖音、B站、知乎）

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 修改 /ws/status 端点连接到 manager | 让广播消息可以到达前端 | ✓ 修复完成 |
| 添加 type 字段到 crawler_status | 前端需要 type 字段来识别消息类型 | ✓ 修复完成 |

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
*Last updated: 2026-04-22 after initialization*
