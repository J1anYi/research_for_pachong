@echo off
rem 激活Tavily搜索环境 (Windows版本)

echo 🔧 激活Tavily搜索环境...

rem 设置环境变量
set TAVILY_API_KEY=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
echo ✅ API密钥已设置: %TAVILY_API_KEY%

rem 检查Python虚拟环境
if exist venv (
    echo 🐍 检测到Python虚拟环境
    if "%VIRTUAL_ENV%"=="" (
        echo 📥 激活虚拟环境...
        call venv\Scripts\activate
        echo ✅ 虚拟环境已激活
    ) else (
        echo ✅ 已在虚拟环境中
    )
) else (
    echo ⚠️  未找到虚拟环境，将使用系统Python
)

rem 检查依赖
echo 📦 检查Python依赖...
python -c "import tavily" >nul 2>&1
if errorlevel 1 (
    echo 📥 正在安装Tavily Python SDK...
    pip install tavily-python
    echo ✅ Tavily Python SDK安装完成
) else (
    echo ✅ Tavily Python SDK已安装
)

rem 测试API连接
echo 🔌 测试Tavily API连接...
python -c "
import os
from tavily import TavilyClient

api_key = os.getenv('TAVILY_API_KEY')
if not api_key:
    print('❌ 错误: 未找到API密钥')
    exit(1)

try:
    client = TavilyClient(api_key=api_key)
    response = client.search('test', max_results=1)
    print('✅ API连接成功! Tavily服务正常。')
except Exception as e:
    print(f'❌ API连接失败: {e}')
"

echo.
echo 🎉 Tavily搜索环境激活完成！
echo.
echo 📝 使用方法:
echo   在Claude Code中使用: /tavily-search [查询内容]
echo   示例: /tavily-search "人工智能的最新发展"
echo.
echo 🔧 高级用法:
echo   /tavily-search 深度搜索 Python 3.13 新特性
echo   /tavily-search 结果数量:10 机器学习框架对比
echo   /tavily-search 包含域名:github.com,stackoverflow.com Python问题
echo.
echo 💡 提示: 这个脚本只需要运行一次。API密钥已保存在配置文件中。

pause