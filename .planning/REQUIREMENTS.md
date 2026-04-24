# Requirements: MediaCrawler 多图轮播、视频下载与UI优化

**Defined:** 2026-04-24
**Core Value:** 图片可靠存储在本地,前端能正常显示图片

## v3.0 Requirements

### 多图轮播显示

- [ ] **CAROUSEL-01**: 小红书卡片支持显示多张图片
- [ ] **CAROUSEL-02**: 图片下方显示圆点指示器（代表图片数量）
- [ ] **CAROUSEL-03**: 点击圆点可切换到对应图片
- [ ] **CAROUSEL-04**: 自动轮播功能，间隔3秒
- [ ] **CAROUSEL-05**: 点击卡片时重置轮播计时器
- [ ] **CAROUSEL-06**: 后端API返回多图URL列表

### UI优化

- [ ] **UI-01**: 清新简约风格设计系统建立
- [ ] **UI-02**: 统一配色方案（浅色系为主）
- [ ] **UI-03**: 优化卡片布局和间距
- [ ] **UI-04**: 优化字体层级和排版
- [ ] **UI-05**: 优化按钮和交互元素样式
- [ ] **UI-06**: 优化模态框样式
- [ ] **UI-07**: 优化加载状态和过渡动画
- [ ] **UI-08**: 响应式布局优化

### 视频下载功能

- [ ] **VIDEO-01**: B站视频卡片显示下载按钮
- [ ] **VIDEO-02**: 点击按钮手动触发视频下载
- [ ] **VIDEO-03**: 视频文件大小检测（阈值50MB）
- [ ] **VIDEO-04**: 大视频（>50MB）支持分片下载
- [ ] **VIDEO-05**: 断点续传功能，支持中断后继续下载
- [ ] **VIDEO-06**: 下载进度显示
- [ ] **VIDEO-07**: 下载状态管理（pending, downloading, completed, failed）
- [ ] **VIDEO-08**: 视频存储路径规划
- [ ] **VIDEO-09**: 下载失败重试机制
- [ ] **VIDEO-10**: 复用现有任务队列架构

## Out of Scope

| Feature | Reason |
|---------|--------|
| 视频自动下载 | 用户明确要求手动触发 |
| 其他平台视频下载 | 当前仅支持B站 |
| 多平台多图轮播 | 当前仅支持小红书 |
| 分布式任务队列 | 单进程 asyncio.Queue 足够 |
| 视频转码/压缩 | 超出当前里程碑范围 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CAROUSEL-01 | Phase 9 | Pending |
| CAROUSEL-02 | Phase 9 | Pending |
| CAROUSEL-03 | Phase 9 | Pending |
| CAROUSEL-04 | Phase 9 | Pending |
| CAROUSEL-05 | Phase 9 | Pending |
| CAROUSEL-06 | Phase 9 | Pending |
| UI-01 | Phase 10 | Pending |
| UI-02 | Phase 10 | Pending |
| UI-03 | Phase 10 | Pending |
| UI-04 | Phase 10 | Pending |
| UI-05 | Phase 10 | Pending |
| UI-06 | Phase 10 | Pending |
| UI-07 | Phase 10 | Pending |
| UI-08 | Phase 10 | Pending |
| VIDEO-01 | Phase 11 | Pending |
| VIDEO-02 | Phase 11 | Pending |
| VIDEO-03 | Phase 11 | Pending |
| VIDEO-04 | Phase 11 | Pending |
| VIDEO-05 | Phase 11 | Pending |
| VIDEO-06 | Phase 11 | Pending |
| VIDEO-07 | Phase 11 | Pending |
| VIDEO-08 | Phase 11 | Pending |
| VIDEO-09 | Phase 11 | Pending |
| VIDEO-10 | Phase 11 | Pending |

**Coverage:**
- v3.0 requirements: 24 total
- Mapped to phases: 24
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-24*
