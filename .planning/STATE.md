# Project State

**Project:** MediaCrawler 前端体验优化
**Current Phase:** Phase 3 - 数据排序与滚动刷新优化
**Status:** Ready to plan
**Last Updated:** 2026-04-22

---

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-22)

**Core value:** 用户能清晰看到实时更新的数据，操作流畅
**Current focus:** Phase 2 完成，准备进入 Phase 3

---

## Progress

### Completed Phases

**Phase 2: 提醒框优化** ✅ Complete (2026-04-22)

- [x] Plan 01: 移除 stats_update 消息的通知触发
- [x] Plan 02: 添加通知去重机制
- [x] Plan 03: 后端发送新增数据和标题信息
- [x] Plan 04: 验证并调整通知显示时间

### Current Phase

**Phase 3: 数据排序与滚动刷新优化**

- [ ] 验证并修复卡片排序问题（最新数据前置）
- [ ] 修复滚动游标刷新无反应问题
- [ ] 添加排序方式切换UI（按时间/按热度）

### Next Actions

1. 运行 `/gsd-discuss-phase 3` 讨论设计决策
2. 或运行 `/gsd-plan-phase 3` 直接规划

---

## Accumulated Context

### Roadmap Evolution

- Phase 3 added: 数据排序与滚动刷新优化

### Key Decisions

| Decision | Rationale | Phase |
|----------|-----------|-------|
| stats_update 不触发通知 | 每次文件变更触发两个消息导致重复通知，stats_update 仅用于统计展示 | Phase 2 Plan 01 |
| 基于 content hash 的去重机制 | 使用 platform + titles + count 作为哈希键，5 秒时间窗口内跳过重复通知 | Phase 2 Plan 02 |
| titles 显示最多 2 条 | 通知详情显示前 2 条标题，超出显示 "等N条"，保持简洁 | Phase 2 Plan 02 |
| 后端计算增量而非前端 | 后端追踪记录总数变化，计算 new_count = current - previous，避免前端状态管理 | Phase 2 Plan 03 |
| 异步读取最新记录标题 | 使用 aiofiles 异步读取 JSONL/JSON 文件，获取最新记录标题用于通知展示 | Phase 2 Plan 03 |

---

## Context

### What Was Fixed (Previous Phase)

WebSocket 端点配置不匹配问题已修复：
- `/ws/status` 端点现在连接到 `ConnectionManager`
- 数据更新消息现在可以正确推送到前端
- ✅ 验证通过：WebSocket 显示"已连接"，提醒框能弹出

### Validation Results

| 功能 | 状态 | 说明 |
|------|------|------|
| WebSocket 连接 | ✅ 成功 | 显示"已连接" |
| 爬虫状态显示 | ✅ 成功 | 显示"爬虫运行中 (xhs)" |
| 数据推送 | ✅ 成功 | 提醒框有弹出 |
| 刷新按钮 | ✅ 修复 | 通过内联 onclick 临时修复 |
| 提醒框内容 | ✅ 优化 | 支持 titles 显示标题列表 |
| 提醒框频率 | ✅ 修复 | 移除 stats_update 触发，每次只弹一个 |
| 通知去重 | ✅ 完成 | 5 秒窗口内相同内容只显示一次 |
| 新增数量推送 | ✅ 完成 | 后端计算 new_count 并推送 |
| 标题信息推送 | ✅ 完成 | 后端获取最新记录标题推送 |
| 通知显示时间 | ✅ 验证 | 5秒满足3-5秒需求范围 |
| 数据排序 | 🔧 优化 | 最新数据应前置 |
| 滚动刷新 | ❌ Bug | 游标刷新无反应 |

---

## Files Reference

| Type | Location |
|------|----------|
| Project | `.planning/PROJECT.md` |
| Requirements | `.planning/REQUIREMENTS.md` |
| Roadmap | `.planning/ROADMAP.md` |
| Codebase Map | `.planning/codebase/` |
