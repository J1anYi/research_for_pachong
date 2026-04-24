---
title: 关键词订阅系统 + 数据趋势看板
type: feat
status: approved
date: 2026-04-21
---

# 关键词订阅系统 + 数据趋势看板

## 概述

为 MediaCrawler 添加关键词订阅功能，用户可以订阅感兴趣的关键词，系统会定期自动爬取并展示数据趋势变化。

## 功能范围（第一阶段）

### 包含功能
- ✅ 小红书、知乎两个平台的订阅
- ✅ 订阅的增删改查
- ✅ 手动触发爬取
- ✅ 基础趋势图表（折线图、统计卡片）
- ✅ WebSocket 新数据通知

### 不包含（第二阶段）
- ❌ 抖音、B站平台
- ❌ 自动定时调度
- ❌ 浏览器推送通知
- ❌ 数据导出功能

## 核心模块

### 1. 订阅管理模块

**数据模型：**
```json
{
  "id": "sub_001",
  "keyword": "Python教程",
  "platform": "zhihu",
  "frequency": "daily",
  "status": "active",
  "created_at": "2026-04-21T10:00:00",
  "last_crawled_at": null,
  "crawl_count": 0
}
```

**API 端点：**
- `GET /api/subscriptions` - 获取订阅列表
- `POST /api/subscriptions` - 创建订阅
- `PUT /api/subscriptions/{id}` - 更新订阅
- `DELETE /api/subscriptions/{id}` - 删除订阅
- `POST /api/subscriptions/{id}/run` - 立即执行爬取

### 2. 趋势看板模块

**API 端点：**
- `GET /api/trends/{subscription_id}` - 获取订阅趋势数据
- `GET /api/trends/compare` - 多订阅对比数据

**数据统计：**
- 每日新增数据量
- 总互动数（点赞+评论+分享）
- 平均互动数
- 热度趋势

### 3. 通知模块

**WebSocket 消息：**
```json
{
  "type": "subscription_update",
  "subscription_id": "sub_001",
  "keyword": "Python教程",
  "platform": "zhihu",
  "new_count": 15,
  "timestamp": "2026-04-21T10:30:00"
}
```

## 技术方案

### 后端文件
- `api/routers/subscriptions.py` - 订阅管理 API
- `api/routers/trends.py` - 趋势数据 API
- `api/services/subscription_manager.py` - 订阅管理服务
- `data/subscriptions.json` - 订阅数据存储

### 前端文件
- `viewer/static/js/subscriptions-app.js` - 订阅管理页面逻辑
- `viewer/static/js/trends-app.js` - 趋势看板页面逻辑

### 第三方依赖
- Chart.js（CDN引入）- 图表绘制

## 用户界面

### 订阅管理页面
- 订阅列表表格（关键词、平台、状态、操作）
- 添加订阅表单（关键词输入、平台选择）
- 编辑/删除操作

### 趋势看板
- 热度趋势折线图
- 互动数据统计卡片
- 时间范围筛选

## 实现顺序

1. 后端订阅管理 API
2. 前端订阅管理页面
3. 手动触发爬取功能
4. 趋势数据 API
5. 前端趋势看板
6. WebSocket 通知集成
