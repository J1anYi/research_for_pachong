# Phase 3: 数据排序与滚动刷新优化 - Context

**Gathered:** 2026-04-22
**Status:** Ready for planning

<domain>
## Phase Boundary

优化前端数据展示顺序，实现无限滚动加载，添加用户可控的排序选项。

**In scope:**
- 验证并确保最新数据始终显示在列表顶部
- 实现无限滚动加载（用户滚动到底部时自动加载更多）
- 添加排序方式切换 UI（时间排序）
- 记住用户排序偏好

**Out of scope:**
- 热度排序（暂不实现，留待后续）
- 新增爬虫平台
- 后端架构重构

</domain>

<decisions>
## Implementation Decisions

### D-01: 数据排序策略
- **选择：后端排序**
- 后端 `read_jsonl_files()` 已按时间降序排列 (`reverse=True`)
- 前端只需正确渲染返回的数据顺序
- 无需前端二次排序，保持简单

### D-02: 滚动加载方式
- **选择：无限滚动**
- 用户滚动到距离底部 100px 时触发加载
- 每次加载更多数据（使用 `offset` 和 `limit` 参数）
- 无需用户手动点击

### D-03: 加载触发阈值
- **选择：100px**
- 距离底部 100px 时触发加载
- 平衡用户体验和提前加载量

### D-04: 加载状态指示
- **选择：加载动画 + 文字**
- 底部显示旋转动画 + "加载中..." 文字
- 清晰告知用户正在加载

### D-05: 排序 UI 位置
- **选择：顶部下拉菜单**
- 放在卡片列表上方
- 选项：最新（时间降序）
- 空间占用少，符合常见设计

### D-06: 排序状态持久化
- **选择：保存到 localStorage**
- 用户选择的排序方式保存到 localStorage
- 下次访问时保持用户选择
- 默认排序：时间降序

### D-07: 热度排序
- **选择：暂不实现**
- Phase 3 只实现时间排序
- 避免范围扩大
- 热度排序可作为后续功能

### Claude's Discretion
- 加载动画具体样式（可用 CSS spinner 或 SVG）
- 加载失败时的错误提示文案
- 排序下拉菜单的具体样式和交互细节

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Backend API
- `api/routers/notes.py` — 笔记 API，包含 `read_jsonl_files()` 排序逻辑和分页参数 `offset`/`limit`

### Frontend
- `viewer/static/js/app.js` — 小红书前端逻辑，需要添加无限滚动和排序 UI
- `viewer/static/css/style.css` — 样式文件，可能需要添加加载动画样式

### Prior Phase Context
- Phase 2 实现了 WebSocket 推送新数据（包含 `new_count` 和 `titles`）
- Phase 1 实现了刷新后滚动到顶部

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **后端排序**: `notes.sort(key=lambda x: x.get("time") or 0, reverse=True)` 已在 notes.py 实现
- **分页参数**: API 支持 `offset` 和 `limit`，可直接用于无限滚动
- **localStorage**: 已用于其他设置，可复用相同模式

### Established Patterns
- **事件绑定**: 使用 `addEventListener` 而非内联 `onclick`
- **API 调用**: 使用 `fetch()` 获取数据
- **DOM 操作**: 使用 `document.createElement()` 创建卡片

### Integration Points
- 无限滚动需要在 `app.js` 添加滚动事件监听器
- 排序 UI 需要在卡片列表上方插入下拉菜单
- 排序改变时需要重新调用 API 并更新 `offset` 参数

### Known Issues
- 当前没有实现滚动加载 — 数据一次性全部加载
- `time` 字段可能为空或 0，需要 `or 0` 处理

</code_context>

<specifics>
## Specific Ideas

- 无限滚动应在用户滚动到距离底部 100px 时触发
- 加载状态显示：旋转动画 + "加载中..." 文字
- 排序下拉菜单选项：最新（时间降序）
- 排序选择保存到 `localStorage`，key 如 `xhs_sort_order`

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-shuju-paixu-yu-gundong-shuaxin-youhua*
*Context gathered: 2026-04-22*
