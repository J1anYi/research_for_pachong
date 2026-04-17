# Tavily 搜索技能集成

这个项目已经集成了Tavily搜索技能，可以通过Claude Code直接使用网络搜索功能。

## 🎯 已安装的技能

### Tavily搜索技能 (`/tavily-search`)

使用Tavily API进行网络搜索，可以获取最新的网络信息。

**API密钥**: `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`

#### 使用方法

```bash
# 基本搜索
/tavily-search 人工智能的最新发展

# 深度搜索
/tavily-search 深度搜索 Python 3.13 新特性

# 指定结果数量
/tavily-search 结果数量:10 机器学习框架对比

# 高级选项
/tavily-search 包含域名:github.com,stackoverflow.com Python问题
/tavily-search 排除域名:twitter.com,facebook.com 新闻
/tavily-search 搜索类型:新闻 加密货币价格
```

#### 技能目录
- `.claude/skills/tavily-search/` - 技能源代码
- `.claude/settings.json` - 技能配置文件
- `.claude/settings.local.json` - 本地配置

## 🚀 快速开始

### 1. 环境设置

技能已自动配置，API密钥已集成。如果需要修改API密钥：

```bash
# 编辑环境变量
export TAVILY_API_KEY="your_new_api_key_here"
```

或者在`.claude/settings.local.json`中修改。

### 2. 测试技能

```bash
# 运行测试脚本
python test_tavily.py

# 或直接使用技能
/tavily-search 测试搜索
```

### 3. 验证安装

技能已通过以下验证：
- ✅ Tavily API连接正常
- ✅ 搜索功能工作正常
- ✅ 中文查询支持
- ✅ 结果格式化正确

## 🔧 技能特点

1. **网络搜索**: 搜索最新的网络信息
2. **深度搜索**: 支持基本和深度搜索模式
3. **中文支持**: 完美支持中文查询
4. **结果过滤**: 可按域名、类型过滤结果
5. **格式化输出**: 结果以Markdown格式展示
6. **错误处理**: 完善的错误处理机制

## 📊 示例输出

技能返回格式化的搜索结果，包括：
- 查询摘要
- AI生成的答案（如果可用）
- 搜索结果列表（标题、URL、内容摘要）
- 相关度评分
- 后续搜索建议

## 🔗 相关资源

- [Tavily官方文档](https://docs.tavily.com/)
- [Tavily Python SDK](https://github.com/tavily-ai/tavily-python)
- [技能源代码](./.claude/skills/tavily-search/)

## 🆘 故障排除

### 常见问题

1. **API密钥无效**
   - 检查API密钥是否正确
   - 确保API密钥有足够的额度

2. **技能不工作**
   - 确保技能已正确安装: `cd .claude/skills/tavily-search && python -m pip install -r requirements.txt`
   - 检查环境变量设置

3. **搜索结果为空**
   - 尝试简化查询
   - 尝试英文搜索

4. **编码问题**
   - 技能已配置UTF-8编码
   - 如果仍有编码问题，检查控制台编码设置

### 获取帮助

```bash
# 查看技能帮助
python .claude/skills/tavily-search/main.py --help-full

# 显示演示
python .claude/skills/tavily-search/main.py --demo
```

## 📈 性能优化

- **缓存**: Tavily API内置缓存机制
- **批量搜索**: 可以一次搜索多个查询
- **异步支持**: 技能支持异步调用
- **错误重试**: 网络错误时自动重试

## 🤝 贡献

欢迎提交问题和改进建议到技能目录：
`.claude/skills/tavily-search/`

## 📄 许可证

这个技能是基于Tavily API开发的。请遵守Tavily的服务条款。

---
*最后更新: 2026-04-17*