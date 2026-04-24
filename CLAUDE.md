# 行为准则

1.说中文

2.不要发送图片.glm-5是纯文本模型

3.浏览器操作用playwright-cli技能

4.**Phase 测试流程**：每次完成 phase 后，必须根据该 phase 内容制定测试文档，只有完成测试文档才能执行下一个 phase。完成测试文档后立即 push。需要浏览器交互时使用 `/playwright-cli` 技能。

5.**Context 管理**：当 context 快满的时候自动执行 `/compact` 命令来压缩上下文，保持对话流畅。

---

# 编码行为准则

用于减少常见LLM编码错误的行为指南。根据项目具体需求合并使用。

**权衡说明：** 这些准则偏向谨慎而非速度。对于简单任务，请自行判断。

## 1. 编码前先思考

**不要假设。不要隐藏困惑。暴露权衡。**

实现之前：
- 明确陈述你的假设。如果不确定，就问。
- 如果存在多种理解方式，把它们都列出来——不要默默选择。
- 如果有更简单的方法，就说出来。必要时提出反对意见。
- 如果有什么不清楚，就停下来。说出困惑的地方。然后问。

## 2. 简单优先

**用最少的代码解决问题。不做任何投机性的设计。**

- 不要添加未被要求的功能。
- 不要为一次性使用的代码创建抽象。
- 不要添加未被请求的"灵活性"或"可配置性"。
- 不要处理不可能发生的错误场景。
- 如果你写了200行代码，而50行就够了，那就重写。

问问自己："资深工程师会认为这太复杂了吗？"如果是，就简化。

## 3. 精准修改

**只修改必须修改的地方。只清理自己造成的混乱。**

编辑现有代码时：
- 不要"改进"相邻的代码、注释或格式。
- 不要重构没有问题的代码。
- 匹配现有风格，即使你会有不同的写法。
- 如果注意到无关的死代码，提出来——不要删除它。

当你的修改产生了孤立代码时：
- 删除你的修改导致不再使用的导入/变量/函数。
- 不要删除原本就存在的死代码，除非被要求。

检验标准：每一行修改都应该能直接追溯到用户的请求。

## 4. 目标驱动执行

**定义成功标准。循环验证直到达成。**

将任务转化为可验证的目标：
- "添加验证" → "为无效输入编写测试，然后让测试通过"
- "修复bug" → "编写能复现问题的测试，然后让测试通过"
- "重构X" → "确保重构前后测试都能通过"

对于多步骤任务，陈述简要计划：
```
1. [步骤] → 验证: [检查项]
2. [步骤] → 验证: [检查项]
3. [步骤] → 验证: [检查项]
```

强有力的成功标准让你可以独立循环验证。弱标准（"让它能用"）需要不断确认。

---

**这些准则有效的标志：** diff中不必要的变化更少，因过度复杂导致的重写更少，澄清问题在实现之前提出而非在犯错之后。

---

# MediaCrawler 项目

多平台社交媒体爬虫项目，支持小红书、抖音、B站、知乎等平台。

## 技术栈

- **后端**: Python + FastAPI + Uvicorn
- **前端**: 纯 HTML/CSS/JavaScript（无框架）
- **数据存储**: JSONL/JSON 文件
- **实时通信**: WebSocket
- **文件监控**: watchdog

## 常用命令

```bash
# 启动开发服务器（在 MediaCrawler 目录）
cd MediaCrawler
uv run uvicorn api.main:app --port 8080 --reload

# 或直接运行
uv run python -m api.main

# 访问地址
# API 文档: http://localhost:8080/docs
# 数据查看器: http://localhost:8080/viewer/
```

## 架构概览

```
MediaCrawler/
├── api/                      # FastAPI 后端
│   ├── main.py               # 应用入口，路由注册
│   ├── routers/              # API 路由
│   │   ├── notes.py          # 小红书笔记 API
│   │   ├── douyin.py         # 抖音 API
│   │   ├── bilibili.py       # B站 API
│   │   ├── zhihu.py          # 知乎 API
│   │   ├── websocket.py      # WebSocket 实时推送
│   │   └── crawler.py        # 爬虫控制 API
│   └── services/
│       └── file_watcher.py   # 文件变更监控服务
├── viewer/                   # 前端可视化界面
│   └── static/
│       ├── index.html        # 主页面
│       └── js/
│           ├── app.js        # 小红书模块
│           ├── douyin-app.js # 抖音模块
│           ├── bilibili-app.js # B站模块
│           ├── zhihu-app.js  # 知乎模块
│           ├── websocket-client.js # WebSocket 客户端
│           └── notifications.js # 实时通知组件
└── data/                     # 数据目录
    └── {platform}/
        ├── jsonl/            # JSONL 格式数据
        ├── json/             # JSON 格式数据
        └── images/           # 图片资源
```

## 数据流

1. **爬虫** → 写入 `data/{platform}/json/` 或 `jsonl/`
2. **file_watcher** → 监控文件变更 → 触发 WebSocket 推送
3. **viewer** → WebSocket 接收 → 更新 UI + 显示叶子式通知

## 支持的平台

| 平台 | 标识 | 数据目录 |
|------|------|----------|
| 小红书 | xhs | data/xhs/ |
| 抖音 | dy | data/dy/ |
| B站 | bili | data/bili/ |
| 知乎 | zhihu | data/zhihu/ |

## 开发规范

### Git 分支与 PR

- 分支命名: `feat/xxx`, `fix/xxx`, `refactor/xxx`
- 所有 PR 提交到 `main` 分支

### 代码风格

- **Python**: 4空格缩进, PEP 8, 类型注解必须
- **JavaScript**: 2空格缩进, ES6+, 使用 `window.xxx` 导出
- **CSS**: BEM 命名, 响应式优先

### 安全规范

1. 路径遍历防护: 所有文件路径用户输入必须验证
2. 使用 FastAPI Query/Path 验证器
3. 函数必须有返回类型注解

---

## 截图功能配置

当需要进行截图功能时，使用 **haiku** 模型（Kimi-2.5）以获得更好的视觉理解能力：

```bash
# 使用 haiku 模型进行截图相关操作
claude --model haiku
```

适用场景：
- UI 自动化测试截图分析
- 页面视觉验证
- 模态框/弹窗状态检查
- 前端布局问题排查

---

# currentDate
Today's date is 2026/04/21.
