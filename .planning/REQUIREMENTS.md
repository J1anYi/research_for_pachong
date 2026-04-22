# Requirements: MediaCrawler 实时数据推送

**Defined:** 2026-04-22
**Core Value:** 爬虫数据必须实时推送到前端显示

## v1 Requirements

本次修复的核心需求。

### 实时数据推送

- [ ] **REAL-01**: 前端 WebSocket 能正确连接到后端
- [ ] **REAL-02**: 文件变化时后端能检测到并触发推送
- [ ] **REAL-03**: 数据更新消息能正确推送到前端
- [ ] **REAL-04**: 前端能接收并处理 data_update 消息
- [ ] **REAL-05**: 前端能接收并处理 stats_update 消息

### 多平台支持

- [ ] **PLAT-01**: 小红书(xhs)数据更新能推送到前端
- [ ] **PLAT-02**: 抖音(dy)数据更新能推送到前端
- [ ] **PLAT-03**: B站(bili)数据更新能推送到前端
- [ ] **PLAT-04**: 知乎(zhihu)数据更新能推送到前端

### 前端显示

- [ ] **UI-01**: 数据更新时显示通知弹窗
- [ ] **UI-02**: 数据更新时刷新对应平台的数据列表
- [ ] **UI-03**: WebSocket 连接状态指示器正常工作

## v2 Requirements

后续可以改进的功能。

### 增强功能

- **ENH-01**: 订阅管理页面的实时更新
- **ENH-02**: 趋势分析页面的实时更新
- **ENH-03**: 推送消息去重和防抖

## Out of Scope

| Feature | Reason |
|---------|--------|
| 新增爬虫平台 | 本次只修复现有平台的推送功能 |
| 重构前端架构 | 保持现有前端结构 |
| 性能优化 | 先确保功能正确 |
| 移动端适配 | 当前只关注桌面端 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| REAL-01 | Phase 1 | Pending |
| REAL-02 | Phase 1 | Pending |
| REAL-03 | Phase 1 | Pending |
| REAL-04 | Phase 1 | Pending |
| REAL-05 | Phase 1 | Pending |
| PLAT-01 | Phase 1 | Pending |
| PLAT-02 | Phase 1 | Pending |
| PLAT-03 | Phase 1 | Pending |
| PLAT-04 | Phase 1 | Pending |
| UI-01 | Phase 1 | Pending |
| UI-02 | Phase 1 | Pending |
| UI-03 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-22*
*Last updated: 2026-04-22 after initial definition*
