# Phase 6: 图片存储管理 - Research

**Researched:** 2026-04-23
**Domain:** 图片存储、去重、格式验证、存储空间管理
**Confidence:** HIGH

## Summary

Phase 6 实现可靠的图片存储和去重机制。需要在现有 image_downloader.py 基础上增加图片存储服务（image_storage.py），支持按平台/日期组织目录结构、下载前检查已完成任务避免重复下载、使用 PIL 验证图片格式、存储空间超限时自动清理最旧图片。

**Primary recommendation:** 创建 image_storage.py 服务，统一管理图片存储路径、去重检查、格式验证和存储空间清理，修改 image_downloader.py 集成这些功能。

## Standard Stack

| Library | Version | Purpose |
|---------|---------|---------|
| Pillow (PIL) | 11.x | 图片验证和处理 |
| hashlib | 内置 | URL hash 计算 |

**Installation:** pip install Pillow

## Architecture Patterns

### Pattern 1: URL Hash 文件名生成
使用 MD5(url)[:16] 作为文件名，避免特殊字符问题。

### Pattern 2: 图片格式验证
使用 PIL.Image.open() 验证图片 + 检测 magic bytes。

### Pattern 3: LRU 存储空间清理
按文件修改时间排序，删除最旧的文件直到空间低于阈值。

## Common Pitfalls

### Pitfall 1: 未验证下载的内容是图片
- 网站返回 HTML 错误页面，保存为 .jpg 但实际是 HTML
- 解决: 下载后立即用 PIL 验证图片格式

### Pitfall 2: 重复下载检查不完整
- 去重检查只查 pending 任务，已完成的 URL 没有返回本地路径
- 解决: 添加 get_completed_task(url) 方法

### Pitfall 3: 存储空间计算不准确
- 解决: 边删除边计算剩余大小

## Code Examples

### image_task_db.py 扩展
async def get_completed_task(self, url: str) -> Optional[ImageTask]:
    async with aiosqlite.connect(self._db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT * FROM image_tasks WHERE url = ? AND status = ?',
            (url, TaskStatus.COMPLETED.value))
        row = await cursor.fetchone()
        return self._row_to_task(row) if row else None

### image_storage.py 新建
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image

class ImageStorageService:
    def __init__(self, data_dir: Path, platform: str):
        self._base_dir = data_dir / platform / 'images'
    
    def get_storage_path(self, url: str, ext: str = '.jpg') -> Tuple[Path, str]:
        url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
        now = datetime.now()
        date_dir = self._base_dir / str(now.year) / f'{now.month:02d}' / f'{now.day:02d}'
        date_dir.mkdir(parents=True, exist_ok=True)
        filename = f'{url_hash}{ext}'
        return date_dir / filename, url_hash
    
    def validate_and_get_ext(self, file_path: Path) -> Optional[str]:
        try:
            with Image.open(file_path) as img:
                img.verify()
            with open(file_path, 'rb') as f:
                header = f.read(8)
            if header[:3] == b'ÿØÿ':
                return '.jpg'
            elif header[:4] == b'PNG':
                return '.png'
            return None
        except Exception:
            return None
    
    def cleanup_by_size(self, max_size_bytes: int) -> int:
        if not self._base_dir.exists():
            return 0
        files = []
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            files.extend(self._base_dir.rglob(f'*{ext}'))
        if not files:
            return 0
        files.sort(key=lambda f: f.stat().st_mtime)
        current_size = sum(f.stat().st_size for f in files)
        deleted = 0
        for file in files:
            if current_size <= max_size_bytes:
                break
            file_size = file.stat().st_size
            file.unlink()
            current_size -= file_size
            deleted += 1
        return deleted

## Open Questions

1. 存储空间阈值默认值? - 建议默认 5GB
2. 多平台目录结构? - 保持简单，按 year/month/day 即可

## Environment Availability

| Dependency | Available | Version |
|------------|-----------|---------|
| Python 3.10+ | YES | 3.12.x |
| Pillow | YES | 11.x |

## Validation Architecture

| Req ID | Behavior |
|--------|----------|
| IMG-01 | 路径生成正确 |
| IMG-02 | 去重检查返回本地路径 |
| IMG-03 | 无效图片被检测删除 |
| IMG-04 | 超空间自动清理 |

**Research date:** 2026-04-23
