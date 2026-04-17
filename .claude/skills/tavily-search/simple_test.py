#!/usr/bin/env python3
"""
简化的Tavily搜索测试脚本（无表情符号，避免编码问题）
"""

import os
import sys

# 设置API密钥
os.environ["TAVILY_API_KEY"] = "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"

# 导入主模块
from main import TavilySearchSkill

def main():
    """主测试函数"""
    if len(sys.argv) < 2:
        print("使用方法: python simple_test.py [查询内容]")
        print("示例: python simple_test.py '人工智能的最新发展'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    print("=" * 60)
    print(f"测试查询: {query}")
    print("=" * 60)

    try:
        # 创建搜索技能实例
        skill = TavilySearchSkill()

        # 执行搜索
        result = skill.search(query)

        # 输出结果（无表情符号）
        print(result)

    except Exception as e:
        print(f"搜索失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()