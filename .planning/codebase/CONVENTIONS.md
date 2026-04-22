# 编码规范文档

本文档记录 MediaCrawler 项目的代码风格约定、文件组织方式和开发规范。

## 1. 文件头部规范

### Python 文件头部

所有 Python 文件必须包含以下版权声明和许可信息：

```python
# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/{相对路径}
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#
# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。
```

### 文件头部管理

项目使用自动化工具管理文件头部：

- **工具**: `tools/file_header_manager.py`
- **配置**: `.pre-commit-config.yaml` 中的 `check-file-headers` 和 `add-file-headers` hooks
- **功能**: 自动检查和添加版权声明

## 2. Python 代码风格

### 缩进与格式

- **缩进**: 4 空格缩进
- **编码**: UTF-8，文件头部声明 `# -*- coding: utf-8 -*-`
- **最大行宽**: 遵循 PEP 8 建议（约 79-100 字符）

### 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| 类名 | PascalCase | `XhsStoreFactory`, `ExcelStoreBase` |
| 函数/方法 | snake_case | `store_content()`, `get_instance()` |
| 变量 | snake_case | `content_item`, `note_id` |
| 常量 | UPPER_SNAKE_CASE | `DATA_DIR`, `NOTE_ID_PATTERN` |
| 私有方法 | _leading_underscore | `_write_headers()`, `_apply_header_style()` |
| 模块级私有 | 双下划线前缀或单下划线 | `_store_impl.py` |

### 类型注解

**必须使用类型注解**，特别是函数返回类型：

```python
def validate_note_id(note_id: str) -> bool:
    """Validate note_id to prevent path traversal attacks."""
    if not note_id or len(note_id) > 64:
        return False
    return bool(NOTE_ID_PATTERN.match(note_id))

async def store_content(self, content_item: Dict) -> None:
    """Store content data to Excel"""
    ...

def get_all_content(self) -> List[Dict]:
    """Get all content from database"""
    ...
```

### 导入顺序

```python
# 1. 标准库
import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 2. 第三方库
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

# 3. 本地模块
from base.base_crawler import AbstractStore
from database.db_session import get_session
from tools import utils
```

### 文档字符串 (Docstrings)

使用三引号文档字符串，支持 Google 风格：

```python
def get_instance(cls, platform: str, crawler_type: str) -> "ExcelStoreBase":
    """
    Get or create a singleton instance for the given platform and crawler type

    Args:
        platform: Platform name (xhs, dy, ks, etc.)
        crawler_type: Type of crawler (search, detail, creator)

    Returns:
        ExcelStoreBase instance
    """
    ...

async def store_content(self, content_item: Dict):
    """
    Store content data to Excel

    Args:
        content_item: Content data dictionary
    """
    ...
```

简单函数可以使用单行文档：

```python
def flush(self):
    """Save workbook to file"""
    ...
```

## 3. JavaScript 代码风格

### 缩进与格式

- **缩进**: 2 空格缩进
- **模块模式**: 使用 IIFE (立即执行函数表达式) 封装

```javascript
(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        wsEndpoint: '/api/ws/status',
        maxReconnectAttempts: 10
    };

    // ... 代码逻辑

    // 导出 API
    window.WSClient = {
        connect,
        disconnect,
        subscribe
    };
})();
```

### 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| 变量 | camelCase | `allNotes`, `currentKeyword` |
| 函数 | camelCase | `loadNotes()`, `renderNotes()` |
| 常量 | UPPER_SNAKE_CASE 或 camelCase | `CONFIG`, `DATA_DIR` |
| 私有变量 | _leading_underscore 或闭包内 | `_instances`, 内部变量 |

### 注释风格

JSDoc 风格的函数注释：

```javascript
/**
 * Subscribe to updates for a specific platform
 * @param {string} platform - Platform identifier ('xhs', 'dy', 'bili', 'zhihu')
 * @param {function} callback - Callback function to be called on update
 * @returns {function} Unsubscribe function
 */
function subscribe(platform, callback) {
    // ...
}
```

### 导出方式

使用 `window` 对象导出模块：

```javascript
// 导出函数供其他模块使用
window.app = {
    loadNotes,
    updateLastUpdate
};

window.WSClient = {
    connect,
    disconnect,
    subscribe
};
```

## 4. 文件组织结构

### 项目目录结构

```
MediaCrawler/
├── api/                      # FastAPI 后端
│   ├── main.py               # 应用入口
│   ├── routers/              # API 路由模块
│   │   ├── notes.py          # 小红书笔记 API
│   │   ├── douyin.py         # 抖音 API
│   │   └── ...
│   ├── schemas/              # 数据模型定义
│   └── services/             # 业务逻辑服务
├── store/                    # 存储层
│   ├── xhs/                  # 小红书存储实现
│   │   ├── __init__.py       # 工厂类导出
│   │   ├── _store_impl.py    # 具体实现类
│   │   └── xhs_store_media.py
│   ├── douyin/               # 抖音存储实现
│   └── excel_store_base.py   # Excel 基础类
├── viewer/                   # 前端可视化界面
│   └── static/
│       ├── index.html
│       └── js/
│           ├── app.js
│           └── websocket-client.js
├── tests/                    # 单元测试
├── test/                     # 集成/工具测试
├── tools/                    # 工具模块
├── base/                     # 基类和抽象接口
└── config/                   # 配置文件
```

### 模块文件命名

- `__init__.py`: 模块初始化和公共接口导出
- `_store_impl.py`: 私有实现文件（下划线前缀表示内部使用）
- `{platform}_store_media.py`: 平台特定的媒体存储逻辑

## 5. 类设计规范

### 抽象基类

使用 ABC 定义抽象基类：

```python
from abc import ABC, abstractmethod
from typing import Dict

class AbstractStore(ABC):
    @abstractmethod
    async def store_content(self, content_item: Dict):
        pass

    @abstractmethod
    async def store_comment(self, comment_item: Dict):
        pass

    @abstractmethod
    async def store_creator(self, creator: Dict):
        pass
```

### 单例模式

使用类变量和锁实现线程安全的单例：

```python
class ExcelStoreBase(AbstractStore):
    _instances: Dict[str, "ExcelStoreBase"] = {}
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, platform: str, crawler_type: str) -> "ExcelStoreBase":
        key = f"{platform}_{crawler_type}"
        with cls._lock:
            if key not in cls._instances:
                cls._instances[key] = cls(platform, crawler_type)
            return cls._instances[key]
```

### 工厂模式

使用字典映射实现工厂：

```python
class XhsStoreFactory:
    STORES = {
        'csv': XhsCsvStoreImplement,
        'json': XhsJsonStoreImplement,
        'jsonl': XhsJsonlStoreImplement,
        'db': XhsDbStoreImplement,
        'sqlite': XhsSqliteStoreImplement,
        'mongodb': XhsMongoStoreImplement,
        'excel': XhsExcelStoreImplement
    }

    @classmethod
    def create_store(cls) -> AbstractStore:
        save_option = config.SAVE_DATA_OPTION
        if save_option not in cls.STORES:
            raise ValueError(f"Invalid save option: {save_option}")
        return cls.STORES[save_option]()
```

## 6. 错误处理模式

### FastAPI 错误处理

使用 HTTPException 返回标准错误：

```python
from fastapi import HTTPException

@router.get("/{note_id}")
async def get_note_detail(note_id: str) -> Dict[str, Any]:
    if not validate_note_id(note_id):
        raise HTTPException(status_code=400, detail="Invalid note ID format")

    # ... 查找逻辑

    raise HTTPException(status_code=404, detail="Note not found")
```

### 异步操作错误处理

```python
async def store_content(self, content_item: Dict):
    note_id = content_item.get("note_id")
    if not note_id:
        return  # 静默处理，或记录日志

    try:
        await self.mongo_store.save_or_update(
            collection_suffix="contents",
            query={"note_id": note_id},
            data=content_item
        )
        utils.logger.info(f"Saved note {note_id} to MongoDB")
    except Exception as e:
        utils.logger.error(f"Error saving note {note_id}: {e}")
        raise
```

## 7. 日志记录约定

### 日志配置

```python
import logging

def init_loging_config():
    level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)s %(levelname)s (%(filename)s:%(lineno)d) - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    _logger = logging.getLogger("MediaCrawler")
    _logger.setLevel(level)
    return _logger

logger = init_loging_config()
```

### 日志使用

```python
from tools import utils

# 信息日志
utils.logger.info(f"[ExcelStoreBase] Stored content to Excel: {content_id}")

# 错误日志
utils.logger.error(f"[ExcelStoreBase] Error saving Excel file: {e}")
```

### 日志格式约定

- 使用方括号标记模块名：`[ModuleName]`
- 包含关键操作信息
- 错误日志包含异常详情

## 8. Pre-commit Hooks

项目配置了 pre-commit hooks 确保代码质量：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-file-headers
        name: Check Python file headers
        entry: python3 tools/file_header_manager.py --check
        types: [python]

      - id: add-file-headers
        name: Add copyright headers to Python files
        entry: python3 tools/file_header_manager.py
        types: [python]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=10240']
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: mixed-line-ending
```

## 9. 安全规范

### 路径遍历防护

所有文件路径用户输入必须验证：

```python
import re

NOTE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

def validate_note_id(note_id: str) -> bool:
    """Validate note_id to prevent path traversal attacks."""
    if not note_id or len(note_id) > 64:
        return False
    return bool(NOTE_ID_PATTERN.match(note_id))

def get_local_image_count(note_id: str) -> int:
    if not validate_note_id(note_id):
        return 0

    note_image_dir = IMAGES_DIR / note_id

    # 额外安全检查
    try:
        note_image_dir.resolve().relative_to(IMAGES_DIR.resolve())
    except (ValueError, OSError):
        return 0
    # ...
```

### FastAPI 参数验证

使用 Query/Path 验证器：

```python
from fastapi import Query

@router.get("")
async def list_notes(
    keyword: Optional[str] = Query(None, max_length=50, description="Filter by source keyword"),
    search: Optional[str] = Query(None, max_length=100, description="Search in title"),
    offset: int = Query(0, ge=0, le=10000, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=500, description="Number of results")
) -> Dict[str, Any]:
    ...
```

## 10. 依赖管理

项目使用 `uv` 和 `pyproject.toml` 管理依赖：

```toml
[project]
name = "mediacrawler"
requires-python = ">=3.11"
dependencies = [
    "fastapi==0.110.2",
    "pydantic==2.5.2",
    "uvicorn==0.29.0",
    # ...
]

# 开发依赖
dependencies = [
    # ...
    "pre-commit>=3.5.0",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
]
```

---

**最后更新**: 2024年4月
**维护者**: MediaCrawler 团队
