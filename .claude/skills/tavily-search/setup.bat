@echo off
rem Tavily搜索技能安装脚本 (Windows版本)

echo 📦 正在安装Tavily搜索技能...

rem 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    exit /b 1
)

rem 检查是否在虚拟环境中
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  不在虚拟环境中，建议在虚拟环境中安装
    set /p CONTINUE=是否继续安装？(y/N):
    if /i not "%CONTINUE%"=="y" (
        echo 安装已取消
        exit /b 0
    )
)

rem 安装依赖
echo 📥 安装Python依赖...
pip install -r requirements.txt

rem 创建.env文件（如果不存在）
if not exist ".env" (
    echo 🔑 创建.env文件...
    (
        echo # Tavily API密钥
        echo TAVILY_API_KEY=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
        echo.
        echo # 其他配置选项
        echo # TAVILY_MAX_RESULTS=5
        echo # TAVILY_SEARCH_DEPTH=basic
    ) > .env
    echo ✅ 已创建.env文件
) else (
    echo ✅ .env文件已存在
)

rem 创建测试脚本
echo 🧪 创建测试脚本...
(
    echo #!/usr/bin/env python3
    echo """
    echo 测试Tavily搜索技能
    echo """
    echo.
    echo import os
    echo import sys
    echo from pathlib import Path
    echo.
    echo # 添加技能目录到路径
    echo skill_dir = Path(__file__).parent / "tavily-search"
    echo sys.path.insert^0, str(skill_dir^)
    echo.
    echo # 导入main模块
    echo exec^(open^(skill_dir / "main.py"^).read^(^)^)
    echo.
    echo if __name__ == "__main__":
    echo     # 测试命令参数
    echo     sys.argv = ["test", "人工智能的最新发展"]
    echo.
    echo     print^("测试Tavily搜索技能..."^)
    echo     print^("=" * 50^)
    echo.
    echo     try:
    echo         exec^(open^(skill_dir / "main.py"^).read^(^), {"__name__": "__main__"}^)
    echo         print^("✅ 测试完成！"^)
    echo     except Exception as e:
    echo         print^(f"❌ 测试失败: {e}"^)
) > test_skill.py

echo.
echo 🎉 Tavily搜索技能安装完成！
echo.
echo 📝 使用方法:
echo 1. 设置环境变量: set TAVILY_API_KEY=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
echo 2. 运行测试: python test_skill.py
echo 3. 在Claude Code中使用: /tavily-search [查询内容]
echo.
echo 🔧 示例命令:
echo   /tavily-search 人工智能的最新发展
echo   /tavily-search 深度搜索 Python 3.13 新特性
echo   /tavily-search 结果数量:10 机器学习框架对比
echo.
echo 📚 更多信息请运行: python main.py --help-full

pause