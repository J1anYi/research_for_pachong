#!/usr/bin/env python3
"""
测试Tavily API是否工作正常
"""

import os
from tavily import TavilyClient

def test_tavily_api():
    # 使用你提供的API密钥
    api_key = "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"

    print("正在测试Tavily API连接...")

    try:
        # 创建Tavily客户端
        client = TavilyClient(api_key=api_key)

        # 测试一个简单的搜索
        print("执行简单搜索测试...")
        response = client.search("What is artificial intelligence?")

        print(f"搜索成功！返回了 {len(response.get('results', []))} 个结果")
        print(f"查询内容: {response.get('query', 'N/A')}")

        # 显示第一个结果
        if response.get('results'):
            first_result = response['results'][0]
            print("\n第一个搜索结果:")
            print(f"标题: {first_result.get('title', 'N/A')}")
            print(f"URL: {first_result.get('url', 'N/A')}")
            print(f"内容摘要: {first_result.get('content', 'N/A')[:200]}...")

        return True

    except Exception as e:
        print(f"API测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_tavily_api()
    if success:
        print("\nTavily API测试成功！API密钥有效。")
    else:
        print("\nTavily API测试失败。请检查API密钥或网络连接。")