# 集成文档

## 概述

MediaCrawler 项目集成了多种外部服务、数据库系统、第三方 API 和代理服务，构建了一个完整的数据采集生态系统。本文档详细记录了项目中的各类集成点及其配置方式。

## 数据库连接

### MySQL
- **驱动**: asyncmy / aiomysql
- **用途**: 结构化数据持久化存储
- **配置参数**:
  - `MYSQL_DB_HOST`: 数据库主机地址
  - `MYSQL_DB_PORT`: 端口号（默认 3306）
  - `MYSQL_DB_USER`: 用户名
  - `MYSQL_DB_PWD`: 密码
  - `MYSQL_DB_NAME`: 数据库名称（默认 media_crawler）
- **连接字符串**: `mysql+asyncmy://{user}:{password}@{host}:{port}/{db_name}`
- **ORM**: SQLAlchemy 2.0+ 异步模式

### PostgreSQL
- **驱动**: asyncpg
- **用途**: 企业级关系型数据存储
- **配置参数**:
  - `POSTGRES_DB_HOST`: 数据库主机地址
  - `POSTGRES_DB_PORT`: 端口号（默认 5432）
  - `POSTGRES_DB_USER`: 用户名（默认 postgres）
  - `POSTGRES_DB_PWD`: 密码
  - `POSTGRES_DB_NAME`: 数据库名称
- **连接字符串**: `postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}`

### SQLite
- **驱动**: aiosqlite
- **用途**: 轻量级本地数据存储，无需额外服务
- **配置**: 本地文件路径 `database/sqlite_tables.db`
- **连接字符串**: `sqlite+aiosqlite:///{db_path}`

### MongoDB
- **驱动**: Motor（Motor 是 PyMongo 的异步版本）
- **用途**: 文档型数据存储，适合非结构化爬虫数据
- **配置参数**:
  - `MONGODB_HOST`: 主机地址（默认 localhost）
  - `MONGODB_PORT`: 端口号（默认 27017）
  - `MONGODB_USER`: 用户名（可选）
  - `MONGODB_PWD`: 密码（可选）
  - `MONGODB_DB_NAME`: 数据库名称
- **连接模式**: 单例模式连接池
- **集合命名**: `{platform}_{collection_suffix}` 格式

### Redis
- **驱动**: redis-py
- **用途**: 
  - 缓存存储
  - Cookie 管理
  - 代理 IP 池状态管理
  - 爬虫状态缓存
- **配置参数**:
  - `REDIS_DB_HOST`: 主机地址（默认 127.0.0.1）
  - `REDIS_DB_PORT`: 端口号（默认 6379）
  - `REDIS_DB_PWD`: 密码
  - `REDIS_DB_NUM`: 数据库编号（默认 0）

## 社交媒体平台 API 集成

### 小红书 (Xiaohongshu)
- **API 域名**: 
  - 国内: `https://edith.xiaohongshu.com`
  - 国际版: `https://webapi.rednote.com`
- **认证方式**: Cookie + 签名验证
- **签名算法**: 使用 xhshow 纯算法生成 X-S、X-T、X-S-Common 等签名头
- **支持功能**:
  - 关键词搜索笔记
  - 笔记详情获取
  - 评论采集（一级/二级评论）
  - 创作者信息获取
  - 创作者笔记列表

### 抖音 (Douyin)
- **API 类型**: 移动端 Web API
- **认证方式**: Cookie 登录
- **支持功能**:
  - 视频搜索
  - 视频详情
  - 评论采集
  - 创作者信息

### B站 (Bilibili)
- **API 类型**: Web API
- **认证方式**: Cookie 登录
- **支持功能**:
  - 视频搜索
  - 视频详情
  - 评论采集
  - UP主信息

### 知乎 (Zhihu)
- **API 类型**: Web API
- **认证方式**: Cookie 登录
- **支持功能**:
  - 问答搜索
  - 回答详情
  - 评论采集

### 微博 (Weibo)
- **API 类型**: Web API
- **认证方式**: Cookie 登录
- **支持功能**:
  - 微博搜索
  - 微博详情
  - 评论采集
  - 图片/视频下载

### 快手 (Kuaishou)
- **API 类型**: GraphQL API
- **认证方式**: Cookie 登录
- **支持功能**:
  - 视频搜索
  - 用户信息
  - 视频详情

### 百度贴吧 (Baidu Tieba)
- **API 类型**: Web API
- **认证方式**: Cookie 登录
- **支持功能**:
  - 帖子搜索
  - 帖子详情
  - 评论采集

## 代理服务集成

### 蜿豆 HTTP 代理
- **配置参数**:
  - `WANDOU_APP_KEY`: 应用密钥
- **特点**: HTTP/HTTPS 代理池

### 快代理 (Kuaidaili)
- **配置参数**:
  - `KDL_SECERT_ID`: 密钥 ID
  - `KDL_SIGNATURE`: 签名
  - `KDL_USER_NAME`: 用户名
  - `KDL_USER_PWD`: 密码
- **特点**: 支持 API 提取和用户名密码认证

### 极速 HTTP 代理 (Jisu)
- **配置参数**:
  - `jisu_key`: 提取密钥
  - `jisu_crypto`: 加密签名
- **特点**: 快速 IP 提取

### 代理池特性
- **自动刷新**: 代理过期自动切换
- **代理模式**: 支持 Mixin 模式注入到 HTTP 客户端
- **配置灵活**: 支持多种代理服务商切换

## 浏览器自动化集成

### Playwright
- **浏览器类型**: Chromium
- **启动模式**:
  - 标准模式: Playwright 启动浏览器
  - CDP 模式: 连接已有浏览器实例
- **用途**:
  - 模拟登录（二维码/手机号/Cookie）
  - JavaScript 渲染
  - 滑块验证码处理
  - Cookie 获取

### CDP (Chrome DevTools Protocol)
- **用途**: 远程调试协议，连接已启动的浏览器
- **优势**: 
  - 复用已有登录状态
  - 减少检测风险
  - 共享浏览器会话

## 实时通信集成

### WebSocket
- **服务端**: FastAPI WebSocket 端点
- **端点**:
  - `/api/ws/logs`: 实时日志推送
  - `/api/ws/status`: 爬虫状态推送
- **功能**:
  - 爬虫进度实时更新
  - 日志流实时推送
  - 心跳保活机制
  - 数据变更广播

### 文件监控 (watchdog)
- **监控目录**: `data/{platform}/jsonl/`
- **触发机制**: 文件变更时推送 WebSocket 消息
- **消息类型**:
  - `stats_update`: 统计数据更新
  - `data_update`: 平台数据更新
  - `subscription_update`: 订阅更新通知

## 外部工具集成

### xhshow 签名库
- **用途**: 小红书 API 签名算法
- **输入**: URI、请求数据、Cookie、请求方法
- **输出**: X-S、X-T、X-S-Common、X-B3-Traceid 签名头

### PyExecJS
- **用途**: 执行 JavaScript 签名算法
- **应用场景**: 各平台加密参数生成

### OpenCV
- **用途**: 
  - 滑块验证码识别
  - 图像处理
  - 滑块轨迹模拟

## 认证机制

### Cookie 认证
- **存储位置**: 
  - 本地文件: `browser_data/{platform}/cookies.json`
  - Redis 缓存
- **自动刷新**: 支持登录状态检测和自动重新登录

### 登录方式
1. **二维码登录**: Playwright 渲染二维码页面
2. **手机号登录**: SMS 验证码登录
3. **Cookie 登录**: 导入已有 Cookie

## 文件存储方案

### 本地文件系统
- **数据格式**:
  - JSONL: 行分隔 JSON，适合增量写入
  - JSON: 标准格式，适合完整导出
  - CSV: 表格格式，适合数据分析
  - Excel: xlsx 格式，适合业务报告
- **存储路径**: `data/{platform}/`
  - `jsonl/`: JSONL 数据文件
  - `json/`: JSON 数据文件
  - `images/`: 图片资源

### 图片存储
- **格式**: JPG/WebP/AVIF
- **路径**: `data/{platform}/images/`
- **处理**: Pillow 库进行格式转换和压缩

## 环境配置

### 环境变量 (.env)
项目通过 `.env` 文件管理敏感配置，示例配置：

```env
# 数据库配置
MYSQL_DB_PWD=123456
REDIS_DB_PWD=123456
MONGODB_PWD=

# 代理配置
WANDOU_APP_KEY=
KDL_SECERY_ID=
jisu_key=
```

### 配置加载
- **库**: python-dotenv
- **优先级**: 环境变量 > .env 文件 > 默认值

## 迁移系统

### Alembic
- **用途**: 数据库迁移管理
- **支持**: MySQL / PostgreSQL / SQLite
- **命令**: 通过 SQLAlchemy 模型自动生成迁移脚本

## 总结

MediaCrawler 的集成架构设计具有以下特点：

1. **多数据源支持**: 支持 5 种数据库后端，覆盖从开发到生产的各种场景
2. **平台广覆盖**: 集成 7 大主流社交媒体平台
3. **代理池灵活**: 支持多种代理服务商，自动切换机制
4. **实时性强**: WebSocket + 文件监控实现毫秒级数据更新
5. **认证多样化**: 支持多种登录方式，适配不同使用场景
6. **可扩展性好**: 模块化设计，便于添加新平台和新存储后端
