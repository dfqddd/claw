#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mx_select_stock - 妙想智能选股技能
基于东方财富权威数据库，智能选股（行情指标、财务指标、板块成分等）
"""

import os
import sys
import json
import csv
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
API_URL = "https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen"
API_KEY = os.getenv("MX_APIKEY")

# 请求头
HEADERS = {
    "Content-Type": "application/json",
}


def select_stocks(keyword: str, page_no: int = 1, page_size: int = 20) -> dict:
    """
    智能选股
    
    Args:
        keyword: 选股条件（自然语言）
        page_no: 页码（默认 1）
        page_size: 每页数量（默认 20）
    
    Returns:
        API 响应字典
    """
    if not API_KEY:
        print("❌ 错误：未找到 API Key")
        print("   请配置环境变量 MX_APIKEY")
        print("   方法：在 ~/.openclaw/workspace-hanli/skills/mx_select_stock/.env 文件中添加")
        print("   格式：MX_APIKEY=your_api_key_here")
        sys.exit(1)
    
    headers = HEADERS.copy()
    headers["apikey"] = API_KEY
    
    data = {
        "keyword": keyword,
        "pageNo": page_no,
        "pageSize": page_size
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败：{e}")
        sys.exit(1)


def parse_markdown_table(md_table: str) -> tuple:
    """
    解析 Markdown 表格
    
    Args:
        md_table: Markdown 格式表格字符串
    
    Returns:
        (headers, rows) 元组
    """
    lines = md_table.strip().split('\n')
    headers = []
    rows = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('|---'):
            continue
        
        # 解析表格行
        cells = [cell.strip() for cell in line.split('|')]
        cells = [c for c in cells if c]  # 移除空单元格
        
        if not headers:
            headers = cells
        else:
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
    
    return headers, rows


def format_output(result: dict, query: str = "") -> str:
    """
    格式化输出结果
    
    Args:
        result: API 响应字典
        query: 查询语句
    
    Returns:
        格式化文本
    """
    output_lines = []
    output_lines.append("=" * 70)
    output_lines.append(f"妙想智能选股结果")
    output_lines.append(f"查询：{query}")
    output_lines.append(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("=" * 70)
    output_lines.append("")
    
    # 检查状态
    status = result.get('status', -1)
    message = result.get('message', 'unknown')
    
    if status != 0 or message != 'ok':
        output_lines.append(f"❌ 接口返回错误：{message}")
        output_lines.append("")
        return "\n".join(output_lines)
    
    # 解析数据 - 适配实际 API 返回结构
    data_data = result.get('data', {}).get('data', {})
    
    # 尝试从 partialResults 解析 Markdown 表格
    partial_results = data_data.get('partialResults', '')
    
    # 获取统计信息
    security_count = data_data.get('securityCount', 0)
    total_condition = data_data.get('totalCondition', '')
    condition_list = data_data.get('responseConditionList', [])
    
    if not partial_results:
        output_lines.append("⚠️  未找到符合条件的股票")
        output_lines.append("")
        output_lines.append("💡 建议：")
        output_lines.append("   1. 检查选股条件是否清晰")
        output_lines.append("   2. 尝试更宽松的条件")
        output_lines.append("   3. 到东方财富妙想 AI 选股：https://mkapi2.dfcfs.com/")
        output_lines.append("")
        return "\n".join(output_lines)
    
    # 统计信息
    output_lines.append(f"📊 总结果：{security_count} 只股票")
    output_lines.append("")
    
    # 选股条件
    if total_condition:
        output_lines.append(f"📋 选股条件：{total_condition}")
        output_lines.append("")
    
    # 条件统计
    if condition_list:
        output_lines.append("📈 条件匹配统计：")
        for cond in condition_list:
            describe = cond.get('describe', '')
            count = cond.get('stockCount', 0)
            output_lines.append(f"   - {describe}: {count} 只")
        output_lines.append("")
    
    # 解析 Markdown 表格
    headers, rows = parse_markdown_table(partial_results)
    
    if not rows:
        output_lines.append("⚠️  解析数据失败")
        output_lines.append("")
        return "\n".join(output_lines)
    
    # 选股条件
    if total_condition:
        output_lines.append(f"📋 选股条件：{total_condition}")
        output_lines.append("")
    
    # 条件统计
    if condition_list:
        output_lines.append("📈 条件匹配统计：")
        for cond in condition_list:
            describe = cond.get('describe', '')
            count = cond.get('stockCount', 0)
            output_lines.append(f"   - {describe}: {count} 只")
        output_lines.append("")
    
    # 输出表格
    if headers and rows:
        # 只显示部分列（避免太宽）
        display_headers = headers[:8] if len(headers) > 8 else headers
        
        # 计算列宽
        col_widths = []
        for header in display_headers:
            max_width = len(header)
            for row in rows:
                value = str(row.get(header, ''))
                max_width = max(max_width, len(value))
            col_widths.append(min(max_width + 2, 25))  # 限制最大宽度
        
        # 输出表头
        header_line = "│".join([h.ljust(col_widths[i]) for i, h in enumerate(display_headers)])
        separator = "┼".join(["─" * w for w in col_widths])
        
        output_lines.append("┌" + "┬".join(["─" * w for w in col_widths]) + "┐")
        output_lines.append("│" + header_line + "│")
        output_lines.append("├" + separator + "┤")
        
        # 输出数据行
        for row in rows:
            row_values = [str(row.get(h, '')) for h in display_headers]
            row_line = "│".join([row_values[i].ljust(col_widths[i]) for i in range(len(display_headers))])
            output_lines.append("│" + row_line + "│")
        
        output_lines.append("└" + "┴".join(["─" * w for w in col_widths]) + "┘")
    
    output_lines.append("")
    output_lines.append("=" * 70)
    output_lines.append(f"显示 {len(rows)} 条结果（共 {security_count} 条）")
    output_lines.append("=" * 70)
    
    return "\n".join(output_lines)


def save_to_csv(rows: list, output_path: str):
    """
    保存结果到 CSV 文件
    
    Args:
        rows: 数据行列表
        output_path: 文件路径
    """
    try:
        if not rows:
            print("⚠️  无数据可保存")
            return
        
        # 使用第一行的键作为字段名
        fieldnames = list(rows[0].keys())
        
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ 数据已保存到：{output_path}")
        print(f"   列数：{len(fieldnames)}")
        print(f"   行数：{len(rows)}")
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
    result = select_stocks("今日涨停的股票", page_no=1, page_size=5)
    
    if result:
        status = result.get('status', -1)
        message = result.get('message', 'unknown')
        
        if status == 0 and message == 'ok':
            print("\n✅ API 连接成功！")
            total = result.get('data', {}).get('data', {}).get('result', {}).get('total', 0)
            print(f"   返回结果数：{total}")
        else:
            print(f"\n⚠️  API 返回状态：{message}")
    else:
        print("\n❌ API 连接失败")
        sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="妙想智能选股技能")
    parser.add_argument("--query", "-q", type=str, help="选股条件（自然语言）")
    parser.add_argument("--page", "-p", type=int, default=1, help="页码（默认 1）")
    parser.add_argument("--size", "-s", type=int, default=20, help="每页数量（默认 20）")
    parser.add_argument("--output", "-o", type=str, help="保存结果到 CSV 文件")
    parser.add_argument("--test", action="store_true", help="测试 API 连接")
    
    args = parser.parse_args()
    
    # 测试模式
    if args.test:
        test_api()
        return
    
    # 查询模式
    if not args.query:
        parser.print_help()
        print("\n❌ 错误：请提供选股条件 (--query)")
        print("\n示例:")
        print("  python3 mx_select_stock.py --query '今日涨幅大于 5% 的股票'")
        print("  python3 mx_select_stock.py --query '电力板块成分股'")
        print("  python3 mx_select_stock.py --query '市盈率小于 20 的股票' --page 1 --size 10")
        print("  python3 mx_select_stock.py --query '涨停股票' --output stocks.csv")
        sys.exit(1)
    
    # 执行选股
    print(f"🔍 选股：{args.query}")
    print(f"页码：{args.page} | 每页：{args.size} 条")
    print("")
    
    result = select_stocks(args.query, args.page, args.size)
    
    # 格式化输出
    output = format_output(result, args.query)
    print(output)
    
    # 保存到 CSV
    if args.output:
        data_data = result.get('data', {}).get('data', {})
        partial_results = data_data.get('partialResults', '')
        _, rows = parse_markdown_table(partial_results)
        save_to_csv(rows, args.output)


if __name__ == "__main__":
    main()
