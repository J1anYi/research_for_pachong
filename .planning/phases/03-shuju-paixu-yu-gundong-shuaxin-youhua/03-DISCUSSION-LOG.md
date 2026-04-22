# Phase 3: 数据排序与滚动刷新优化 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-22
**Phase:** 03-数据排序与滚动刷新优化
**Areas discussed:** 排序策略, 滚动加载, 加载指示, 排序UI, 状态持久化, 热度排序

---

## 排序策略

| Option | Description | Selected |
|--------|-------------|----------|
| 后端排序 | 后端已按时间降序排列，只需确保前端正确渲染 | ✓ |
| 前端二次排序 | 前端收到数据后再次排序 | |
| 混合方案 | 前后端同时排序 | |

**User's choice:** 后端排序
**Notes:** 后端 `read_jsonl_files()` 已实现排序，前端无需额外处理

---

## 滚动加载方式

| Option | Description | Selected |
|--------|-------------|----------|
| 无限滚动 | 用户滚动到底部时自动加载下一页 | ✓ |
| 手动加载按钮 | 在列表底部添加"加载更多"按钮 | |
| 预加载方案 | 当用户滚动到 80% 位置时预加载 | |

**User's choice:** 无限滚动
**Notes:** 现代 App 标准做法，用户体验流畅

---

## 滚动阈值

| Option | Description | Selected |
|--------|-------------|----------|
| 200px | 滚动到距离底部 200px 时触发加载 | |
| 100px | 滚动到距离底部 100px 时触发加载 | ✓ |
| 500px | 滚动到距离底部 500px 时触发加载 | |

**User's choice:** 100px
**Notes:** 更接近底部，用户感知更自然

---

## 加载状态指示

| Option | Description | Selected |
|--------|-------------|----------|
| 加载动画 + 文字 | 底部显示旋转动画 + "加载中..." 文字 | ✓ |
| 仅加载动画 | 只显示旋转动画，无文字 | |
| 骨架屏 | 显示骨架屏（卡片占位符） | |

**User's choice:** 加载动画 + 文字
**Notes:** 清晰告知用户正在加载

---

## 排序 UI

| Option | Description | Selected |
|--------|-------------|----------|
| 顶部下拉菜单 | 放在卡片列表上方 | ✓ |
| 侧边筛选面板 | 提供完整选择器 | |
| 暂不添加UI | 先只支持时间排序 | |

**User's choice:** 顶部下拉菜单
**Notes:** 空间占用少，符合常见设计

---

## 排序状态持久化

| Option | Description | Selected |
|--------|-------------|----------|
| 保存到 localStorage | 用户选择后保存，下次访问保持 | ✓ |
| 不保存，每次重置 | 每次刷新后重置为默认排序 | |

**User's choice:** 保存到 localStorage
**Notes:** 记住用户偏好，提升体验

---

## 热度排序

| Option | Description | Selected |
|--------|-------------|----------|
| 计算热度分数 | 基于点赞数、评论数等指标计算热度 | |
| 使用点赞数 | 按点赞数降序排列 | |
| 暂不实现热度 | Phase 3 只实现时间排序 | ✓ |

**User's choice:** 暂不实现热度
**Notes:** 避免范围扩大，热度排序作为后续功能

---

## Claude's Discretion

- 加载动画具体样式（可用 CSS spinner 或 SVG）
- 加载失败时的错误提示文案
- 排序下拉菜单的具体样式和交互细节

## Deferred Ideas

None — discussion stayed within phase scope.
