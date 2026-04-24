---
phase: 3
phase_name: "数据排序与滚动刷新优化"
project: "MediaCrawler 前端体验优化"
generated: "2026-04-23"
counts:
  decisions: 5
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
**Source:** 03-PLAN-01.md, 03-SUMMARY-01.md

---

### D2: IntersectionObserver 实现无限滚动
使用 IntersectionObserver 监听底部 sentinel 元素，rootMargin 设为 100px 提前触发加载。

**Rationale:** 比监听 scroll 事件性能更好，不会频繁触发重绘。
**Source:** 03-PLAN-02.md, 03-SUMMARY-02.md

---

### D3: localStorage 持久化排序偏好
用户选择的排序方式保存到 localStorage，key 为 `xhs_sort_order`。

**Rationale:** 无需后端存储，下次访问自动恢复用户偏好。
**Source:** 03-PLAN-03.md, 03-SUMMARY-03.md

---

### D4: 热度排序暂不实现
Phase 3 只实现时间排序，热度排序留待后续。

**Rationale:** 避免范围扩大，保持迭代节奏。
**Source:** 03-PLAN-03.md

---

### D5: CSS Grid 替代 Masonry 布局
用户反馈 masonry 纵向排列不符合阅读习惯，改为 CSS Grid 横向排列。

**Rationale:** 横向排列更符合人类阅读方式，第一行比第二行更新，每行内从左到右时间递减。
**Source:** 03-UAT.md

---

## Lessons

### L1: 自动化验证 ≠ 用户验证
VERIFICATION.md 显示所有检查通过，但 UAT 发现用户无法验证排序正确性（卡片无时间显示）。

**Context:** 代码验证只能检查功能是否实现，无法发现用户体验问题。
**Source:** 03-UAT.md Test 1

---

### L2: CSS 多列布局的特殊行为
Masonry 布局（column-count）纵向排列数据，与用户期望的横向阅读习惯不符。

**Context:** 用户期望第一张卡片比第二张早，换行的全部卡片比第一行的要晚。Masonry 布局按列填充，视觉顺序与数据顺序不一致。
**Source:** 03-UAT.md

---

### L3: 时间戳格式需自动检测
API 返回毫秒级时间戳（13位），代码中 `timestamp * 1000` 会导致错误日期。

**Context:** 后端返回毫秒级时间戳，前端格式化时需要判断位数自动处理。
**Source:** 执行过程

---

### L4: IntersectionObserver 需要在"没有更多数据"时停止监听
即使调用了 `unobserve()`，如果 sentinel 元素被复用或重新创建，observer 可能再次触发。

**Context:** 在 sentinel 上添加 `data-no-more="true"` 标记，observer 回调中检查该标记可防止重复触发。
**Source:** 执行过程

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

### S2: 布局方式影响用户对排序的理解
Masonry 布局的纵向排列让用户误以为排序不正确，实际数据已正确排序，只是视觉呈现方式与用户期望不符。

**Impact:** 需要修改布局为 CSS Grid 横向排列，符合用户阅读习惯。
**Source:** 03-UAT.md

---

## UAT Findings Summary

| Issue | Severity | Root Cause | Resolution |
|-------|----------|------------|------------|
| 笔记卡片无时间显示 | minor | `createNoteCard()` 未渲染时间字段 | 添加时间显示组件 |
| 加载完成提示与动画同时显示 | cosmetic | sentinel 元素状态管理 | 接受为特性 |
| 布局不符合阅读习惯 | minor | Masonry 纵向排列 | 改为 CSS Grid 横向排列 |
