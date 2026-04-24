---
title: feat: Realtime Multi-Platform Data Sync
type: feat
status: active
date: 2026-04-21
---

# feat: Realtime Multi-Platform Data Sync

## Overview

实现全平台实时数据同步功能：当爬虫完成数据爬取后，自动将新数据推送到viewer页面，无需手动刷新。当前系统仅监视小红书数据目录，其他平台（抖音、B站、知乎）的数据变化无法被检测到。

## Problem Frame

用户在API页面点击爬虫启动后，爬取的数据需要能立即在viewer页面显示。当前存在两个主要问题：

1. **文件监视器只监视小红书目录**：`file_watcher` 只监视 `data/xhs/jsonl/` 目录
2. **viewer页面没有WebSocket连接**：虽然有WebSocket基础设施，但viewer页面（`/viewer/`）的前端代码没有连接WebSocket来接收实时更新

## Requirements Trace

- R1. 文件监视器必须监视所有平台的数据目录（小红书、抖音、B站、知乎）
- R2. viewer页面必须连接WebSocket接收实时数据更新通知
- R3. 当某平台数据变化时，只通知该平台的viewer组件刷新数据
- R4. 新增平台数据目录不存在时，系统应能优雅处理

## Scope Boundaries

- 不修改爬虫核心逻辑或数据存储方式
- 不修改现有WebUI（`/`）的WebSocket功能
- 不添加数据库支持，保持JSONL文件读取方式

## Context & Research

### Relevant Code and Patterns

- `api/services/file_watcher.py` - 现有文件监视服务，使用watchdog库
- `api/routers/websocket.py` - WebSocket连接管理器，已有广播机制
- `api/main.py` - 应用启动时初始化文件监视器
- `viewer/static/js/app.js` - 小红书页面前端逻辑
- `viewer/static/js/douyin-app.js` - 抖音页面前端逻辑
- `viewer/static/js/bilibili-app.js` - B站页面前端逻辑
- `viewer/static/js/zhihu-app.js` - 知乎页面前端逻辑

### Institutional Learnings

- 现有WebSocket基础设施已经成熟，有 `ConnectionManager` 和广播机制
- 文件监视器使用watchdog库，跨平台兼容

### External References

- FastAPI WebSocket文档
- watchdog库文档

## Key Technical Decisions

- **多平台监视策略**: 扩展现有 `FileWatcherService` 支持监视多个目录，每个平台一个实例
- **消息路由**: WebSocket消息包含 `platform` 字段，前端根据平台过滤消息
- **前端集成**: 每个平台的前端模块独立管理WebSocket连接，保持模块化

## Open Questions

### Resolved During Planning

- Q: 是否需要为每个平台创建单独的WebSocket端点？ A: 否，使用单一WebSocket端点配合平台标识字段更简洁

### Deferred to Implementation

- WebSocket重连策略的具体实现细节
- 前端节流/防抖处理的具体延迟时间

## High-Level Technical Design

> *This illustrates the intended approach and is directional guidance for review, not implementation specification. The implementing agent should treat it as context, not code to reproduce.*

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Crawler writes │────▶│  File Watcher    │────▶│  WebSocket      │
│  to JSONL files │     │  (multi-platform)│     │  broadcast      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                              │
                        ┌─────────────────────────────────────┘
                        ▼
              ┌─────────────────────┐
              │  Viewer Frontend    │
              │  (WebSocket client) │
              │  - xhs-app.js       │
              │  - douyin-app.js    │
              │  - bilibili-app.js  │
              │  - zhihu-app.js     │
              └─────────────────────┘
```

## Implementation Units

- [ ] **Unit 1: 扩展文件监视器支持多平台**

**Goal:** 修改 `FileWatcherService` 支持监视多个平台的数据目录

**Requirements:** R1, R4

**Dependencies:** None

**Files:**
- Modify: `api/services/file_watcher.py`
- Modify: `api/main.py`

**Approach:**
- 重构 `FileWatcherService` 支持多实例或单实例多路径
- 添加平台标识，当文件变化时触发带平台信息的回调
- 在应用启动时为每个平台创建监视器
- 使用字典存储各平台目录路径和回调函数

**Patterns to follow:**
- 现有 `FileWatcherService` 的watchdog实现模式
- 现有 `broadcast_stats_update` 函数结构

**Test scenarios:**
- Happy path: 在xhs/jsonl目录写入新数据，触发回调
- Happy path: 在dy/jsonl目录写入新数据，触发回调
- Edge case: 平台目录不存在时，不抛出错误
- Integration: 爬虫写入数据后，文件监视器检测到变化

**Verification:**
- 文件监视器能检测到所有平台目录的数据变化
- 控制台输出显示正确的平台标识

---

- [ ] **Unit 2: 扩展WebSocket消息格式支持平台标识**

**Goal:** 修改WebSocket广播机制，消息包含平台标识，使前端能区分更新来源

**Requirements:** R3

**Dependencies:** Unit 1

**Files:**
- Modify: `api/routers/websocket.py`
- Modify: `api/schemas/crawler.py`

**Approach:**
- 创建新的消息类型 `DataUpdateMessage`，包含 `platform` 字段
- 添加平台特定的广播函数 `broadcast_platform_update(platform)`
- 保留现有 `broadcast_stats_update` 用于小红书兼容

**Patterns to follow:**
- 现有 `StatsUpdateMessage` schema
- 现有 `broadcast_stats_update` 函数结构

**Test scenarios:**
- Happy path: 广播xhs平台更新，消息包含 `platform: "xhs"`
- Happy path: 广播dy平台更新，消息包含 `platform: "dy"`
- Integration: WebSocket客户端收到正确格式的消息

**Verification:**
- WebSocket消息格式正确，包含平台标识
- 现有WebUI功能不受影响

---

- [ ] **Unit 3: 为viewer前端添加WebSocket客户端**

**Goal:** 在viewer页面的各平台JS模块中添加WebSocket连接和消息处理逻辑

**Requirements:** R2, R3

**Dependencies:** Unit 2

**Files:**
- Modify: `viewer/static/js/app.js` (小红书)
- Modify: `viewer/static/js/douyin-app.js` (抖音)
- Modify: `viewer/static/js/bilibili-app.js` (B站)
- Modify: `viewer/static/js/zhihu-app.js` (知乎)
- Create: `viewer/static/js/websocket-client.js` (共享模块)

**Approach:**
- 创建共享的WebSocket客户端模块，处理连接、重连、心跳
- 每个平台模块导入共享模块，订阅自己平台的消息
- 收到更新消息后自动调用现有的数据加载函数
- 添加连接状态指示器

**Patterns to follow:**
- 现有 `loadNotes()` / `loadDouyinData()` 等数据加载函数
- 现有WebSocket心跳机制（参考 `/ws/logs` 端点）

**Test scenarios:**
- Happy path: 页面加载后WebSocket自动连接
- Happy path: 收到本平台更新消息后自动刷新数据
- Edge case: WebSocket断开后自动重连
- Edge case: 连接失败时不影响手动刷新功能
- Integration: 爬虫完成后，viewer页面自动显示新数据

**Verification:**
- 打开viewer页面，启动爬虫，数据自动更新
- 控制台无WebSocket错误
- 连接断开后能自动重连

---

- [ ] **Unit 4: 添加连接状态UI指示器**

**Goal:** 在viewer页面显示WebSocket连接状态，提升用户体验

**Requirements:** R2

**Dependencies:** Unit 3

**Files:**
- Modify: `viewer/static/index.html`
- Modify: `viewer/static/css/style.css`

**Approach:**
- 在页面header区域添加连接状态指示器
- 使用CSS动画表示连接中/已连接/断开状态
- 状态变化时有轻微动画过渡

**Patterns to follow:**
- 现有Neon Cyberpunk主题的视觉风格
- 现有 `.refresh-btn` 的动效模式

**Test scenarios:**
- Happy path: WebSocket连接后显示"已连接"状态
- Happy path: WebSocket断开后显示"断开"状态
- Edge case: 重连中显示"连接中"状态

**Verification:**
- 连接状态指示器正确反映WebSocket状态
- 动画流畅，不影响页面性能

## System-Wide Impact

- **Interaction graph:** 文件监视器回调 -> WebSocket广播 -> 前端消息处理 -> 数据刷新
- **Error propagation:** 文件监视器错误记录到控制台，不中断服务；WebSocket连接失败允许重试
- **State lifecycle risks:** WebSocket断开期间可能丢失更新，前端重连后应主动刷新一次数据
- **API surface parity:** 不影响现有API端点
- **Integration coverage:** 需要端到端测试：爬虫 -> 文件监视器 -> WebSocket -> 前端刷新

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| 多个文件监视器实例可能增加资源消耗 | 使用单实例多路径模式，共享Observer |
| WebSocket在高并发下可能有性能问题 | 现有ConnectionManager已有广播优化 |
| 前端频繁刷新可能影响用户体验 | 添加防抖处理，避免短时间内多次刷新 |

## Documentation / Operational Notes

- 部署时确保所有平台数据目录存在或有创建权限
- 监控WebSocket连接数，避免过多空闲连接

## Sources & References

- **Origin document:** 用户需求讨论
- Related code: `api/services/file_watcher.py`, `api/routers/websocket.py`
- External docs: FastAPI WebSocket, Python watchdog library
