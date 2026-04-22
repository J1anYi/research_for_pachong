# Roadmap: MediaCrawler 前端体验优化

**Created:** 2026-04-22
**Project:** MediaCrawler 前端体验优化
**Phases:** 3
**Requirements:** 12

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
   - 后端已按时间降序排列
   - 验证前端渲染顺序

3. **滚动行为**
   - ✅ 刷新后自动滚动到顶部
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

## Phase 3: 数据排序与滚动刷新优化

**Goal:** 优化卡片排序逻辑，修复滚动游标刷新问题

**Status:** pending

### Requirements

- SORT-01: 验证并修复卡片排序问题（最新数据前置）
- SORT-02: 修复滚动游标刷新无反应问题
- SORT-03: 添加排序方式切换UI（按时间/按热度）

### Success Criteria

1. 最新爬取的数据始终显示在列表顶部
2. 向下滚动时能正确加载更多数据
3. 用户可以切换排序方式
4. 排序状态在刷新后保持

### Technical Approach

1. **卡片排序问题排查**
   - 检查 `read_jsonl_files()` 返回的数据顺序
   - 验证 `time` 字段是否正确解析
   - 在前端渲染前再次排序

2. **滚动刷新问题排查**
   - 检查滚动事件监听器是否正常工作
   - 检查分页参数 `offset` 和 `limit` 是否正确传递
   - 添加加载更多数据的 UI 提示

3. **排序 UI**
   - 添加排序下拉菜单
   - 保存用户排序偏好到 localStorage

### Key Files

- `viewer/static/js/app.js` - 小红书前端逻辑
- `api/routers/notes.py` - 小红书 API
- `viewer/static/css/style.css` - 样式文件

---

## Summary

| Phase | Goal | Requirements | Status |
|-------|------|--------------|--------|
| 1 | 数据刷新与排序优化 | 4 | in_progress |
| 2 | 提醒框优化 | 5 | pending |
| 3 | 数据排序与滚动刷新优化 | 3 | pending |

---
*Last updated: 2026-04-22*
