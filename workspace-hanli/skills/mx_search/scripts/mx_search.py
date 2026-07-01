#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mx_search - 妙想资讯搜索技能
基于东方财富妙想搜索 API，获取金融资讯（新闻、公告、研报、政策等）
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# 加载环境变量
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass

# API 配置
API_URL = "https://mkapi2.dfcfs.com/finskillshub/api/claw/news-search"
API_KEY = os.getenv("MX_APIKEY")

# 请求头
HEADERS = {
    "Content-Type": "application/json",
}


def search_news(query: str, limit: int = 10) -> dict:
    """
    搜索金融资讯
    
    Args:
        query: 搜索关键词
        limit: 返回结果数量（默认 10）
    
    Returns:
        API 响应字典
    """
    if not API_KEY:
        print("❌ 错误：未找到 API Key")
        print("   请配置环境变量 MX_APIKEY")
        print("   方法：在 ~/.openclaw/workspace-hanli/skills/mx_search/.env 文件中添加")
        print("   格式：MX_APIKEY=your_api_key_here")
        sys.exit(1)
    
    headers = HEADERS.copy()
    headers["apikey"] = API_KEY
    
    data = {
        "query": query,
        "limit": limit
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败：{e}")
        sys.exit(1)


def format_output(result: dict, query: str = "") -> str:
    """
    格式化输出结果
    
    Args:
        result: API 响应字典
        query: 搜索关键词
    
    Returns:
        格式化文本
    """
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append(f"妙想资讯搜索结果")
    output_lines.append(f"查询：{query}")
    output_lines.append(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("=" * 60)
    output_lines.append("")
    
    # 解析结果 - 适配实际 API 返回结构
    # 结构：data.data.llmSearchResponse.data
    news_list = []
    try:
        news_list = result.get('data', {}).get('data', {}).get('llmSearchResponse', {}).get('data', [])
    except Exception:
        news_list = []
    
    if not news_list:
        output_lines.append("⚠️  未找到相关资讯")
        output_lines.append("")
        return "\n".join(output_lines)
    
    for idx, news in enumerate(news_list, 1):
        title = news.get('title', '无标题')
        content = news.get('content', '无摘要')
        source = news.get('source', news.get('insName', '未知来源'))
        publish_time = news.get('date', '未知时间')
        info_type = news.get('informationType', '')
        jump_url = news.get('jumpUrl', '')
        
        output_lines.append(f"[{idx}] {title}")
        
        # 信息类型
        type_map = {
            'NEWS': '新闻',
            'NOTICE': '公告',
            'REPORT': '研报',
            'INV_NEWS': '资讯',
            'AN': '公告'
        }
        if info_type:
            output_lines.append(f"    类型：{type_map.get(info_type, info_type)}")
        
        # 来源和时间
        output_lines.append(f"    来源：{source} | 时间：{publish_time}")
        
        # 摘要（截断过长内容）
        if content:
            # 清理多余空白
            content = ' '.join(content.split())
            if len(content) > 300:
                content = content[:300] + "..."
            output_lines.append(f"    摘要：{content}")
        
        # 链接
        if jump_url:
            output_lines.append(f"    链接：{jump_url}")
        
        output_lines.append("-" * 60)
        output_lines.append("")
    
    output_lines.append("=" * 60)
    output_lines.append(f"共找到 {len(news_list)} 条资讯")
    output_lines.append("=" * 60)
    
    return "\n".join(output_lines)


def save_to_file(content: str, output_path: str):
    """
    保存结果到文件
    
    Args:
        content: 要保存的内容
        output_path: 文件路径
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 结果已保存到：{output_path}")
    except Exception as e:
        print(f"❌ 保存失败：{e}")


def test_api():
    """
    测试 API 连接
    """
    print("🔍 测试 API 连接...")
    print(f"API URL: {API_URL}")
    print(f"API Key: {'已配置' if API_KEY else '❌ 未配置'}")
    
    if not API_KEY:
        print("\n❌ 请先配置 API Key")
        sys.exit(1)
    
    # 简单测试查询
    result = search_news("A 股", limit=1)
    
    if result:
        print("\n✅ API 连接成功！")
        print(f"   返回结果数：{len(result.get('result', []))}")
    else:
        print("\n❌ API 连接失败")
        sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="妙想资讯搜索技能")
    parser.add_argument("--query", "-q", type=str, help="搜索关键词")
    parser.add_argument("--limit", "-l", type=int, default=10, help="返回结果数量（默认 10）")
    parser.add_argument("--output", "-o", type=str, help="保存结果到文件")
    parser.add_argument("--test", action="store_true", help="测试 API 连接")
    
    args = parser.parse_args()
    
    # 测试模式
    if args.test:
        test_api()
        return
    
    # 查询模式
    if not args.query:
        parser.print_help()
        print("\n❌ 错误：请提供搜索关键词 (--query)")
        print("\n示例:")
        print("  python3 mx_search.py --query '立讯精密最新研报'")
        print("  python3 mx_search.py --query '电力板块新闻' --limit 5")
        print("  python3 mx_search.py --query '北向资金' --output news.md")
        sys.exit(1)
    
    # 执行搜索
    print(f"🔍 搜索：{args.query}")
    print(f"限制：{args.limit} 条结果")
    print("")
    
    result = search_news(args.query, args.limit)
    
    # 格式化输出
    output = format_output(result, args.query)
    print(output)
    
    # 保存到文件
    if args.output:
        save_to_file(output, args.output)


if __name__ == "__main__":
    main()
