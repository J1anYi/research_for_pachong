# 测试文档

本文档记录 MediaCrawler 项目的测试框架、测试策略和测试约定。

## 1. 测试框架

### 核心测试工具

| 工具 | 版本 | 用途 |
|------|------|------|
| pytest | >=7.4.0 | 主测试框架 |
| pytest-asyncio | >=0.21.0 | 异步测试支持 |
| unittest.mock | 内置 | Mock 和 Patch |

### 依赖配置

测试依赖定义在 `pyproject.toml` 中：

```toml
[project]
dependencies = [
    # ... 其他依赖
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
]
```

## 2. 测试目录结构

项目包含两个测试目录：

```
MediaCrawler/
├── tests/                      # 单元测试目录
│   ├── __init__.py
│   ├── conftest.py             # 共享 fixtures
│   ├── test_excel_store.py     # Excel 存储测试
│   └── test_store_factory.py   # 存储工厂测试
│
└── test/                       # 集成/工具测试目录
    ├── __init__.py
    ├── test_utils.py           # 工具函数测试
    ├── test_db_sync.py         # 数据库同步测试
    ├── test_mongodb_integration.py  # MongoDB 集成测试
    ├── test_redis_cache.py     # Redis 缓存测试
    ├── test_proxy_ip_pool.py   # 代理池测试
    └── test_expiring_local_cache.py  # 本地缓存测试
```

### 目录用途说明

- **`tests/`**: 单元测试，测试独立模块和函数
- **`test/`**: 集成测试和工具测试，需要外部依赖（数据库、缓存等）

## 3. 测试文件命名约定

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 单元测试文件 | `test_{module_name}.py` | `test_excel_store.py`, `test_utils.py` |
| 集成测试文件 | `test_{feature}_integration.py` | `test_mongodb_integration.py` |
| Fixture 文件 | `conftest.py` | `tests/conftest.py` |

## 4. 测试类组织

### 类命名约定

测试类使用 PascalCase，以 `Test` 开头：

```python
class TestExcelStoreBase:
    """Test cases for ExcelStoreBase"""
    ...

class TestSingletonPattern:
    """Test singleton pattern for Excel store"""
    ...

class TestXhsStoreFactory:
    """Test cases for XhsStoreFactory"""
    ...
```

### 测试方法命名

测试方法使用 `test_` 前缀，描述测试场景：

```python
def test_initialization(self, excel_store):
    """Test Excel store initialization"""
    ...

def test_store_content(self, excel_store):
    """Test storing content data"""
    ...

def test_invalid_store_option(self):
    """Test that invalid store option raises ValueError"""
    ...
```

## 5. Fixture 使用

### 共享 Fixtures (conftest.py)

项目在 `tests/conftest.py` 中定义共享 fixtures：

```python
import pytest
from pathlib import Path

# 项目路径 fixture
@pytest.fixture(scope="session")
def project_root_path():
    """Return project root path"""
    project_root = Path(__file__).parent.parent
    return project_root

# 测试数据 fixtures
@pytest.fixture
def sample_xhs_note():
    """Sample Xiaohongshu note data for testing"""
    return {
        "note_id": "test_note_123",
        "type": "normal",
        "title": "Test Title",
        "desc": "This is a test description",
        "user_id": "user_123",
        "nickname": "Test User",
        "liked_count": 100,
        "collected_count": 50,
        "comment_count": 25,
        # ...
    }

@pytest.fixture
def sample_xhs_comment():
    """Sample Xiaohongshu comment data for testing"""
    return {
        "comment_id": "comment_123",
        "note_id": "test_note_123",
        "content": "This is a test comment",
        # ...
    }

@pytest.fixture
def sample_xhs_creator():
    """Sample Xiaohongshu creator data for testing"""
    return {
        "user_id": "creator_123",
        "nickname": "Creator Name",
        # ...
    }
```

### 本地 Fixtures

测试文件内部定义的 fixtures：

```python
class TestExcelStoreBase:
    @pytest.fixture(autouse=True)
    def clear_singleton_state(self):
        """Clear singleton state before and after each test"""
        ExcelStoreBase._instances.clear()
        yield
        ExcelStoreBase._instances.clear()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)

    @pytest.fixture
    def excel_store(self, temp_dir, monkeypatch):
        """Create ExcelStoreBase instance for testing"""
        monkeypatch.chdir(temp_dir)
        store = ExcelStoreBase(platform="test", crawler_type="search")
        yield store
```

### Fixture 作用域

| 作用域 | 使用场景 | 示例 |
|--------|----------|------|
| `session` | 整个测试会话只执行一次 | `project_root_path` |
| `function` (默认) | 每个测试函数执行一次 | `sample_xhs_note`, `temp_dir` |
| `autouse=True` | 自动应用于所有测试 | `clear_singleton_state` |

## 6. 异步测试

### 配置 pytest-asyncio

项目使用 `pytest-asyncio` 支持异步测试：

```python
import pytest

class TestExcelStoreBase:
    @pytest.mark.asyncio
    async def test_store_content(self, excel_store):
        """Test storing content data"""
        content_item = {
            "note_id": "test123",
            "title": "Test Title",
            "desc": "Test Description"
        }

        await excel_store.store_content(content_item)

        assert excel_store.contents_sheet.max_row == 2
        assert excel_store.contents_headers_written is True

    @pytest.mark.asyncio
    async def test_store_comment(self, excel_store):
        """Test storing comment data"""
        comment_item = {
            "comment_id": "comment123",
            "note_id": "note456",
            "content": "Great post!"
        }

        await excel_store.store_comment(comment_item)

        assert excel_store.comments_sheet.max_row == 2
```

### 运行异步测试

```bash
# 使用 pytest 自动检测 @pytest.mark.asyncio 标记
pytest tests/test_excel_store.py
```

## 7. Mock 和 Patch 使用

### Patch 配置值

```python
from unittest.mock import patch

class TestXhsStoreFactory:
    @patch('config.SAVE_DATA_OPTION', 'csv')
    def test_create_csv_store(self):
        """Test creating CSV store"""
        store = XhsStoreFactory.create_store()
        assert isinstance(store, XhsCsvStoreImplement)

    @patch('config.SAVE_DATA_OPTION', 'json')
    def test_create_json_store(self):
        """Test creating JSON store"""
        store = XhsStoreFactory.create_store()
        assert isinstance(store, XhsJsonStoreImplement)

    @patch('config.SAVE_DATA_OPTION', 'invalid')
    def test_invalid_store_option(self):
        """Test that invalid store option raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            XhsStoreFactory.create_store()

        assert "Invalid save option" in str(exc_info.value)
```

### 测试异常

使用 `pytest.raises` 测试异常：

```python
def test_invalid_store_option(self):
    """Test that invalid store option raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        XhsStoreFactory.create_store()

    assert "Invalid save option" in str(exc_info.value)
```

## 8. 条件跳过测试

### 跳过缺失依赖的测试

```python
try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


@pytest.mark.skipif(not EXCEL_AVAILABLE, reason="openpyxl not installed")
class TestExcelStoreBase:
    """Test cases for ExcelStoreBase"""
    ...


@pytest.mark.skipif(not EXCEL_AVAILABLE, reason="openpyxl not installed")
def test_excel_import_availability():
    """Test that openpyxl is available"""
    assert EXCEL_AVAILABLE is True
```

## 9. 测试覆盖情况

### 已覆盖的模块

| 模块 | 测试文件 | 覆盖类型 |
|------|----------|----------|
| Excel 存储 | `tests/test_excel_store.py` | 单元测试 |
| 存储工厂 | `tests/test_store_factory.py` | 单元测试 |
| 工具函数 | `test/test_utils.py` | 单元测试 |
| 数据库同步 | `test/test_db_sync.py` | 集成测试 |
| MongoDB 集成 | `test/test_mongodb_integration.py` | 集成测试 |
| Redis 缓存 | `test/test_redis_cache.py` | 集成测试 |
| 代理池 | `test/test_proxy_ip_pool.py` | 集成测试 |
| 本地缓存 | `test/test_expiring_local_cache.py` | 单元测试 |

### 未覆盖的模块

以下模块目前缺少测试覆盖：

- `api/routers/` - API 路由层
- `api/services/` - 服务层
- `viewer/static/js/` - 前端 JavaScript
- 各平台爬虫实现 (`crawler/`)
- 存储实现细节 (`store/xhs/_store_impl.py` 等)

## 10. 测试运行命令

### 运行所有测试

```bash
# 在 MediaCrawler 目录下运行
cd MediaCrawler
uv run pytest
```

### 运行指定测试文件

```bash
# 运行单元测试
uv run pytest tests/

# 运行集成测试
uv run pytest test/

# 运行单个测试文件
uv run pytest tests/test_excel_store.py
```

### 运行详细输出

```bash
# 显示详细输出
uv run pytest -v

# 显示测试函数名
uv run pytest -v --tb=short
```

### 运行带覆盖率报告

```bash
# 安装覆盖率插件
uv add pytest-cov

# 运行并生成覆盖率报告
uv run pytest --cov=. --cov-report=html
```

### 只运行特定标记的测试

```bash
# 只运行异步测试
uv run pytest -m asyncio

# 只运行跳过条件满足的测试
uv run pytest --runxfail
```

## 11. 测试最佳实践

### 测试隔离

每个测试应该独立运行，不依赖其他测试的状态：

```python
@pytest.fixture(autouse=True)
def clear_singleton_state(self):
    """Clear singleton state before and after each test"""
    ExcelStoreBase._instances.clear()
    yield
    ExcelStoreBase._instances.clear()
```

### 使用临时目录

测试文件操作应使用临时目录：

```python
@pytest.fixture
def temp_dir(self):
    """Create temporary directory for test files"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # 清理
    shutil.rmtree(temp_path, ignore_errors=True)
```

### 断言最佳实践

```python
# 好的断言 - 明确的期望
assert excel_store.contents_sheet.max_row == 2  # Header + 1 data row
assert excel_store.contents_headers_written is True

# 好的断言 - 使用 isinstance 检查类型
assert isinstance(store, XhsCsvStoreImplement)

# 好的断言 - 检查异常消息
with pytest.raises(ValueError) as exc_info:
    XhsStoreFactory.create_store()
assert "Invalid save option" in str(exc_info.value)
```

### 测试文档字符串

每个测试方法应有描述性的文档字符串：

```python
def test_initialization(self, excel_store):
    """Test Excel store initialization"""
    ...

def test_all_stores_registered(self):
    """Test that all store types are registered"""
    ...
```

## 12. 集成测试注意事项

### 外部依赖

`test/` 目录中的集成测试需要外部依赖：

- **MySQL/SQLite**: 数据库连接配置
- **MongoDB**: MongoDB 实例
- **Redis**: Redis 服务

运行这些测试前需确保服务可用：

```python
# test/test_db_sync.py
def get_mysql_engine():
    """Create and return a MySQL database engine"""
    conn_str = f"mysql+pymysql://{mysql_db_config['user']}:{mysql_db_config['password']}@..."
    return create_engine(conn_str)
```

### 手动确认

某些测试需要手动确认：

```python
def main():
    """Main function"""
    # ...
    if any(mysql_diff.values()):
        choice = input(">>> Manual confirmation required: Synchronize ORM model to MySQL database? (y/N): ")
        if choice.lower() == 'y':
            sync_database(mysql_engine, mysql_diff)
```

## 13. 前端测试

目前项目没有前端 JavaScript 的自动化测试。建议添加：

- **测试框架**: Jest 或 Vitest
- **测试位置**: `viewer/static/js/__tests__/`
- **覆盖内容**: API 调用、WebSocket 连接、UI 交互

---

**最后更新**: 2024年4月
**维护者**: MediaCrawler 团队
