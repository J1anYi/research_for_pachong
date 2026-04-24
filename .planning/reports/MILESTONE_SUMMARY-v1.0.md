# Milestone v1.0 — MediaCrawler 前端体验优化

**Generated:** 2026-04-23
**Purpose:** Team onboarding and project review

---

## 1. Project Overview

**MediaCrawler** 是一个多平台社交媒体爬虫项目，支持小红书、抖音、B站、知乎等平台。

本次里程碑目标是**修复实时数据推送功能并优化前端体验**，让爬取的数据能够实时显示在前端界面上，并提供流畅的用户交互体验。

### Core Value

**用户能清晰看到实时更新的数据，操作流畅** — 这是用户的核心期望，其他功能都为此服务。

### Tech Stack

- **后端**: Python + FastAPI + Uvicorn
- **前端**: 纯 HTML/CSS/JavaScript（无框架）
- **数据存储**: JSONL/JSON 文件
- **实时通信**: WebSocket
- **文件监控**: watchdog

---

## 2. Architecture & Technical Decisions

| Decision | Why | Phase |
|----------|-----|-------|
| stats_update 不触发通知 | 每次文件变更触发两个消息导致重复通知，stats_update 仅用于统计展示 | Phase 2 |
| 基于 content hash 的去重机制 | 使用 platform + titles + count 作为哈希键，5 秒时间窗口内跳过重复通知 | Phase 2 |
| titles 显示最多 2 条 | 通知详情显示前 2 条标题，超出显示 "等N条"，保持简洁 | Phase 2 |
| 后端计算增量而非前端 | 后端追踪记录总数变化，计算 new_count = current - previous，避免前端状态管理 | Phase 2 |
| 异步读取最新记录标题 | 使用 aiofiles 异步读取 JSONL/JSON 文件，获取最新记录标题用于通知展示 | Phase 2 |
| IntersectionObserver 实现无限滚动 | 使用 rootMargin: '100px' 提前触发加载，平滑用户体验 | Phase 3 |
| localStorage 持久化排序偏好 | 用户选择的排序方式保存到 localStorage，下次访问保持选择 | Phase 3 |
| CSS Grid 替代 Masonry 布局 | 横向排列更符合人类阅读方式，第一行比第二行更新 | Phase 3 |
| 后端排序优于前端排序 | 后端排序性能更好，前端只需渲染数据，保持简单 | Phase 3 |

---

## 3. Phases Delivered

| Phase | Name | Status | One-Liner |
|-------|------|--------|-----------|
| 1 | 数据刷新与排序优化 | ⚠️ Partial | WebSocket 端点修复完成，刷新按钮通过内联 onclick 临时修复 |
| 2 | 提醒框优化 | ✅ Complete | 修复重复弹出、添加去重机制、显示标题信息、调整显示时间 |
| 3 | 数据排序与滚动刷新优化 | ✅ Complete | 验证排序逻辑、实现无限滚动、添加排序选择器 UI |

---

## 4. Requirements Coverage

### Bug 修复

- ✅ **BUG-01**: 修复右上角"刷新"按钮点击无反应问题 — 通过内联 onclick 临时修复
- ✅ **BUG-02**: 修复提醒框一直弹出的问题 — 移除 stats_update 触发
- ✅ **BUG-03**: 修复数据统计一直显示"新增 340 条数据"的问题 — 后端计算增量

### 提醒框优化

- ✅ **NOTIF-01**: 提醒框显示更新的内容标题 — 后端推送 titles 字段
- ✅ **NOTIF-02**: 提醒框维持时间延长 — 验证 5 秒满足 3-5 秒范围
- ✅ **NOTIF-03**: 提醒框去重 — 基于 content hash 的 5 秒窗口去重

### 数据展示优化

- ✅ **DATA-01**: 最新爬取的数据前置显示 — 后端时间降序排列
- ✅ **DATA-02**: 添加卡片排序功能 — 排序选择器 UI + localStorage
- ✅ **DATA-03**: 数据更新时平滑滚动到新数据位置 — 无限滚动 + 增量渲染

---

## 5. Key Decisions Log

| ID | Decision | Phase | Rationale |
|----|----------|-------|-----------|
| D1 | stats_update 仅日志不通知 | 2 | 避免重复通知弹窗 |
| D2 | 5 秒去重窗口 | 2 | 平衡用户体验和去重效果 |
| D3 | titles 最多 2 条 | 2 | 保持通知简洁 |
| D4 | 后端计算增量 | 2 | 避免前端状态管理复杂性 |
| D5 | IntersectionObserver 无限滚动 | 3 | 性能优于 scroll 事件监听 |
| D6 | localStorage 持久化 | 3 | 无需后端存储，跨会话保持 |
| D7 | CSS Grid 横向排列 | 3 | 符合用户阅读习惯 |
| D8 | 热度排序暂不实现 | 3 | 保持迭代节奏，避免范围扩大 |

---

## 6. Tech Debt & Deferred Items

### Known Issues

1. **刷新按钮内联 onclick** — Phase 1 临时修复，应改为正规事件绑定
2. **加载完成动画** — "没有更多数据了" 与旋转动画同时显示，接受为特性
3. **热度排序未实现** — Phase 3 决策，留待后续

### Deferred to Future

- **ENH-01**: 提醒框可点击跳转到对应数据
- **ENH-02**: 支持批量标记已读
- **ENH-03**: 数据更新音效提示（可选）

---

## 7. Getting Started

### Run the Project

```bash
cd MediaCrawler
uv run uvicorn api.main:app --port 8080 --reload
```

### Key Directories

```
MediaCrawler/
├── api/                    # FastAPI 后端
│   ├── main.py             # 应用入口
│   ├── routers/            # API 路由
│   │   ├── notes.py        # 小红书笔记 API
│   │   └── websocket.py    # WebSocket 实时推送
│   └── services/
│       └── file_watcher.py # 文件变更监控
├── viewer/                 # 前端可视化界面
│   └── static/
│       ├── index.html      # 主页面
│       └── js/
│           ├── app.js      # 小红书模块
│           ├── websocket-client.js # WebSocket 客户端
│           └── notifications.js # 实时通知组件
└── data/                   # 数据目录
    └── {platform}/
        ├── jsonl/          # JSONL 格式数据
        └── json/           # JSON 格式数据
```

### Access Points

- **API 文档**: http://localhost:8080/docs
- **数据查看器**: http://localhost:8080/viewer/

### Where to Look First

1. **WebSocket 连接**: `viewer/static/js/websocket-client.js`
2. **通知组件**: `viewer/static/js/notifications.js`
3. **小红书前端**: `viewer/static/js/app.js`
4. **数据 API**: `api/routers/notes.py`

---

## Stats

- **Timeline:** 2026-04-22 → 2026-04-23 (2 days)
- **Phases:** 3 / 3 complete
- **Plans:** 11 total (Phase 2: 4, Phase 3: 3)
- **Requirements:** 9 v1 requirements, all mapped

---

## Files Modified Summary

| Phase | Files Modified |
|-------|----------------|
| Phase 2 | `notifications.js`, `app.js`, `douyin-app.js`, `bilibili-app.js`, `zhihu-app.js`, `websocket.py`, `notes.py`, `crawler.py` |
| Phase 3 | `app.js`, `api.js`, `style.css`, `index.html` |

---

*This summary was generated from milestone artifacts. Ask questions about any section for more details.*
