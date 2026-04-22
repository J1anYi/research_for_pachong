# Roadmap: MediaCrawler 实时数据推送修复

**Created:** 2026-04-22
**Project:** MediaCrawler 实时数据推送修复
**Phases:** 1
**Requirements:** 12

---

## Phase 1: 验证并完善实时数据推送

**Goal:** 验证 WebSocket 推送功能完整可用，确保所有平台都能正常推送数据到前端

**Status:** pending

### Requirements

- REAL-01: 前端 WebSocket 能正确连接到后端
- REAL-02: 文件变化时后端能检测到并触发推送
- REAL-03: 数据更新消息能正确推送到前端
- REAL-04: 前端能接收并处理 data_update 消息
- REAL-05: 前端能接收并处理 stats_update 消息
- PLAT-01: 小红书(xhs)数据更新能推送到前端
- PLAT-02: 抖音(dy)数据更新能推送到前端
- PLAT-03: B站(bili)数据更新能推送到前端
- PLAT-04: 知乎(zhihu)数据更新能推送到前端
- UI-01: 数据更新时显示通知弹窗
- UI-02: 数据更新时刷新对应平台的数据列表
- UI-03: WebSocket 连接状态指示器正常工作

### Success Criteria

1. 启动服务后，前端 WebSocket 连接状态显示"已连接"
2. 当爬虫写入数据到文件时，前端在 1 秒内收到更新通知
3. 所有4个平台（小红书、抖音、B站、知乎）的数据更新都能正确推送到前端
4. 数据更新时前端显示通知弹窗，内容正确
5. 数据列表自动刷新显示新数据

### Technical Approach

1. **验证 WebSocket 连接**
   - 启动后端服务
   - 打开前端页面
   - 检查浏览器控制台 WebSocket 连接日志
   - 确认连接状态指示器显示"已连接"

2. **验证文件监控**
   - 手动修改 JSONL 文件
   - 检查后端日志是否显示 `[FileWatcher]` 和 `[WS]` 日志
   - 确认消息被广播

3. **验证前端接收**
   - 检查浏览器控制台是否显示 `[WS] Data update for platform: xhs` 等日志
   - 确认通知弹窗显示
   - 确认数据列表刷新

4. **多平台测试**
   - 分别测试小红书、抖音、B站、知乎
   - 确认每个平台都能正常推送

### Key Files

- `api/routers/websocket.py` - WebSocket 端点
- `api/services/file_watcher.py` - 文件监控服务
- `viewer/static/js/websocket-client.js` - 前端 WebSocket 客户端
- `viewer/static/js/app.js` - 小红书前端逻辑
- `viewer/static/js/douyin-app.js` - 抖音前端逻辑
- `viewer/static/js/bilibili-app.js` - B站前端逻辑
- `viewer/static/js/zhihu-app.js` - 知乎前端逻辑

---

## Summary

| Phase | Goal | Requirements | Status |
|-------|------|--------------|--------|
| 1 | 验证并完善实时数据推送 | 12 | pending |

---
*Last updated: 2026-04-22*
