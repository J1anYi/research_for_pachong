#!/usr/bin/env python3
"""
Tavily搜索技能的Python脚本
"""

import os
import sys
import json
import argparse
from pathlib import Path
from tavily import TavilyClient

# 设置默认编码为utf-8，避免Windows控制台编码问题
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class TavilySearchSkill:
    def __init__(self, api_key=None):
        """初始化Tavily搜索技能"""
        # 优先使用传入的API密钥，然后尝试从环境变量获取
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")

        if not self.api_key:
            print("错误: 未找到Tavily API密钥")
            print("请设置环境变量 TAVILY_API_KEY 或通过 --api-key 参数提供")
            sys.exit(1)

        self.client = TavilyClient(api_key=self.api_key)

    def search(self, query, max_results=5, search_depth="basic", include_images=False,
               include_answer=False, include_raw_content=False, include_domains=None,
               exclude_domains=None):
        """执行搜索"""

        # 解析查询中的选项
        options = self._parse_query_options(query)

        # 更新参数
        query_text = options.get("query", query)
        max_results = options.get("max_results", max_results)
        search_depth = options.get("search_depth", search_depth)
        include_domains = options.get("include_domains", include_domains)
        exclude_domains = options.get("exclude_domains", exclude_domains)

        try:
            # 准备搜索参数
            search_params = {
                "query": query_text,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_answer": include_answer,
                "include_raw_content": include_raw_content,
                "include_images": include_images
            }

            # 添加域名过滤器
            if include_domains:
                search_params["include_domains"] = include_domains
            if exclude_domains:
                search_params["exclude_domains"] = exclude_domains

            print(f"正在搜索: {query_text}")
            print(f"参数: {max_results}个结果, {search_depth}深度")

            # 执行搜索
            response = self.client.search(**search_params)

            # 格式化输出
            return self._format_response(response, query_text)

        except Exception as e:
            return self._format_error(str(e), query_text)

    def _parse_query_options(self, query):
        """解析查询字符串中的选项"""
        options = {
            "query": query,
            "max_results": 5,
            "search_depth": "basic",
            "include_domains": None,
            "exclude_domains": None
        }

        # 解析搜索深度
        if "深度搜索" in query or "详细搜索" in query:
            options["search_depth"] = "advanced"
            options["query"] = options["query"].replace("深度搜索", "").replace("详细搜索", "").strip()

        # 解析结果数量
        import re
        max_results_match = re.search(r'结果数量[:：]\s*(\d+)', query)
        if max_results_match:
            options["max_results"] = int(max_results_match.group(1))
            options["query"] = re.sub(r'结果数量[:：]\s*\d+', '', options["query"]).strip()

        # 解析搜索类型
        search_type_match = re.search(r'搜索类型[:：]\s*(\w+)', query)
        if search_type_match:
            search_type = search_type_match.group(1).lower()
            # 这里可以根据搜索类型调整参数
            if search_type in ["news", "新闻"]:
                options["query"] += " 最新新闻"

        # 解析包含域名
        include_match = re.search(r'包含域名[:：]\s*([\w\.,]+)', query)
        if include_match:
            domains = include_match.group(1).split(',')
            options["include_domains"] = [d.strip() for d in domains]
            options["query"] = re.sub(r'包含域名[:：]\s*[\w\.,]+', '', options["query"]).strip()

        # 解析排除域名
        exclude_match = re.search(r'排除域名[:：]\s*([\w\.,]+)', query)
        if exclude_match:
            domains = exclude_match.group(1).split(',')
            options["exclude_domains"] = [d.strip() for d in domains]
            options["query"] = re.sub(r'排除域名[:：]\s*[\w\.,]+', '', options["query"]).strip()

        return options

    def _format_response(self, response, query):
        """格式化搜索结果响应"""
        output = []

        # 标题
        output.append("**Tavily 搜索结果**")
        output.append(f"**查询**: {query}")
        output.append("")

        # 如果有答案
        if response.get("answer"):
            output.append("### AI 答案")
            output.append(response["answer"])
            output.append("")

        # 搜索信息
        output.append(f"**搜索结果数**: {len(response.get('results', []))}")
        if response.get("query"):
            output.append(f"**实际查询**: {response['query']}")
        output.append("")

        # 搜索结果列表
        if response.get("results"):
            output.append("### 搜索结果")
            for i, result in enumerate(response["results"], 1):
                output.append(f"#### {i}. {result.get('title', '无标题')}")
                output.append(f"**URL**: {result.get('url', '无URL')}")
                if result.get('score'):
                    output.append(f"**相关度**: {result['score']:.2f}")

                # 内容摘要
                content = result.get('content', '')
                if content:
                    # 截取前300个字符
                    preview = content[:300] + "..." if len(content) > 300 else content
                    output.append(f"**内容**: {preview}")

                output.append("")

        # 如果有图片
        if response.get("images"):
            output.append("### 相关图片")
            images = response.get("images", [])[:5]  # 最多显示5张
            for i, img_url in enumerate(images, 1):
                output.append(f"{i}. {img_url}")
            output.append("")

        # 后续建议
        output.append("### 后续搜索建议")
        output.append("1. 添加更多具体关键词以获得更精确的结果")
        output.append("2. 使用 `深度搜索` 获取更详细的信息")
        output.append("3. 指定 `结果数量:10` 查看更多结果")
        output.append("4. 添加 `搜索类型:新闻` 获取最新动态")

        return "\n".join(output)

    def _format_error(self, error_message, query):
        """格式化错误信息"""
        error_msg = f"""
❌ **Tavily 搜索失败**

**查询**: {query}
**错误信息**: {error_message}

**可能的原因**:
1. API密钥无效或已过期
2. 网络连接问题
3. 查询格式不正确
4. Tavily服务暂时不可用

**解决方法**:
1. 检查API密钥是否正确
2. 等待几分钟后重试
3. 简化查询内容
4. 联系Tavily支持

如需帮助，请使用 `/tavily-search-help` 命令。
"""
        return error_msg

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Tavily搜索技能")
    parser.add_argument("query", nargs="?", help="搜索查询内容")
    parser.add_argument("--api-key", help="Tavily API密钥")
    parser.add_argument("--max-results", type=int, default=5, help="最大结果数量")
    parser.add_argument("--depth", choices=["basic", "advanced"], default="basic", help="搜索深度")
    parser.add_argument("--include-images", action="store_true", help="包含图片")
    parser.add_argument("--include-answer", action="store_true", help="包含AI答案")
    parser.add_argument("--include-raw-content", action="store_true", help="包含原始内容")
    parser.add_argument("--include-domains", help="包含的域名（逗号分隔）")
    parser.add_argument("--exclude-domains", help="排除的域名（逗号分隔）")
    parser.add_argument("--demo", action="store_true", help="显示演示示例")
    parser.add_argument("--help-full", action="store_true", help="显示完整帮助")

    args = parser.parse_args()

    # 显示演示
    if args.demo:
        print("""
🎯 **Tavily 搜索演示**

**基本用法**:
1. `/tavily-search 人工智能的最新发展`
2. `/tavily-search Python 3.13 新特性`

**高级选项**:
1. `/tavily-search 深度搜索 气候变化的最新研究`
2. `/tavily-search 结果数量:10 OpenAI GPT-5`
3. `/tavily-search 包含域名:github.com,stackoverflow.com Python 问题`
4. `/tavily-search 搜索类型:新闻 加密货币价格`

**环境变量**:
设置 TAVILY_API_KEY 环境变量以自动使用API密钥
        """)
        return

    # 显示完整帮助
    if args.help_full:
        print("""
📚 **Tavily 搜索技能完整帮助**

**命令格式**:
`/tavily-search [查询内容] [选项]`

**可用选项（在查询中指定）**:
- `深度搜索` - 进行更深入的搜索，获取更详细的信息
- `结果数量:N` - 指定返回的结果数量（例如：结果数量:10）
- `搜索类型:类型` - 指定搜索类型（例如：搜索类型:新闻）
- `包含域名:domain1.com,domain2.com` - 只在指定域名中搜索
- `排除域名:domain1.com,domain2.com` - 排除指定域名的结果

**示例**:
1. `/tavily-search 最新的人工智能研究`
2. `/tavily-search 深度搜索 Python 3.13 性能改进`
3. `/tavily-search 结果数量:8 机器学习框架对比`
4. `/tavily-search 包含域名:github.com,gitlab.com 开源项目`
5. `/tavily-search 搜索类型:新闻 科技公司财报`

**API密钥**:
需要有效的Tavily API密钥。可以从 https://tavily.com/ 获取。

**环境变量**:
export TAVILY_API_KEY="your_api_key_here"

**更多信息**:
访问 https://docs.tavily.com/ 查看完整文档。
        """)
        return

    # 如果没有查询内容
    if not args.query:
        parser.print_help()
        print("\n💡 **提示**: 直接在命令中指定查询内容，例如: `/tavily-search 最新科技新闻`")
        return

    # 创建搜索技能实例
    skill = TavilySearchSkill(api_key=args.api_key)

    # 解析域名列表
    include_domains = args.include_domains.split(",") if args.include_domains else None
    exclude_domains = args.exclude_domains.split(",") if args.exclude_domains else None

    # 执行搜索
    result = skill.search(
        query=args.query,
        max_results=args.max_results,
        search_depth=args.depth,
        include_images=args.include_images,
        include_answer=args.include_answer,
        include_raw_content=args.include_raw_content,
        include_domains=include_domains,
        exclude_domains=exclude_domains
    )

    # 输出结果
    print(result)

if __name__ == "__main__":
    main()