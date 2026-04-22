# Roadmap: MediaCrawler 前端体验优化

**Created:** 2026-04-22
**Project:** MediaCrawler 前端体验优化
**Phases:** 2
**Requirements:** 9

---

## Phase 1: 数据刷新与排序优化

**Goal:** 修复刷新功能，优化数据展示顺序，让用户能看到最新数据

**Status:** in_progress

### Requirements

- BUG-01: 修复右上角"刷新"按钮点击无反应问题 ✅ (已通过内联onclick临时修复)
- DATA-01: 最新爬取的数据前置显示
- DATA-02: 添加卡片排序功能（按时间排序）
- DATA-03: 数据更新时平滑滚动到新数据位置

### Success Criteria

1. 点击刷新按钮后数据列表重新加载并显示
2. 新数据出现在列表顶部
3. 用户可以选择排序方式（时间升序/降序）
4. 刷新后自动滚动到顶部

### Technical Approach

1. **修复刷新按钮**
   - ✅ 已添加内联 onclick 作为临时方案
   - 需要清理为正规事件绑定

2. **数据排序**
   - 修改 API 返回数据时按时间降序排列
   - 或在前端渲染前排序

3. **滚动行为**
   - 刷新后自动滚动到顶部
   - 使用 `scrollIntoView({ behavior: 'smooth' })`

### Key Files

- `viewer/static/js/app.js` - 小红书前端逻辑
- `api/routers/notes.py` - 小红书 API

---

## Phase 2: 提醒框优化

**Goal:** 修复提醒框重复弹出和内容显示问题

**Status:** pending

### Requirements

- BUG-02: 修复提醒框一直弹出的问题
- BUG-03: 修复数据统计一直显示"新增 340 条数据"的问题
- NOTIF-01: 提醒框显示更新的内容标题
- NOTIF-02: 提醒框维持时间延长
- NOTIF-03: 提醒框去重

### Success Criteria

1. 提醒框只在有新数据时弹出一次
2. 提醒框显示具体更新的内容（如笔记标题）
3. 提醒框维持 3-5 秒后自动消失
4. 相同内容不重复弹出

### Technical Approach

1. **修复重复弹出**
   - 检查 `broadcast_stats_update()` 是否被重复调用
   - 添加消息去重机制（基于时间戳或内容hash）

2. **优化提醒内容**
   - 读取最新的数据记录
   - 提取标题或关键字段显示

3. **延长显示时间**
   - 修改 `notifications.js` 中的 `autoClose` 时间

---

## Summary

| Phase | Goal | Requirements | Status |
|-------|------|--------------|--------|
| 1 | 数据刷新与排序优化 | 4 | in_progress |
| 2 | 提醒框优化 | 5 | pending |

---
*Last updated: 2026-04-22*
