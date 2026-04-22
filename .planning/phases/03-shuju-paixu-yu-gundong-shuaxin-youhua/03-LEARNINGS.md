---
phase: 3
phase_name: "数据排序与滚动刷新优化"
project: "MediaCrawler 前端体验优化"
generated: "2026-04-22"
counts:
  decisions: 4
  lessons: 4
  patterns: 3
  surprises: 2
missing_artifacts: []
---

# Phase 3 Learnings: 数据排序与滚动刷新优化

## Decisions

### D1: 后端排序优于前端排序
后端已实现时间降序排序，前端直接使用排序结果，无需二次排序。

**Rationale:** 后端排序性能更好，前端只需渲染数据，保持简单。
**Source:** 03-CONTEXT.md D-01

---

### D2: IntersectionObserver 实现无限滚动
使用 IntersectionObserver 监听底部 sentinel 元素，rootMargin 设为 100px 提前触发加载。

**Rationale:** 比监听 scroll 事件性能更好，不会频繁触发重绘。
**Source:** 03-CONTEXT.md D-02, D-03

---

### D3: localStorage 持久化排序偏好
用户选择的排序方式保存到 localStorage，key 为 `xhs_sort_order`。

**Rationale:** 无需后端存储，下次访问自动恢复用户偏好。
**Source:** 03-CONTEXT.md D-06

---

### D4: 热度排序暂不实现
Phase 3 只实现时间排序，热度排序留待后续。

**Rationale:** 避免范围扩大，保持迭代节奏。
**Source:** 03-CONTEXT.md D-07

---

## Lessons

### L1: 自动化验证 ≠ 用户验证
VERIFICATION.md 显示所有检查通过，但 UAT 发现用户无法验证排序正确性（卡片无时间显示）。

**Context:** 代码验证只能检查功能是否实现，无法发现用户体验问题。
**Source:** 03-UAT.md Test 1

---

### L2: finally 块可能覆盖业务逻辑
`loadMoreNotes()` 中 `showNoMoreData()` 被 `finally` 块的 `showLoadingMore(false)` 覆盖。

**Context:** 在 try 块中设置状态，finally 块清空了显示内容，导致用户看不到"没有更多数据"提示。
**Source:** 03-UAT.md Gap 2

---

### L3: 增量渲染需独立函数
无限滚动应使用 `renderMoreNotes()` 增量渲染，而非重新渲染整个列表。

**Context:** 重新渲染整个列表会丢失滚动位置和图片懒加载状态。
**Source:** 03-SUMMARY-02.md

---

### L4: 分页状态重置时机重要
`loadNotes()` 重置 `currentOffset` 和 `hasMoreData`，确保筛选条件改变时从头加载。

**Context:** 如果忘记重置，无限滚动可能加载错误的数据范围。
**Source:** 03-PLAN-02.md Task 5

---

## Patterns

### P1: 无限滚动三件套
1. 状态变量: `currentOffset`, `isLoadingMore`, `hasMoreData`
2. IntersectionObserver 监听 sentinel 元素
3. 加载指示器 + 完成提示

**When to use:** 任何需要分页加载的列表页面。
**Source:** 03-SUMMARY-02.md

---

### P2: localStorage 偏好持久化模式
```javascript
const STORAGE_KEY = 'app_preference_name';
// 读取
const saved = localStorage.getItem(STORAGE_KEY);
if (saved) currentValue = saved;
// 保存
localStorage.setItem(STORAGE_KEY, currentValue);
```

**When to use:** 用户设置、主题偏好、排序选择等需要跨会话保持的状态。
**Source:** 03-SUMMARY-03.md

---

### P3: 验证现有代码再修改
Plan 01 的目标是"验证并修复卡片排序问题"，但验证发现后端排序逻辑已正确，无需修改。

**When to use:** 修复 bug 前先确认问题确实存在，避免不必要的代码改动。
**Source:** 03-SUMMARY-01.md

---

## Surprises

### S1: 后端排序逻辑早已存在
原以为需要添加排序功能，实际 `notes.py` 第 173 行已有 `notes.sort(key=lambda x: x.get("time") or 0, reverse=True)`。

**Impact:** Plan 01 变为纯验证任务，无需修改代码。
**Source:** 03-SUMMARY-01.md

---

### S2: MediaCrawler 是独立 git 仓库
提交代码时发现 MediaCrawler 目录有自己的 `.git`，是独立仓库而非子目录。

**Impact:** 需要分别提交两个仓库的变更，使用 `git -C` 命令操作子仓库。
**Source:** 执行过程

---

## UAT Findings Summary

| Issue | Severity | Root Cause | Fix Needed |
|-------|----------|------------|------------|
| 笔记卡片无时间显示 | minor | `createNoteCard()` 未渲染时间字段 | 添加时间显示 |
| 加载完成提示未显示 | major | `finally` 块覆盖了 `showNoMoreData()` | 修复逻辑顺序 |
