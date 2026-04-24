---
phase: 08-pachong-jicheng
created: 2026-04-24
---

# Phase 8: 爬虫集成 - LEARNINGS

## 关键决策

### 1. Fire-and-Forget 模式
**决策**: 使用 `asyncio.create_task()` 实现图片入队，不阻塞爬虫主流程

**原因**:
- 图片下载是后台任务，不应影响爬虫性能
- 失败时只记录警告日志，不影响数据存储

**代码模式**:
```python
try:
    from api.services import image_queue_service
    for img in image_list:
        url = img.get("url")
        if url:
            asyncio.create_task(image_queue_service.enqueue(url))
except Exception as e:
    utils.logger.warning(f"Failed to enqueue: {e}")
```

### 2. 存储路径设计
**决策**: 使用 URL hash 作为文件名，按日期分目录

**路径格式**: `{data_dir}/{platform}/images/{year}/{month}/{day}/{url_hash}.webp`

**原因**:
- URL hash 实现自动去重
- 日期目录便于管理和清理
- 与旧存储格式 (note_id-based) 兼容

---

## 遇到的问题

### 问题 1: image_list 数据格式不匹配

**现象**: API 返回 `local_image_url: null`，前端无法显示图片

**根因**: 
- 数据中 `image_list` 是**逗号分隔的字符串**
- 代码期望是**数组**
- `image_list[0]` 返回字符串第一个字符 `"h"`，而不是第一个 URL

**修复**:
```python
# 修复前（错误）
image_list = note.get("image_list", [])
first_remote_url = image_list[0] if image_list else ""

# 修复后（正确）
image_list_raw = note.get("image_list", "")
if isinstance(image_list_raw, str):
    image_list = [url.strip() for url in image_list_raw.split(",") if url.strip()]
else:
    image_list = image_list_raw if image_list_raw else []
first_remote_url = image_list[0] if image_list else ""
```

**教训**: 永远不要假设数据格式，要检查实际类型并做兼容处理

---

### 问题 2: 服务器热重载失败

**现象**: 修改代码后 API 仍返回旧数据

**根因**: 
- uvicorn `--reload` 没有正确触发重载
- 旧服务器进程一直运行
- 端口冲突导致新服务器无法启动

**解决方法**:
1. 完全终止旧进程: `taskkill /F /IM python.exe`
2. 清除 Python 缓存: `find . -name "*.pyc" -delete`
3. 重新启动服务器

**教训**: 关键代码修改后应完全重启服务器，不要依赖热重载

---

### 问题 3: 端口冲突

**现象**: 8080 端口被多个进程占用，无法启动新服务器

**根因**: 
- 多个 uvicorn reload 子进程残留
- Windows 上杀进程权限问题

**解决方法**:
1. 使用 `netstat -ano | findstr :8080` 找到占用进程
2. 用 PowerShell `Stop-Process -Id PID -Force` 强制终止
3. 或更换端口（本次改为 8081）

**教训**: 使用专用端口避免冲突，项目中默认端口改为 8081

---

## 调试技巧

### 1. 直接测试函数 vs API 测试
- 直接用 Python 测试函数更可靠（排除服务器缓存问题）
- API 测试可能受热重载失败影响

```bash
# 直接测试函数
uv run python -c "from api.routers.notes import format_note_for_response; ..."

# API 测试
curl -s "http://localhost:8081/api/notes?limit=1"
```

### 2. 检查数据格式
```python
# 检查实际数据类型
image_list = note.get("image_list")
print(f"type: {type(image_list)}, value: {image_list[:100]}")
```

### 3. 验证图片下载
```bash
# 检查本地图片
ls -la data/xhs/images/2026/04/24/

# 检查队列状态
curl -s http://localhost:8081/api/image-queue/stats
```

---

## 配置变更

| 配置项 | 原值 | 新值 | 原因 |
|--------|------|------|------|
| 默认端口 | 8080 | 8081 | 避免端口冲突 |

---

## 后续改进建议

1. **数据格式统一**: 修改爬虫存储逻辑，将 `image_list` 存为数组格式
2. **健康检查**: 添加 API 端点返回代码版本，便于确认服务器加载了新代码
3. **端口配置**: 支持环境变量配置端口，而非硬编码

---

*Learnings extracted: 2026-04-24*
