# Tavily搜索技能使用指南

## 🎯 安装已完成

Tavily搜索技能已经成功安装并配置完成！

## ✅ 已验证的功能

1. **API连接** - ✅ 工作正常（已使用你的API密钥测试）
2. **搜索功能** - ✅ 可以正常搜索并返回结果
3. **中文支持** - ✅ 支持中文查询
4. **技能集成** - ✅ 已配置为Claude Code技能

## 🚀 使用方法

你现在可以在Claude Code中直接使用Tavily搜索：

### 方式1: 使用技能命令
```bash
# 基本搜索
/tavily-search 人工智能的最新发展

# 深度搜索
/tavily-search 深度搜索 Python 3.13 新特性

# 更多结果
/tavily-search 结果数量:10 机器学习框架对比

# 特定域名搜索
/tavily-search 包含域名:github.com,stackoverflow.com Python问题
```

### 方式2: 命令行测试
```bash
# 运行测试脚本
python test_tavily.py

# 直接运行技能
cd .claude/skills/tavily-search
python main.py "搜索内容"
```

## 🔧 技能配置详情

- **技能名称**: `tavily-search`
- **技能路径**: `.claude/skills/tavily-search/`
- **API密钥**: `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`（已配置）
- **Python依赖**: `tavily-python>=0.7.0`

## 📁 文件结构

```
research_for_pachong/
├── .claude/
│   ├── settings.json              # 技能配置
│   ├── settings.local.json        # 本地配置（含API密钥）
│   └── skills/
│       └── tavily-search/
│           ├── main.py            # 主技能脚本
│           ├── run.py             # 技能接口
│           ├── config.json        # 技能配置
│           ├── requirements.txt   # 依赖
│           ├── setup.sh           # 安装脚本
│           ├── setup.bat          # Windows安装脚本
│           └── README.md          # 详细文档
├── CLAUDE.md                      # 项目说明
├── test_tavily.py                 # API测试脚本
└── venv/                          # Python虚拟环境
```

## 🧪 测试验证

我已经验证了以下功能：

1. **API连接测试** - 成功
2. **中文搜索测试** - 成功（搜索"人工智能的最新发展"返回了5个结果）
3. **技能调用测试** - 成功
4. **错误处理测试** - 正常工作

## 📊 示例输出

当你使用`/tavily-search 人工智能的最新发展`时，你会得到：

1. **查询摘要** - 显示搜索参数
2. **搜索结果** - 5个相关结果，每个包含：
   - 标题
   - URL
   - 相关性评分
   - 内容摘要
3. **搜索建议** - 如何改进搜索

## 🔗 相关链接

- [Tavily官方文档](https://docs.tavily.com/)
- [技能详细文档](./.claude/skills/tavily-search/README.md)

## 🆘 故障排除

### 如果技能不工作：

1. **检查Python依赖**
   ```bash
   cd .claude/skills/tavily-search
   pip install -r requirements.txt
   ```

2. **检查环境变量**
   ```bash
   echo $TAVILY_API_KEY
   # 应该是: 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
   ```

3. **运行API测试**
   ```bash
   python test_tavily.py
   ```

### 如果遇到编码问题：

技能已经配置了UTF-8编码支持。如果控制台显示乱码，可能是终端编码问题。

## 🎉 开始使用！

现在你可以直接在Claude Code中使用`/tavily-search`命令进行网络搜索了！

**示例**:
```
用户: 帮我搜索一下最新的Python 3.13特性
Claude: 我将使用Tavily搜索技能帮你搜索...

/tavily-search Python 3.13 新特性
```

**进阶用法**:
```
/tavily-search 深度搜索 机器学习的最新算法
/tavily-search 结果数量:8 前端框架对比
/tavily-search 包含域名:github.com,microsoft.com 开源项目
```

---
*安装完成时间: 2026-04-17*