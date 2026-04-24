# Phase 8: 爬虫集成 - PLAN

---
wave: 1
depends_on: []
files_modified:
  - MediaCrawler/store/xhs/__init__.py
autonomous: false
---

## 阶段目标

将爬虫与图片下载队列集成，实现爬取完成后自动提交图片下载任务。

**需求覆盖:** CRAWL-01, CRAWL-02

---

## Task 1: 在存储层集成图片入队逻辑

<read_first>
- `MediaCrawler/store/xhs/__init__.py` — 需要修改的文件，包含 `update_xhs_note` 函数
- `MediaCrawler/api/services/__init__.py` — 服务导出入口，提供 `image_queue_service` 单例
- `MediaCrawler/api/services/image_queue.py` — 消息队列服务，提供 `enqueue` 方法
</read_first>

<acceptance_criteria>
- `MediaCrawler/store/xhs/__init__.py` 文件中存在 `from api.services import image_queue_service` 导入语句
- `MediaCrawler/store/xhs/__init__.py` 文件中存在 `import asyncio` 导入语句
- `update_xhs_note` 函数中存在调用 `image_queue_service.enqueue` 的代码
- `update_xhs_note` 函数中存在 try-except 包裹 enqueue 调用的错误处理代码
- 日志包含 `[store.xhs.update_xhs_note]` 前缀
</acceptance_criteria>

<action>
在 `MediaCrawler/store/xhs/__init__.py` 文件的 `update_xhs_note` 函数末尾（第 132 行 `await XhsStoreFactory.create_store().store_content(local_db_item)` 之后）添加以下代码：

```python
    # 图片下载任务入队 (fire-and-forget)
    try:
        from api.services import image_queue_service
        for img in image_list:
            url = img.get("url")
            if url:
                # Fire-and-forget: 不等待结果，不阻塞主流程
                asyncio.create_task(image_queue_service.enqueue(url))
    except Exception as e:
        utils.logger.warning(f"[store.xhs.update_xhs_note] Failed to enqueue image download task: {e}")
```

同时在文件顶部添加 `import asyncio` 导入（如果尚未存在）。
</action>

---

## 验证标准

### 代码验证

1. **导入检查**
   ```bash
   grep -n "import asyncio" MediaCrawler/store/xhs/__init__.py
   # 期望: 找到 import asyncio 导入语句
   ```

2. **服务导入检查**
   ```bash
   grep -n "from api.services import image_queue_service" MediaCrawler/store/xhs/__init__.py
   # 期望: 找到服务导入语句
   ```

3. **入队逻辑检查**
   ```bash
   grep -n "image_queue_service.enqueue" MediaCrawler/store/xhs/__init__.py
   # 期望: 找到 enqueue 调用
   ```

4. **错误处理检查**
   ```bash
   grep -n "Failed to enqueue image download task" MediaCrawler/store/xhs/__init__.py
   # 期望: 找到错误日志语句
   ```

### 功能验证

1. **手动测试**
   - 启动 API 服务: `cd MediaCrawler && uv run uvicorn api.main:app --port 8080`
   - 运行小红书爬虫，爬取 1-2 条笔记
   - 检查日志是否包含 `[ImageQueue] Enqueued:` 输出
   - 检查 `data/images/` 目录是否有图片下载

2. **队列状态检查**
   - 访问 `http://localhost:8080/api/image-queue/stats`
   - 确认队列正在处理任务

---

## must_haves

从阶段目标派生的必须达成条件：

1. **集成完成** — `store/xhs/__init__.py` 中 `update_xhs_note` 函数调用 `image_queue_service.enqueue`
2. **不阻塞主流程** — 使用 `asyncio.create_task` 实现 fire-and-forget 模式
3. **错误隔离** — enqueue 失败不影响数据存储主流程
4. **日志可追踪** — 失败时记录带 `[store.xhs.update_xhs_note]` 前缀的警告日志

---

## 风险与缓解

| 风险 | 级别 | 缓解措施 |
|------|------|----------|
| 队列满时丢任务 | MEDIUM | `enqueue` 已有去重逻辑，队列满时 `put_nowait` 抛异常，被 try-except 捕获 |
| 服务未启动 | LOW | API 启动时自动启动 `image_queue_service`，爬虫调用时服务已就绪 |
| asyncio.create_task 异常 | LOW | `enqueue` 内部有 try-except，异常不会传播 |

---

## 配置依赖

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `ENABLE_GET_MEIDAS` | False | 已禁用爬虫原生媒体下载，避免重复下载 |

---

## 后续扩展

本 Phase 仅处理小红书平台。验证成功后可扩展至：

- 抖音: `store/douyin/__init__.py`
- B站: `store/bilibili/__init__.py`
- 知乎: `store/zhihu/__init__.py`

---

*Plan created: 2026-04-24*
