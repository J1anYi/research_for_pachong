#!/usr/bin/env python3
"""
Tavily搜索技能的Claude技能接口
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

# 导入main模块
from main import main as tavily_main

def run_skill(args):
    """
    运行Tavily搜索技能
    """
    # 解析输入参数
    # Claude技能会传递完整的查询字符串
    if not args:
        print("用法: /tavily-search [查询内容] [选项]")
        print("示例: /tavily-search 人工智能的最新发展")
        print("       /tavily-search 深度搜索 Python 3.13 新特性")
        return

    # 将参数转换为系统参数格式
    query = " ".join(args)
    sys.argv = ["tavily-search", query]

    try:
        tavily_main()
    except SystemExit:
        # main()可能会调用sys.exit()，这是正常的
        pass
    except Exception as e:
        print(f"技能执行错误: {e}")
        print("请使用 --help-full 查看完整帮助信息")

if __name__ == "__main__":
    # 命令行直接运行
    if len(sys.argv) > 1:
        run_skill(sys.argv[1:])
    else:
        # 交互模式
        print("🎯 Tavily搜索技能")
        print("=" * 50)
        print("输入搜索查询 (输入 'exit' 退出):")

        while True:
            try:
                query = input("\n搜索查询: ").strip()
                if query.lower() in ['exit', 'quit', 'q']:
                    break
                if query:
                    sys.argv = ["tavily-search", query]
                    tavily_main()
            except KeyboardInterrupt:
                print("\n退出")
                break
            except Exception as e:
                print(f"错误: {e}")