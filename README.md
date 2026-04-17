# Research for Pachong

小红书内容爬取和数据展示系统。

## 项目结构

- `MediaCrawler/` - 基于 Playwright 的小红书爬虫（子模块）
- `docs/brainstorms/` - 需求文档
- `docs/plans/` - 实施计划

## 功能

1. **小红书内容爬取** - 二维码登录、关键词搜索、笔记爬取、图片下载
2. **数据展示前端** - 瀑布流卡片布局、实时监控、轮询刷新

## 快速开始

```bash
# 启动爬虫（在 MediaCrawler 目录）
cd MediaCrawler
uv run uvicorn api.main:app --port 8080 --reload

# 访问数据查看器
# http://localhost:8080/viewer/
```

## 文档

- [爬虫需求文档](docs/brainstorms/2026-04-17-xiaohongshu-crawler-requirements.md)
- [爬虫实施计划](docs/plans/2026-04-17-001-feat-xiaohongshu-crawler-plan.md)
- [数据查看器需求文档](docs/brainstorms/2026-04-17-xiaohongshu-data-viewer-requirements.md)
- [数据查看器实施计划](docs/plans/2026-04-17-001-feat-xiaohongshu-data-viewer-plan.md)
