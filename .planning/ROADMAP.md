# Roadmap: MediaCrawler

**Last Updated:** 2026-04-24

---

## Current Milestone: v3.0 多图轮播、视频下载与UI优化

**Goal:** 实现小红书多图轮播、B站视频下载（支持大视频分片和断点续传）、UI清新简约风格优化

### Phase 9: 小红书多图轮播显示

**Goal:** 实现小红书卡片多图片显示和轮播交互

**Requirements:** CAROUSEL-01, CAROUSEL-02, CAROUSEL-03, CAROUSEL-04, CAROUSEL-05, CAROUSEL-06

**Success Criteria:**
1. 用户点击小红书卡片能看到所有图片
2. 图片下方显示圆点指示器，点击可切换
3. 自动轮播每3秒切换一次
4. 点击卡片后轮播计时器重置

**Approach:**
- 后端: 修改 notes API 返回多图 URL 列表
- 前端: 实现图片轮播组件（圆点指示器 + 自动轮播 + 计时器重置）
- 样式: 轮播动画和过渡效果

---

### Phase 10: UI清新简约风格优化

**Goal:** 全面优化UI，建立清新简约的设计风格

**Requirements:** UI-01, UI-02, UI-03, UI-04, UI-05, UI-06, UI-07, UI-08

**Success Criteria:**
1. 整体风格清新简约，留白充足
2. 配色统一协调（浅色系为主）
3. 卡片布局美观舒适
4. 交互流畅自然

**Approach:**
- 使用 /design-consultation skill 建立设计系统
- 定义配色方案和字体层级
- 重构 CSS 样式，统一视觉语言
- 优化各平台卡片样式
- 优化模态框、按钮、加载状态

**Design Direction:**
- 风格: 清新简约
- 配色: 浅色系为主，柔和的强调色
- 留白: 充足的间距和呼吸感
- 字体: 清晰易读，层级分明

---

### Phase 11: B站视频下载功能

**Goal:** 实现B站视频手动下载，支持大视频分片和断点续传

**Requirements:** VIDEO-01, VIDEO-02, VIDEO-03, VIDEO-04, VIDEO-05, VIDEO-06, VIDEO-07, VIDEO-08, VIDEO-09, VIDEO-10

**Success Criteria:**
1. B站视频卡片显示下载按钮
2. 点击按钮开始下载，显示进度
3. 大视频（>50MB）自动分片下载
4. 中断后可继续下载（断点续传）
5. 下载失败自动重试

**Approach:**
- 后端: 创建视频任务数据库表，复用任务队列架构
- 后端: 实现分片下载和断点续传逻辑（使用 yt-dlp）
- 后端: 视频大小检测和分片策略
- 前端: 下载按钮、进度显示、状态管理

**Technical Notes:**
- 复用 v2.0 的 image_task_db.py 架构创建 video_task_db.py
- 使用 yt-dlp 进行视频下载
- 分片大小建议: 10MB per chunk
- 断点续传: 记录已下载字节范围

---

## Completed Milestones

### [v2.0: 图片本地存储与任务队列](./milestones/v2.0-ROADMAP.md) ✅ Complete (2026-04-24)

**Summary:** 实现图片本地存储,通过任务队列机制解决限流和鉴权问题。包含任务数据库、消息队列、定时调度、存储管理、前端优化和爬虫集成,共 5 个 Phase,20 个需求全部完成。

### [v1.0: 前端体验优化](./milestones/v1.0-ROADMAP.md) ✅ Complete (2026-04-22)

**Summary:** 修复 WebSocket 实时推送、提醒框优化、数据排序和无限滚动加载,共 3 个 Phase,9 个需求全部完成。

---

## Summary

| Phase | Goal | Requirements | Status |
|-------|------|--------------|--------|
| Phase 9 | 小红书多图轮播显示 | 6 | ○ Pending |
| Phase 10 | UI清新简约风格优化 | 8 | ○ Pending |
| Phase 11 | B站视频下载功能 | 10 | ○ Pending |

**Total:** 3 phases, 24 requirements

---
*Roadmap created: 2026-04-24*
