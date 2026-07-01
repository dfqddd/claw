#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mx_selfselect - 妙想自选股管理技能
基于东方财富通行证账户数据，管理自选股（查询、添加、删除）
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
API_URL_QUERY = "https://mkapi2.dfcfs.com/finskillshub/api/claw/self-select/get"
API_URL_MANAGE = "https://mkapi2.dfcfs.com/finskillshub/api/claw/self-select/manage"
API_KEY = os.getenv("MX_APIKEY")

# 请求头
HEADERS = {
    "Content-Type": "application/json",
}


def query_self_stocks() -> dict:
    """
    查询自选股列表
    
    Returns:
        API 响应字典
    """
    if not API_KEY:
        print("❌ 错误：未找到 API Key")
        print("   请配置环境变量 MX_APIKEY")
        sys.exit(1)
    
    headers = HEADERS.copy()
    headers["apikey"] = API_KEY
    
    try:
        response = requests.post(API_URL_QUERY, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败：{e}")
        sys.exit(1)


def manage_self_stocks(query: str) -> dict:
    """
    添加/删除自选股
    
    Args:
        query: 操作指令（如"把贵州茅台加入自选"）
    
    Returns:
        API 响应字典
    """
    if not API_KEY:
        print("❌ 错误：未找到 API Key")
        print("   请配置环境变量 MX_APIKEY")
        sys.exit(1)
    
    headers = HEADERS.copy()
    headers["apikey"] = API_KEY
    
    data = {
        "query": query
    }
    
    try:
        response = requests.post(API_URL_MANAGE, headers=headers, json=data, timeout=30)
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


def parse_stock_data(result: dict) -> tuple:
    """
    解析自选股数据
    
    Args:
        result: API 响应字典
    
    Returns:
        (headers, rows) 元组
    """
    headers = []
    rows = []
    
    try:
        # 尝试从 partialResults 解析 Markdown 表格
        partial_results = result.get('data', {}).get('partialResults', '')
        
        if partial_results:
            headers, rows = parse_markdown_table(partial_results)
    except Exception as e:
        print(f"⚠️  解析数据失败：{e}")
    
    return headers, rows


def format_query_output(result: dict) -> str:
    """
    格式化查询结果输出
    
    Args:
        result: API 响应字典
    
    Returns:
        格式化文本
    """
    output_lines = []
    output_lines.append("=" * 70)
    output_lines.append(f"我的自选股列表")
    output_lines.append(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("=" * 70)
    output_lines.append("")
    
    # 检查状态
    status = result.get('status', -1)
    message = result.get('message', 'unknown')
    
    # 获取自选股数量
    security_count = result.get('data', {}).get('securityCount', 0)
    
    if status != 0:
        output_lines.append(f"❌ 查询失败：{message}")
        output_lines.append("")
        return "\n".join(output_lines)
    
    # 解析数据
    headers, rows = parse_stock_data(result)
    
    if not rows:
        output_lines.append("📭 自选股列表为空")
        output_lines.append("")
        output_lines.append("💡 使用以下命令添加股票：")
        output_lines.append("   python3 mx_selfselect.py --action add --query '贵州茅台'")
        output_lines.append("")
        return "\n".join(output_lines)
    
    output_lines.append(f"📊 共 {security_count} 只股票")
    output_lines.append("")
    
    # 只显示关键字段（避免太宽）
    key_fields = ['代码', '名称', '市场代码简称', '最新价 (元)(2026.03.16)', '涨跌幅 (%)(2026.03.16)', '涨跌额 (元)(2026.03.16)']
    display_headers = []
    for field in key_fields:
        # 尝试精确匹配
        if field in headers:
            display_headers.append(field)
        else:
            # 尝试模糊匹配（去掉日期后缀）
            for h in headers:
                if field.split('(')[0].strip() in h or h.split('(')[0].strip() in field:
                    display_headers.append(h)
                    break
    
    if not display_headers:
        display_headers = headers[:8] if len(headers) > 8 else headers
    
    # 输出表格
    if display_headers and rows:
        # 计算列宽
        col_widths = []
        for header in display_headers:
            max_width = len(header)
            for row in rows:
                value = str(row.get(header, ''))
                max_width = max(max_width, len(value))
            col_widths.append(min(max_width + 2, 20))
        
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
    return "\n".join(output_lines)


def format_manage_output(result: dict, action: str, query: str) -> str:
    """
    格式化操作结果输出
    
    Args:
        result: API 响应字典
        action: 操作类型（add/remove）
        query: 操作指令
    
    Returns:
        格式化文本
    """
    output_lines = []
    output_lines.append("=" * 70)
    output_lines.append(f"自选股操作结果")
    output_lines.append(f"操作：{'添加' if action == 'add' else '删除'}")
    output_lines.append(f"指令：{query}")
    output_lines.append(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("=" * 70)
    output_lines.append("")
    
    # 检查状态
    status = result.get('status', -1)
    message = result.get('message', 'unknown')
    
    if status != 0 or message != 'ok':
        output_lines.append(f"❌ 操作失败：{message}")
        output_lines.append("")
        return "\n".join(output_lines)
    
    # 检查操作结果
    data = result.get('data', {})
    success = data.get('success', False)
    msg = data.get('message', '操作成功')
    
    if success:
        output_lines.append(f"✅ 操作成功！")
        output_lines.append(f"   {msg}")
    else:
        output_lines.append(f"⚠️  操作结果：{msg}")
    
    output_lines.append("")
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
        
        fieldnames = list(rows[0].keys())
        
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ 数据已保存到：{output_path}")
        print(f"   行数：{len(rows)}")
    except Exception as e:
        print(f"❌ 保存失败：{e}")


def test_api():
    """
    测试 API 连接
    """
    print("🔍 测试 API 连接...")
    print(f"API Key: {'已配置' if API_KEY else '❌ 未配置'}")
    
    if not API_KEY:
        print("\n❌ 请先配置 API Key")
        sys.exit(1)
    
    # 测试查询接口
    print("\n1. 测试查询接口...")
    result = query_self_stocks()
    
    if result:
        status = result.get('status', -1)
        message = result.get('message', 'unknown')
        
        if status == 0 and message == 'ok':
            print("   ✅ 查询接口正常")
            rows = parse_stock_data(result)[1]
            print(f"   自选股数量：{len(rows)}")
        else:
            print(f"   ⚠️  查询接口返回：{message}")
    else:
        print("   ❌ 查询接口失败")
    
    print("\n✅ API 连接测试完成！")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="妙想自选股管理技能")
    parser.add_argument("--action", "-a", type=str,
                       choices=['query', 'add', 'remove'],
                       help="操作类型：query(查询) / add(添加) / remove(删除)")
    parser.add_argument("--query", "-q", type=str, help="操作指令（添加/删除时需要）")
    parser.add_argument("--output", "-o", type=str, help="保存结果到 CSV 文件（查询时使用）")
    parser.add_argument("--test", action="store_true", help="测试 API 连接")
    
    args = parser.parse_args()
    
    # 测试模式
    if args.test:
        test_api()
        return
    
    # 检查是否提供了 action
    if not args.action:
        parser.print_help()
        print("\n❌ 错误：请提供操作类型 (--action)")
        print("\n示例:")
        print("  python3 mx_selfselect.py --action query")
        print("  python3 mx_selfselect.py --action add --query '贵州茅台'")
        print("  python3 mx_selfselect.py --action remove --query '贵州茅台'")
        sys.exit(1)
    
    # 查询模式
    if args.action == 'query':
        print("🔍 查询自选股列表...")
        print("")
        
        result = query_self_stocks()
        output = format_query_output(result)
        print(output)
        
        # 保存到 CSV
        if args.output:
            headers, rows = parse_stock_data(result)
            # 使用原始行数据保存
            save_to_csv(rows, args.output)
    
    # 添加模式
    elif args.action == 'add':
        if not args.query:
            print("❌ 错误：添加股票需要提供 --query 参数")
            print("\n示例:")
            print("  python3 mx_selfselect.py --action add --query '贵州茅台'")
            print("  python3 mx_selfselect.py --action add --query '把宁德时代加入自选'")
            sys.exit(1)
        
        # 构建自然语言指令
        if "加入" in args.query or "添加" in args.query:
            query_text = args.query
        else:
            query_text = f"把{args.query}加入自选"
        
        print(f"➕ 添加股票：{args.query}")
        print("")
        
        result = manage_self_stocks(query_text)
        output = format_manage_output(result, 'add', query_text)
        print(output)
    
    # 删除模式
    elif args.action == 'remove':
        if not args.query:
            print("❌ 错误：删除股票需要提供 --query 参数")
            print("\n示例:")
            print("  python3 mx_selfselect.py --action remove --query '贵州茅台'")
            print("  python3 mx_selfselect.py --action remove --query '把宁德时代从自选删除'")
            sys.exit(1)
        
        # 构建自然语言指令
        if "删除" in args.query or "移除" in args.query:
            query_text = args.query
        else:
            query_text = f"把{args.query}从自选删除"
        
        print(f"➖ 删除股票：{args.query}")
        print("")
        
        result = manage_self_stocks(query_text)
        output = format_manage_output(result, 'remove', query_text)
        print(output)


if __name__ == "__main__":
    main()
