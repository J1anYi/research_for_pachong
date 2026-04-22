# MediaCrawler 目录结构文档

## 项目根目录

```
E:\code_github\research_for_pachong\
├── MediaCrawler/                 # 主项目目录
│   ├── api/                      # FastAPI 后端服务
│   ├── base/                     # 抽象基类定义
│   ├── browser_data/             # 浏览器用户数据目录
│   ├── cache/                    # 缓存系统
│   ├── cmd_arg/                  # 命令行参数解析
│   ├── config/                   # 配置模块
│   ├── constant/                 # 常量定义
│   ├── data/                     # 数据存储目录
│   ├── database/                 # 数据库模块
│   ├── docs/                     # 项目文档
│   ├── libs/                     # 第三方库
│   ├── media_platform/           # 平台爬虫实现
│   ├── model/                    # 数据模型
│   ├── proxy/                    # 代理模块
│   ├── store/                    # 存储实现
│   ├── tools/                    # 工具函数
│   ├── viewer/                   # 前端可视化界面
│   ├── main.py                   # CLI 入口
│   ├── pyproject.toml            # 项目配置
│   └── .venv/                    # Python 虚拟环境
├── venv/                         # 根目录虚拟环境
├── docs/                         # 规划文档目录
│   ├── brainstorms/
│   ├── ideation/
│   ├── plans/
│   └── superpowers/
├── .planning/                    # 分析文档目录
│   └── codebase/
└── CLAUDE.md                     # Claude 项目说明
```

---

## 核心目录详解

### 1. api/ - API 服务层

```
MediaCrawler/api/
├── __init__.py
├── main.py                    # FastAPI 应用入口
├── routers/                   # API 路由模块
│   ├── __init__.py
│   ├── bilibili.py           # B站数据 API
│   ├── crawler.py            # 爬虫控制 API (启动/停止/状态)
│   ├── data.py               # 通用数据查询 API
│   ├── douyin.py             # 抖音数据 API
│   ├── notes.py              # 小红书笔记 API
│   ├── subscriptions.py      # 订阅管理 API
│   ├── trends.py             # 趋势分析 API
│   ├── websocket.py          # WebSocket 实时推送
│   └── zhihu.py              # 知乎数据 API
├── schemas/                   # Pydantic 请求/响应模型
│   ├── __init__.py
│   └── crawler.py            # 爬虫相关数据结构
├── services/                  # 业务服务层
│   ├── __init__.py
│   ├── crawler_manager.py    # 爬虫进程管理
│   ├── file_watcher.py       # 文件变更监控服务
│   └── subscription_manager.py # 订阅任务管理
└── webui/                     # 前端构建产物
    ├── index.html
    ├── assets/               # 静态资源
    └── logos/                # 平台 Logo
```

**关键文件说明：**

| 文件 | 用途 |
|------|------|
| `main.py` | FastAPI 应用入口，注册路由，配置 CORS，挂载静态文件 |
| `routers/crawler.py` | 爬虫控制：启动、停止、获取状态、获取日志 |
| `services/file_watcher.py` | 使用 watchdog 监控 JSONL/JSON 文件变更，触发 WebSocket 推送 |

---

### 2. base/ - 抽象基类

```
MediaCrawler/base/
├── __init__.py
└── base_crawler.py            # 核心抽象类定义
```

**base_crawler.py 定义的抽象类：**

```python
class AbstractCrawler:      # 爬虫基类
    - start()               # 启动爬虫
    - search()              # 搜索内容
    - launch_browser()      # 启动浏览器

class AbstractLogin:        # 登录基类
    - begin()               # 开始登录流程
    - login_by_qrcode()     # 二维码登录
    - login_by_mobile()     # 手机登录
    - login_by_cookies()    # Cookie 登录

class AbstractStore:        # 存储基类
    - store_content()       # 存储内容
    - store_comment()       # 存储评论
    - store_creator()       # 存储创作者信息

class AbstractApiClient:    # API 客户端基类
    - request()             # 发送请求
    - update_cookies()      # 更新 Cookie
```

---

### 3. media_platform/ - 平台爬虫实现

```
MediaCrawler/media_platform/
├── __init__.py
├── xhs/                       # 小红书爬虫
│   ├── __init__.py
│   ├── client.py             # API 客户端
│   ├── core.py               # 核心爬虫逻辑
│   ├── exception.py          # 自定义异常
│   ├── extractor.py          # HTML 解析器
│   ├── field.py              # 枚举常量
│   ├── help.py               # 辅助函数
│   ├── login.py              # 登录实现
│   ├── playwright_sign.py    # 签名算法
│   └── xhs_sign.py           # 签名算法
├── douyin/                    # 抖音爬虫
│   ├── client.py
│   ├── core.py
│   ├── exception.py
│   ├── field.py
│   ├── help.py
│   └── login.py
├── bilibili/                  # B站爬虫
│   ├── exception.py
│   ├── field.py
│   ├── help.py
│   └── login.py
├── zhihu/                     # 知乎爬虫
│   ├── client.py
│   ├── core.py
│   ├── exception.py
│   ├── field.py
│   ├── help.py
│   └── login.py
├── weibo/                     # 微博爬虫
│   ├── client.py
│   ├── core.py
│   ├── exception.py
│   ├── field.py
│   ├── help.py
│   └── login.py
├── kuaishou/                  # 快手爬虫
│   ├── client.py
│   ├── core.py
│   ├── exception.py
│   ├── field.py
│   ├── graphql.py
│   ├── help.py
│   └── login.py
└── tieba/                     # 百度贴吧爬虫
    ├── client.py
    ├── core.py
    ├── field.py
    ├── help.py
    └── login.py
```

**每个平台的模块职责：**

| 文件 | 职责 |
|------|------|
| `core.py` | 爬虫主逻辑，继承 AbstractCrawler |
| `client.py` | API 客户端，继承 AbstractApiClient |
| `login.py` | 登录流程，继承 AbstractLogin |
| `field.py` | 枚举类型、常量定义 |
| `help.py` | URL 解析、ID 提取等辅助函数 |
| `exception.py` | 平台特有异常类 |

---

### 4. store/ - 数据存储实现

```
MediaCrawler/store/
├── __init__.py
├── excel_store_base.py        # Excel 存储基类
├── xhs/                       # 小红书存储实现
│   ├── __init__.py
│   ├── _store_impl.py        # 各存储类型实现
│   └── xhs_store_media.py    # 媒体文件存储
├── douyin/                    # 抖音存储实现
│   ├── __init__.py
│   ├── _store_impl.py
│   └── douyin_store_media.py
├── bilibili/                  # B站存储实现
│   ├── __init__.py
│   ├── _store_impl.py
│   └── bilibilli_store_media.py
├── zhihu/                     # 知乎存储实现
│   ├── __init__.py
│   └── _store_impl.py
├── weibo/                     # 微博存储实现
│   ├── __init__.py
│   ├── _store_impl.py
│   └── weibo_store_media.py
├── kuaishou/                  # 快手存储实现
│   ├── __init__.py
│   └── _store_impl.py
└── tieba/                     # 贴吧存储实现
    ├── __init__.py
    └── _store_impl.py
```

**存储实现类型：**

| 实现类 | 存储格式 | 说明 |
|--------|----------|------|
| `XhsCsvStoreImplement` | CSV | 逗号分隔值文件 |
| `XhsJsonStoreImplement` | JSON | 标准 JSON 文件 |
| `XhsJsonlStoreImplement` | JSONL | 每行一个 JSON 对象 |
| `XhsDbStoreImplement` | MySQL | 关系型数据库 |
| `XhsSqliteStoreImplement` | SQLite | 轻量级数据库 |
| `XhsMongoStoreImplement` | MongoDB | 文档数据库 |
| `XhsExcelStoreImplement` | Excel | 电子表格文件 |

---

### 5. config/ - 配置模块

```
MediaCrawler/config/
├── __init__.py               # 配置导出
├── db_config.py              # 数据库配置
├── dy_config.py              # 抖音配置
├── ks_config.py              # 快手配置
├── tieba_config.py           # 贴吧配置
├── weibo_config.py           # 微博配置
└── xhs_config.py             # 小红书配置
```

**核心配置项：**

```python
# 平台配置
PLATFORM: str              # "xhs" | "dy" | "bili" | ...

# 爬虫配置
CRAWLER_TYPE: str          # "search" | "detail" | "creator"
CRAWLER_MAX_NOTES_COUNT: int
CRAWLER_MAX_SLEEP_SEC: float

# 存储配置
SAVE_DATA_OPTION: str      # "jsonl" | "json" | "csv" | "excel" | "db" | "sqlite" | "mongodb"

# 代理配置
ENABLE_IP_PROXY: bool
IP_PROXY_PROVIDER_NAME: str
IP_PROXY_POOL_COUNT: int

# 浏览器配置
HEADLESS: bool
ENABLE_CDP_MODE: bool
```

---

### 6. database/ - 数据库模块

```
MediaCrawler/database/
├── __init__.py
├── db.py                    # 数据库初始化
├── db_session.py            # 会话管理
├── models.py                # SQLAlchemy ORM 模型
└── mongodb_store_base.py    # MongoDB 存储基类
```

**ORM 模型 (models.py)：**

| 模型类 | 表名 | 说明 |
|--------|------|------|
| `XhsNote` | xhs_note | 小红书笔记 |
| `XhsNoteComment` | xhs_note_comment | 小红书评论 |
| `XhsCreator` | xhs_creator | 小红书创作者 |
| `DouyinVideo` | douyin_video | 抖音视频 |
| `BilibiliVideo` | bilibili_video | B站视频 |
| `ZhihuNote` | zhihu_note | 知乎回答 |

---

### 7. model/ - 数据模型

```
MediaCrawler/model/
├── __init__.py
├── m_baidu_tieba.py         # 贴吧数据模型
├── m_bilibili.py            # B站数据模型
├── m_douyin.py              # 抖音数据模型
├── m_kuaishou.py            # 快手数据模型
├── m_weibo.py               # 微博数据模型
├── m_xiaohongshu.py         # 小红书数据模型
└── m_zhihu.py               # 知乎数据模型
```

**Pydantic 模型示例：**

```python
# model/m_xiaohongshu.py
class NoteUrlInfo(BaseModel):
    note_id: str
    xsec_source: str
    xsec_token: str

class CreatorUrlInfo(BaseModel):
    user_id: str
    xsec_token: str
    xsec_source: str
```

---

### 8. proxy/ - 代理模块

```
MediaCrawler/proxy/
├── __init__.py
├── base_proxy.py            # 代理提供者抽象基类
├── proxy_ip_pool.py         # IP 代理池实现
├── proxy_mixin.py           # 代理刷新 Mixin
├── types.py                 # 类型定义
└── providers/               # 代理服务商实现
    ├── __init__.py
    ├── jishu_http_proxy.py  # 极速代理
    ├── kuaidl_proxy.py      # 快代理
    └── wandou_http_proxy.py # 蜿豆代理
```

---

### 9. cache/ - 缓存系统

```
MediaCrawler/cache/
├── __init__.py
├── abs_cache.py             # 缓存抽象基类
├── cache_factory.py         # 缓存工厂
├── local_cache.py           # 本地内存缓存
└── redis_cache.py           # Redis 缓存
```

---

### 10. viewer/ - 前端可视化界面

```
MediaCrawler/viewer/
└── static/
    ├── index.html           # 主页面
    ├── css/
    │   └── style.css       # 样式文件
    └── js/
        ├── api.js          # 小红书 API 封装
        ├── app.js          # 小红书应用逻辑
        ├── modal.js        # 小红书模态框
        ├── monitor.js      # 监控面板
        ├── douyin-api.js   # 抖音 API
        ├── douyin-app.js   # 抖音应用
        ├── douyin-modal.js # 抖音模态框
        ├── bilibili-api.js # B站 API
        ├── bilibili-app.js # B站应用
        ├── bilibili-modal.js
        ├── zhihu-api.js    # 知乎 API
        ├── zhihu-app.js    # 知乎应用
        ├── zhihu-modal.js
        ├── subscriptions-app.js # 订阅管理
        ├── trends-app.js   # 趋势分析
        ├── websocket-client.js # WebSocket 客户端
        └── notifications.js # 实时通知组件
```

---

### 11. tools/ - 工具函数

```
MediaCrawler/tools/
├── async_file_writer.py     # 异步文件写入器
├── cdp_browser.py           # CDP 浏览器管理
├── httpx_util.py            # HTTPX 工具函数
├── time_util.py             # 时间工具
├── app_runner.py            # 应用运行器
└── utils.py                 # 通用工具函数
```

---

### 12. data/ - 数据存储目录

```
MediaCrawler/data/
├── xhs/                     # 小红书数据
│   ├── jsonl/              # JSONL 格式
│   ├── json/               # JSON 格式
│   ├── images/             # 图片资源
│   └── videos/             # 视频资源
├── dy/                      # 抖音数据
│   ├── jsonl/
│   ├── json/
│   └── videos/
├── bili/                    # B站数据
│   ├── jsonl/
│   └── json/
└── zhihu/                   # 知乎数据
    ├── jsonl/
    └── json/
```

---

## 入口点

### 1. CLI 入口

```bash
# 启动爬虫
cd MediaCrawler
uv run python main.py --platform xhs --type search

# 初始化数据库
uv run python main.py --init_db sqlite
```

### 2. API 服务入口

```bash
# 启动 Web UI 服务
cd MediaCrawler
uv run uvicorn api.main:app --port 8080 --reload

# 或直接运行
uv run python -m api.main
```

**访问地址：**
- API 文档: http://localhost:8080/docs
- 数据查看器: http://localhost:8080/viewer/
- Web UI: http://localhost:8080/

---

## 配置文件位置

| 文件 | 用途 |
|------|------|
| `MediaCrawler/pyproject.toml` | 项目依赖配置 |
| `MediaCrawler/config/*.py` | 各平台配置参数 |
| `MediaCrawler/.env` | 环境变量（可选） |

---

## 第三方库目录

```
MediaCrawler/libs/
├── stealth.min.js           # 反检测脚本
├── douyin.js                # 抖音签名
└── zhihu.js                 # 知乎签名
```

---

## 浏览器数据目录

```
MediaCrawler/browser_data/
├── xhs_user_data_dir/       # 小红书登录状态
├── bili_user_data_dir/      # B站登录状态
├── zhihu_user_data_dir/     # 知乎登录状态
└── ...                      # 其他平台
```

登录状态持久化，避免每次重新登录。
