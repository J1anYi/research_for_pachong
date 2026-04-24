---
date: 2026-04-20
topic: bilibili-popular-rank
---

# B站热门榜单爬取功能

## Problem Frame

用户希望爬取B站首页热门榜单的前100个视频，但当前MediaCrawler只支持关键词搜索、指定视频详情、UP主数据三种模式，不支持热门榜单。

## Requirements

**核心功能**
- R1. 新增爬虫类型 `popular`，支持爬取B站热门视频榜单
- R2. 使用B站官方API `https://api.bilibili.com/x/web-interface/popular` 获取热门视频列表
- R3. 支持配置爬取数量（默认100条）
- R4. 数据存储格式与现有搜索模式一致（JSONL/JSON/CSV等）

**API集成**
- R5. 支持分页获取（每页最多20条，需5页获取100条）
- R6. 复用现有的视频详情获取逻辑和评论爬取逻辑

## Success Criteria

- 执行 `CRAWLER_TYPE=popular PLATFORM=bili` 能成功爬取热门榜单
- 爬取100条视频数据并保存到 `data/bili/jsonl/` 目录
- 数据包含视频基本信息、UP主信息、评论（如启用）

## Scope Boundaries

- 不包含视频下载功能（已有ENABLE_GET_MEIDAS配置）
- 不包含个性化热门（需要登录Cookie）
- 仅支持B站平台

## Key Decisions

- **API选择**: 使用 `/x/web-interface/popular` 接口，无需登录即可获取
- **爬虫模式**: 新增 `popular` 类型，复用现有架构
- **数据格式**: 与搜索模式保持一致，存储到相同目录

## Dependencies / Assumptions

- B站API稳定可用
- 无需登录即可获取热门榜单数据

## Outstanding Questions

### Deferred to Planning

- [Affects R5][Technical] 是否需要处理API限流或风控？

## Next Steps

→ /ce:plan for structured implementation planning
