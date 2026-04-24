# Phase 8: 爬虫集成 - Context

**Gathered:** 2026-04-24
**Status:** Ready for planning

<domain>
## Phase Boundary

将爬虫与图片下载队列集成，实现爬取完成后自动提交图片下载任务。

**Scope:**
- 修改小红书存储层，在保存数据后自动发送图片下载任务
- 使用 fire-and-forget 异步方式，不阻塞爬虫主流程
- 仅处理图片 URL，忽略视频 URL

**Out of Scope:**
- 视频下载（后续 Phase）
- 其他平台（抖音、B站、知乎）- 验证后再扩展
- 修改爬虫核心逻辑

</domain>

<decisions>
## Implementation Decisions

### 集成架构
- **D-01:** 集成点 = 存储层（`store/xhs/__init__.py` 中的 `update_xhs_note` 函数）
  - **Why:** 统一入口，所有存储方式（csv/json/jsonl/db）都受益
  - **How:** 在 `update_xhs_note` 函数末尾添加图片任务入队逻辑

### 异步处理
- **D-02:** 异步方式 = fire-and-forget（`asyncio.create_task`）
  - **Why:** 不阻塞爬虫主流程，即使队列满也不影响数据保存
  - **How:** 使用 `asyncio.create_task(image_queue_service.enqueue(url))`

### 错误处理
- **D-03:** 错误处理 = 记录日志继续执行
  - **Why:** 图片下载是辅助功能，不应影响爬虫主功能
  - **How:** try-except 包裹 enqueue 调用，失败时 `utils.logger.warning`

### 平台范围
- **D-04:** 平台范围 = 仅小红书
  - **Why:** 先验证单平台集成，降低风险
  - **How:** 仅修改 `store/xhs/__init__.py`

### 多图处理
- **D-05:** 多图处理 = 逐个入队
  - **Why:** 每个图片独立入队，并行下载，适合大多数场景
  - **How:** 遍历 `image_list`，逐个调用 enqueue

### 视频处理
- **D-06:** 视频处理 = 忽略
  - **Why:** 本 Phase 仅处理图片，视频下载更复杂
  - **How:** 不处理 `video_url` 字段

### Claude's Discretion
- 具体的代码实现细节（由 planner 和 executor 决定）
- 日志格式和级别
- 是否需要添加配置开关

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 核心服务
- `MediaCrawler/api/services/image_queue.py` — 消息队列服务，enqueue 入口
- `MediaCrawler/api/services/__init__.py` — 服务导出，image_queue_service 单例

### 存储层
- `MediaCrawler/store/xhs/__init__.py` — 小红书存储入口，update_xhs_note 函数
- `MediaCrawler/store/xhs/_store_impl.py` — 存储实现

### 爬虫层（参考）
- `MediaCrawler/media_platform/xhs/core.py` — 小红书爬虫核心
- `MediaCrawler/media_platform/xhs/client.py` — 小红书 API 客户端

### 已完成 Phase 参考
- `.planning/phases/04-renwu-shujuku-yu-xiaoxi-duilie-jichu/04-SUMMARY.md` — 任务队列基础
- `.planning/phases/06-tupian-cunchu-guanli/06-VERIFICATION.md` — 图片存储

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `image_queue_service.enqueue(url, priority)` — 入队入口，已在 `api/services/__init__.py` 导出
- `utils.logger` — 统一日志工具
- `asyncio.create_task` — Python 原生异步任务

### Established Patterns
- 存储层使用工厂模式：`XhsStoreFactory.create_store()`
- 数据保存后无返回值，直接 return
- 日志使用 `utils.logger.info()` 格式

### Integration Points
- **主要修改点:** `store/xhs/__init__.py` → `update_xhs_note()` 函数
- **图片 URL 来源:** `note_item.get("image_list", [])` — 每个 dict 有 `url` 或 `url_default` 字段
- **视频 URL 来源:** `note_item.get("video", {})` — 本 Phase 忽略

### 关键代码片段
```python
# store/xhs/__init__.py update_xhs_note() 中
image_list: List[Dict] = note_item.get("image_list", [])
for img in image_list:
    if img.get('url_default') != '':
        img.update({'url': img.get('url_default')})
# image_list 中每个元素有 'url' 字段
```

</code_context>

<specifics>
## Specific Ideas

- 保持爬虫主流程不受影响，图片下载作为后台辅助功能
- 使用现有的 `image_queue_service` 单例，无需新建服务

</specifics>

<deferred>
## Deferred Ideas

### 后续平台扩展
- 抖音集成 — 待小红书验证后
- B站集成 — 待小红书验证后
- 知乎集成 — 待小红书验证后

### 视频下载
- 视频下载功能 — 需要 Phase 9 或后续版本

</deferred>

---

*Phase: 08-pachong-jicheng*
*Context gathered: 2026-04-24*
