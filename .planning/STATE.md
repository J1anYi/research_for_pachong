# Project State

**Project:** MediaCrawler 前端体验优化
**Current Phase:** Phase 2 - 提醒框优化
**Status:** In Progress - Plan 04 completed
**Last Updated:** 2026-04-22

---

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-22)

**Core value:** 用户能清晰看到实时更新的数据，操作流畅
**Current focus:** 实现通知去重机制

---

## Progress

### Completed Phases

**Phase 2 - Plan 01: 移除 stats_update 消息的通知触发**
- [x] 移除 app.js 中 stats_update 的通知触发
- [x] 移除 douyin-app.js 中 stats_update 的通知触发
- [x] 移除 bilibili-app.js 中 stats_update 的通知触发
- [x] 移除 zhihu-app.js 中 stats_update 的通知触发

**Phase 2 - Plan 02: 添加通知去重机制**
- [x] 添加 NOTIFICATION_DEDUP 数据结构
- [x] 创建 generateNotificationHash 函数
- [x] 创建 isDuplicateNotification 函数
- [x] 在 showDataNotification 中应用去重逻辑
- [x] 支持 titles 参数显示标题列表

**Phase 2 - Plan 03: 后端发送新增数据和标题信息**
- [x] 扩展 DataUpdateMessage schema 添加 new_count 和 titles 字段
- [x] 添加平台记录计数追踪功能
- [x] 添加获取最新记录和计数的辅助函数
- [x] 修改 broadcast_platform_update 包含新记录信息

**Phase 2 - Plan 04: 验证并调整通知显示时间**
- [x] 验证 autoCloseTimeout 配置为 5000ms
- [x] 确认进度条动画时间 5s 与超时时间同步
- [x] 确认鼠标悬停暂停功能正常

### Current Phase

**Phase 1: 数据刷新与排序优化**

- [x] 添加内联 onclick 作为刷新按钮临时修复
- [x] 刷新后自动滚动到顶部
- [ ] 清理内联 onclick，改用正规事件绑定
- [ ] 验证数据排序是否正确

### Next Actions

1. 所有 Phase 2 计划已完成
2. 检查是否有更多计划需要执行
3. 标记 Phase 2 为完成状态

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
