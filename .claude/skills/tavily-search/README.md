# Tavily 搜索技能

这是一个Claude Code技能，用于通过Tavily API进行网络搜索。

## 📋 功能特性

- 🔍 **网络搜索**：搜索最新的网络信息
- 🎯 **深度搜索**：支持基本搜索和深度搜索模式
- 🔧 **高级选项**：可指定结果数量、搜索类型、域名过滤等
- 📄 **格式化输出**：结果以Markdown格式展示，便于阅读
- 🔄 **多语言支持**：支持中文和英文搜索

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- Tavily API密钥（已提供：`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`）

### 2. 安装

```bash
# 进入技能目录
cd .claude/skills/tavily-search

# 运行安装脚本（Linux/Mac）
./setup.sh

# 或者运行安装脚本（Windows）
setup.bat

# 或者手动安装
pip install -r requirements.txt
```

### 3. 设置环境变量

```bash
# Linux/Mac
export TAVILY_API_KEY="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"

# Windows (命令提示符)
set TAVILY_API_KEY=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

# Windows (PowerShell)
$env:TAVILY_API_KEY="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"
```

或者创建 `.env` 文件（已自动创建）：
```env
TAVILY_API_KEY=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
```

## 🎮 使用方法

### 在Claude Code中使用

```bash
# 基本搜索
/tavily-search 人工智能的最新发展

# 深度搜索
/tavily-search 深度搜索 Python 3.13 新特性

# 指定结果数量
/tavily-search 结果数量:10 机器学习框架对比

# 包含特定域名
/tavily-search 包含域名:github.com,stackoverflow.com Python问题

# 排除特定域名
/tavily-search 排除域名:twitter.com,facebook.com 新闻

# 搜索新闻
/tavily-search 搜索类型:新闻 加密货币价格
```

### 命令行使用

```bash
# 基本搜索
python main.py "人工智能的最新发展"

# 高级选项
python main.py "深度搜索 Python 3.13" --depth advanced --max-results 10

# 显示演示
python main.py --demo

# 显示完整帮助
python main.py --help-full
```

## 🔧 高级选项

### 查询中可用的选项

可以直接在查询字符串中指定选项：

1. **深度搜索** - 进行更深入的搜索
   ```
   /tavily-search 深度搜索 气候变化的最新研究
   ```

2. **结果数量:N** - 指定返回结果数量
   ```
   /tavily-search 结果数量:8 机器学习框架对比
   ```

3. **搜索类型:类型** - 指定搜索类型
   ```
   /tavily-search 搜索类型:新闻 科技公司财报
   ```

4. **包含域名:domain1.com,domain2.com** - 只搜索指定域名
   ```
   /tavily-search 包含域名:github.com,gitlab.com 开源项目
   ```

5. **排除域名:domain1.com,domain2.com** - 排除指定域名
   ```
   /tavily-search 排除域名:twitter.com,facebook.com 最新消息
   ```

### 命令行参数

```bash
# 完整的命令行选项
python main.py --help

# 可用参数：
# --api-key           API密钥
# --max-results       最大结果数量（默认：5）
# --depth             搜索深度（basic/advanced，默认：basic）
# --include-images    包含图片
# --include-answer    包含AI答案
# --include-raw-content 包含原始内容
# --include-domains   包含的域名（逗号分隔）
# --exclude-domains   排除的域名（逗号分隔）
```

## 📊 输出格式

搜索结果以以下格式呈现：

```
🔍 **Tavily 搜索结果**

**查询**: 人工智能的最新发展

### 💡 AI 答案
[如果有AI生成的答案会显示在这里]

**搜索结果数**: 5

### 📄 搜索结果

#### 1. 标题1
**URL**: https://example.com
**相关度**: 0.92
**内容**: 内容摘要...

#### 2. 标题2
**URL**: https://example2.com
**相关度**: 0.87
**内容**: 内容摘要...

### 🖼️ 相关图片
1. https://example.com/image1.jpg
2. https://example.com/image2.jpg

### 💭 后续搜索建议
1. 添加更多具体关键词以获得更精确的结果
2. 使用 `深度搜索` 获取更详细的信息
3. 指定 `结果数量:10` 查看更多结果
4. 添加 `搜索类型:新闻` 获取最新动态
```

## 🧪 测试

### 运行测试脚本

```bash
python test_skill.py
```

### 手动测试API

```bash
python test_tavily.py
```

## 🔗 相关资源

- [Tavily官方文档](https://docs.tavily.com/)
- [Tavily Python SDK](https://github.com/tavily-ai/tavily-python)
- [获取Tavily API密钥](https://app.tavily.com/)

## 📄 许可证

这个技能是基于Tavily API开发的。请遵守Tavily的服务条款。

## 🤝 贡献

欢迎提交问题和改进建议！

## 🐛 故障排除

### 常见问题

1. **API密钥无效**
   - 检查API密钥是否正确
   - 确保API密钥有足够的额度

2. **网络连接问题**
   - 检查网络连接
   - 尝试使用代理

3. **Python包安装失败**
   - 确保Python版本符合要求
   - 尝试使用虚拟环境

4. **搜索结果为空**
   - 尝试简化查询
   - 尝试英文搜索

### 获取帮助

```bash
# 显示帮助
python main.py --help-full

# 显示演示
python main.py --demo
```

## 📈 更新日志

### v1.0.0 (2026-04-17)
- 初始版本发布
- 支持基本搜索功能
- 支持高级搜索选项
- 提供完整的文档和示例