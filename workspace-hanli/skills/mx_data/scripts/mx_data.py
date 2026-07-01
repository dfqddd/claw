#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mx_data - 妙想金融数据技能
基于东方财富权威数据库，查询金融数据（行情、财务、关系等）
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
API_URL = "https://mkapi2.dfcfs.com/finskillshub/api/claw/query"
API_KEY = os.getenv("MX_APIKEY")

# 请求头
HEADERS = {
    "Content-Type": "application/json",
}


def query_data(tool_query: str) -> dict:
    """
    查询金融数据
    
    Args:
        tool_query: 自然语言查询语句
    
    Returns:
        API 响应字典
    """
    if not API_KEY:
        print("❌ 错误：未找到 API Key")
        print("   请配置环境变量 MX_APIKEY")
        print("   方法：在 ~/.openclaw/workspace-hanli/skills/mx_data/.env 文件中添加")
        print("   格式：MX_APIKEY=your_api_key_here")
        sys.exit(1)
    
    headers = HEADERS.copy()
    headers["apikey"] = API_KEY
    
    data = {
        "toolQuery": tool_query
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败：{e}")
        sys.exit(1)


def parse_table_data(table_data: dict, name_map: dict) -> list:
    """
    解析表格数据
    
    Args:
        table_data: 表格数据字典
        name_map: 列名映射
    
    Returns:
        解析后的表格数据列表
    """
    rows = []
    
    # 获取表头（headName）和指标列
    head_name = None
    head_values = []
    indicator_data = {}
    
    for key, value in table_data.items():
        if key == 'headName':
            head_values = value
        elif key == 'headNameSub':
            head_name = value
        else:
            indicator_data[key] = value
    
    # 构建行数据
    if head_values and indicator_data:
        for idx, head_val in enumerate(head_values):
            row = {'时间/维度': head_val}
            for indicator_code, values in indicator_data.items():
                indicator_name = name_map.get(indicator_code, indicator_code)
                if idx < len(values):
                    row[indicator_name] = values[idx]
            rows.append(row)
    
    return rows


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
    output_lines.append("=" * 60)
    output_lines.append(f"妙想金融数据查询结果")
    output_lines.append(f"查询：{query}")
    output_lines.append(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("=" * 60)
    output_lines.append("")
    
    # 解析结果 - 适配实际 API 返回结构
    # 结构：data.data.searchDataResultDTO.dataTableDTOList
    data_list = []
    try:
        data_list = result.get('data', {}).get('data', {}).get('searchDataResultDTO', {}).get('dataTableDTOList', [])
    except Exception:
        data_list = []
    
    if not data_list:
        output_lines.append("⚠️  未找到相关数据")
        output_lines.append("")
        output_lines.append("💡 建议：")
        output_lines.append("   1. 检查查询语句是否清晰")
        output_lines.append("   2. 尝试更具体的查询词")
        output_lines.append("   3. 到东方财富妙想 AI 查询：https://mkapi2.dfcfs.com/")
        output_lines.append("")
        return "\n".join(output_lines)
    
    for idx, data_item in enumerate(data_list, 1):
        # 证券信息
        code = data_item.get('code', 'N/A')
        entity_name = data_item.get('entityName', 'N/A')
        title = data_item.get('title', 'N/A')
        
        output_lines.append(f"[{idx}] {entity_name}")
        output_lines.append(f"    指标：{title}")
        output_lines.append("")
        
        # 表格数据
        table = data_item.get('table', {})
        raw_table = data_item.get('rawTable', {})
        name_map = data_item.get('nameMap', {})
        indicator_order = data_item.get('indicatorOrder', [])
        
        if table:
            # 获取表头
            head_values = table.get('headName', [])
            head_name_sub = name_map.get('headNameSub', '时间/维度')
            
            # 构建表头行
            headers = [head_name_sub]
            for code in indicator_order:
                headers.append(name_map.get(code, code))
            
            # 构建数据行
            rows = []
            if head_values:
                for i, head_val in enumerate(head_values):
                    row = [str(head_val)]
                    for code in indicator_order:
                        values = table.get(code, [])
                        if i < len(values):
                            row.append(str(values[i]))
                        else:
                            row.append('N/A')
                    rows.append(row)
            
            # 输出表格
            if headers and rows:
                # 计算列宽
                col_widths = []
                for i, header in enumerate(headers):
                    max_width = len(header)
                    for row in rows:
                        if i < len(row):
                            max_width = max(max_width, len(row[i]))
                    col_widths.append(min(max_width + 2, 40))  # 限制最大宽度
                
                # 输出表头
                header_line = "│".join([h.ljust(col_widths[i]) for i, h in enumerate(headers)])
                separator = "┼".join(["─" * w for w in col_widths])
                
                output_lines.append("┌" + "┬".join(["─" * w for w in col_widths]) + "┐")
                output_lines.append("│" + header_line + "│")
                output_lines.append("├" + separator + "┤")
                
                # 输出数据行
                for row in rows:
                    row_line = "│".join([str(row[i]).ljust(col_widths[i]) if i < len(row) else "N/A".ljust(col_widths[i]) for i in range(len(headers))])
                    output_lines.append("│" + row_line + "│")
                
                output_lines.append("└" + "┴".join(["─" * w for w in col_widths]) + "┘")
        
        # 证券标签信息
        entity_tag = data_item.get('entityTagDTO', {})
        if entity_tag:
            secu_type = entity_tag.get('entityTypeName', '')
            market = entity_tag.get('marketChar', '')
            full_name = entity_tag.get('fullName', '')
            
            tag_info = []
            if secu_type:
                tag_info.append(secu_type)
            if market:
                tag_info.append(market)
            
            if tag_info:
                output_lines.append("")
                output_lines.append(f"    证券类型：{' | '.join(tag_info)}")
        
        output_lines.append("")
        output_lines.append("-" * 60)
        output_lines.append("")
    
    output_lines.append("=" * 60)
    output_lines.append(f"共查询到 {len(data_list)} 条数据")
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
    result = query_data("东方财富最新价")
    
    if result:
        print("\n✅ API 连接成功！")
        data_list = result.get('data', {}).get('data', {}).get('searchDataResultDTO', {}).get('dataTableDTOList', [])
        print(f"   返回数据条数：{len(data_list)}")
    else:
        print("\n❌ API 连接失败")
        sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="妙想金融数据技能")
    parser.add_argument("--query", "-q", type=str, help="查询语句")
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
        print("\n❌ 错误：请提供查询语句 (--query)")
        print("\n示例:")
        print("  python3 mx_data.py --query '东方财富最新价'")
        print("  python3 mx_data.py --query '电力板块涨跌幅'")
        print("  python3 mx_data.py --query '顺钠股份 000533 实时行情'")
        print("  python3 mx_data.py --query '宁德时代市盈率' --output data.md")
        sys.exit(1)
    
    # 执行查询
    print(f"🔍 查询：{args.query}")
    print("")
    
    result = query_data(args.query)
    
    # 格式化输出
    output = format_output(result, args.query)
    print(output)
    
    # 保存到文件
    if args.output:
        save_to_file(output, args.output)


if __name__ == "__main__":
    main()
