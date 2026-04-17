#!/usr/bin/env bash
# Tavily搜索技能安装脚本

set -e

echo "📦 正在安装Tavily搜索技能..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

# 检查是否在虚拟环境中
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  不在虚拟环境中，建议在虚拟环境中安装"
    read -p "是否继续安装？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "安装已取消"
        exit 0
    fi
fi

# 安装依赖
echo "📥 安装Python依赖..."
pip install -r requirements.txt

# 创建.env文件（如果不存在）
if [[ ! -f ".env" ]]; then
    echo "🔑 创建.env文件..."
    cat > .env << EOF
# Tavily API密钥
TAVILY_API_KEY=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

# 其他配置选项
# TAVILY_MAX_RESULTS=5
# TAVILY_SEARCH_DEPTH=basic
EOF
    echo "✅ 已创建.env文件"
else
    echo "✅ .env文件已存在"
fi

# 设置脚本权限
echo "🔧 设置执行权限..."
chmod +x main.py

# 创建测试脚本
echo "🧪 创建测试脚本..."
cat > test_skill.py << 'EOF'
#!/usr/bin/env python3
"""
测试Tavily搜索技能
"""

import os
import sys
from pathlib import Path

# 添加技能目录到路径
skill_dir = Path(__file__).parent / "tavily-search"
sys.path.insert(0, str(skill_dir))

# 导入main模块
exec(open(skill_dir / "main.py").read())

if __name__ == "__main__":
    # 测试命令参数
    sys.argv = ["test", "人工智能的最新发展"]

    print("测试Tavily搜索技能...")
    print("=" * 50)

    try:
        exec(open(skill_dir / "main.py").read(), {"__name__": "__main__"})
        print("✅ 测试完成！")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
EOF

chmod +x test_skill.py

echo ""
echo "🎉 Tavily搜索技能安装完成！"
echo ""
echo "📝 使用方法:"
echo "1. 设置环境变量: export TAVILY_API_KEY='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'"
echo "2. 运行测试: python test_skill.py"
echo "3. 在Claude Code中使用: /tavily-search [查询内容]"
echo ""
echo "🔧 示例命令:"
echo "  /tavily-search 人工智能的最新发展"
echo "  /tavily-search 深度搜索 Python 3.13 新特性"
echo "  /tavily-search 结果数量:10 机器学习框架对比"
echo ""
echo "📚 更多信息请运行: python main.py --help-full"