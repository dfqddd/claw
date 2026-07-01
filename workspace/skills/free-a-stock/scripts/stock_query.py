#!/usr/bin/env python3
"""
免费 A 股数据查询脚本
基于腾讯财经、新浪财经等免费 API，无需 Token
"""

import argparse
import json
import sys
import urllib.request
import ssl
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 忽略 SSL 验证（某些免费 API 的证书问题）
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://finance.qq.com/'
}


def fetch_url(url: str, decode: str = 'gbk') -> str:
    """获取 URL 内容"""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        response = urllib.request.urlopen(req, timeout=10, context=CTX)
        return response.read().decode(decode)
    except Exception as e:
        raise Exception(f"网络请求失败：{e}")


def parse_symbol(symbol: str) -> tuple:
    """解析股票代码，返回 (市场代码，数字代码)"""
    symbol = symbol.upper().strip()
    
    # 处理带市场后缀的格式 (如 600000.SH, 000001.SZ, 899050.BJ)
    if '.' in symbol:
        parts = symbol.split('.')
        code = parts[0]
        market = parts[1].lower() if len(parts) > 1 else ''
        if market in ['sh', 'sse']:
            return 'sh', code
        elif market in ['sz', 'szse']:
            return 'sz', code
        elif market in ['bj', 'bse']:
            return 'bj', code
    
    # 处理纯数字格式
    if symbol.startswith('6'):
        return 'sh', symbol
    elif symbol.startswith('0') or symbol.startswith('3'):
        return 'sz', symbol
    
    return '', symbol


def get_realtime_quote(symbol: str) -> Dict[str, Any]:
    """获取实时行情（腾讯财经 API）"""
    market, code = parse_symbol(symbol)
    if not market:
        # 处理北交所代码 (8/4/9 开头)
        symbol_stripped = symbol.upper().strip()
        if symbol_stripped.startswith('8') or symbol_stripped.startswith('4') or symbol_stripped.startswith('9'):
            market = 'bj'
            code = symbol_stripped
        else:
            return {"error": f"无效的股票代码：{symbol}"}
    
    # 北交所代码特殊处理
    if market == 'bj':
        url = f"https://qt.gtimg.cn/q=bj{code}"
    else:
        url = f"https://qt.gtimg.cn/q={market}{code}"
    try:
        data = fetch_url(url, 'gbk')
        # 解析腾讯格式：v_sh600000="51~平安银行~000001~10.85~..."
        if '=' not in data:
            return {"error": "数据格式异常"}
        
        parts = data.split('=')[1].strip('"').split('~')
        if len(parts) < 50:
            return {"error": "数据解析失败"}
        
        # 腾讯字段解析 (修正后 v3)
        # 0:未知，1:名称，2:代码，3:现价，4:昨收，5:开盘，6:成交量 (手)
        # 30:时间戳 (YYYYMMDDHHMMSS), 31:涨跌额，32:涨跌幅
        # 33:最高，34:最低，35:现价/成交量/成交额，36:成交量 (手)，37:成交额 (万)
        
        current = float(parts[3]) if parts[3] else 0
        pre_close = float(parts[4]) if parts[4] else 0  # 昨收
        open_price = float(parts[5]) if parts[5] else 0  # 开盘
        volume = int(float(parts[6]) * 100) if parts[6] else 0  # 手->股
        high = float(parts[33]) if len(parts) > 33 and parts[33] else 0  # 最高
        change = float(parts[31]) if len(parts) > 31 and parts[31] else 0
        change_pct = float(parts[32]) if len(parts) > 32 and parts[32] else 0
        low = float(parts[34]) if len(parts) > 34 and parts[34] else 0
        
        # 成交额使用字段 35 的第三个值 (单位：元)，更精确
        amount = 0
        if len(parts) > 35 and '/' in parts[35]:
            amount_parts = parts[35].split('/')
            if len(amount_parts) >= 3 and amount_parts[2]:
                amount = float(amount_parts[2])  # 直接是元
        
        # 获取时间戳
        timestamp = parts[30] if len(parts) > 30 and parts[30] else ""
        if timestamp and len(timestamp) >= 14:
            timestamp = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[8:10]}:{timestamp[10:12]}:{timestamp[12:14]}"
        
        return {
            "symbol": f"{code}.{market.upper()}",
            "name": parts[1],
            "code": code,
            "market": market.upper(),
            "current": current,
            "open": open_price,
            "high": high,
            "low": low,
            "pre_close": pre_close,
            "change": change,
            "change_pct": change_pct,
            "volume": volume,
            "amount": amount,
            "timestamp": timestamp,
            "provider": "腾讯财经"
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}


def get_multi_quotes(symbols: List[str]) -> List[Dict[str, Any]]:
    """批量获取行情"""
    results = []
    for symbol in symbols:
        result = get_realtime_quote(symbol)
        results.append(result)
    return results


def get_kline_data(symbol: str, ktype: str = 'daily', days: int = 100) -> Dict[str, Any]:
    """获取 K 线数据（腾讯财经 API）"""
    market, code = parse_symbol(symbol)
    if not market:
        return {"error": f"无效的股票代码：{symbol}"}
    
    # 腾讯 K 线 API 参数：day(日线), week(周线), month(月线)
    ktype_map = {
        'daily': 'day',
        'weekly': 'week',
        'monthly': 'month'
    }
    ktype_param = ktype_map.get(ktype.lower(), 'day')
    
    # 腾讯 API: param=市场代码，类型，,,,数量，qfq
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={market}{code},{ktype_param},,,{days},qfq"
    
    try:
        data = fetch_url(url)
        result = json.loads(data)
        
        if result.get('code') != 0:
            return {"error": result.get('msg', 'K 线数据获取失败'), "symbol": symbol}
        
        # 解析腾讯 K 线数据
        stock_data = result.get('data', {}).get(f'{market}{code}', {})
        # 腾讯返回的键是 qfqday, qfqweek, qfqmonth (前复权)
        klines = stock_data.get(f'qfq{ktype_param}', []) or stock_data.get(ktype_param, [])
        
        if not klines:
            return {"error": "无 K 线数据", "symbol": symbol, "type": ktype}
        
        # 转换格式：["2026-02-13","10.960","10.910","10.990","10.900","555047.000"]
        # [日期，开盘，收盘，最高，最低，成交量]
        result_data = []
        for k in klines:
            if len(k) >= 6:
                result_data.append({
                    "date": k[0],
                    "open": float(k[1]),
                    "close": float(k[2]),
                    "high": float(k[3]),
                    "low": float(k[4]),
                    "volume": int(float(k[5]) * 100) if k[5] else 0  # 手->股
                })
        
        return {
            "symbol": f"{code}.{market.upper()}",
            "type": ktype,
            "days": days,
            "data": result_data,
            "total": len(result_data),
            "provider": "腾讯财经"
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol, "type": ktype}


def get_stock_list(market: str = 'all') -> Dict[str, Any]:
    """获取股票列表"""
    # 简化版：返回示例数据
    # 实际可以爬取东方财富等网站的股票列表
    
    sample_stocks = [
        {"code": "600000", "name": "浦发银行", "market": "SH"},
        {"code": "600036", "name": "招商银行", "market": "SH"},
        {"code": "000001", "name": "平安银行", "market": "SZ"},
        {"code": "000002", "name": "万科 A", "market": "SZ"},
        {"code": "300001", "name": "特锐德", "market": "SZ"},
        {"code": "688001", "name": "华兴源创", "market": "SH"},
    ]
    
    if market.lower() == 'sh':
        sample_stocks = [s for s in sample_stocks if s['market'] == 'SH']
    elif market.lower() == 'sz':
        sample_stocks = [s for s in sample_stocks if s['market'] == 'SZ']
    
    return {
        "market": market,
        "total": len(sample_stocks),
        "data": sample_stocks,
        "note": "示例数据，完整列表需要访问东方财富等网站",
        "provider": "内置"
    }


def format_output(data: Any, format_type: str = 'json') -> None:
    """格式化输出"""
    if format_type == 'json':
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif format_type == 'table':
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                # 打印表格
                headers = list(data[0].keys())
                print('\t'.join(headers))
                for row in data:
                    print('\t'.join(str(row.get(h, '')) for h in headers))
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2))


def get_market_summary() -> Dict[str, Any]:
    """获取市场汇总数据（含北交所）"""
    indices = [
        {"symbol": "000001.SH", "name": "上证指数", "market": "沪市"},
        {"symbol": "399001.SZ", "name": "深证成指", "market": "深市"},
        {"symbol": "899050.BJ", "name": "北证 50", "market": "北交所"},
    ]
    
    result = {
        "markets": [],
        "total_amount": 0,
        "total_volume": 0,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "provider": "腾讯财经"
    }
    
    for idx in indices:
        data = get_realtime_quote(idx["symbol"])
        if "error" not in data:
            result["markets"].append({
                "market": idx["market"],
                "index": idx["name"],
                "current": data.get("current"),
                "change_pct": data.get("change_pct"),
                "amount": data.get("amount", 0),
                "volume": data.get("volume", 0)
            })
            result["total_amount"] += data.get("amount", 0)
            result["total_volume"] += data.get("volume", 0)
    
    result["total_amount_formatted"] = f"{result['total_amount']/100000000:.2f}亿"
    return result


def main():
    parser = argparse.ArgumentParser(description="免费 A 股数据查询 - 无需 Token")
    parser.add_argument("--symbol", help="股票代码，如 600000.SH 或 000001.SZ")
    parser.add_argument("--symbols", help="多个股票代码，用逗号分隔")
    parser.add_argument("--market-summary", action="store_true", help="获取市场汇总数据（含北交所）")
    parser.add_argument("--kline", choices=['daily', 'weekly', 'monthly'], help="K 线类型")
    parser.add_argument("--days", type=int, default=100, help="K 线天数")
    parser.add_argument("--list", choices=['all', 'sh', 'sz'], help="股票列表")
    parser.add_argument("--format", default='json', choices=['json', 'table'], help="输出格式")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    
    args = parser.parse_args()
    
    try:
        # 市场汇总数据（含北交所）
        if args.market_summary:
            result = get_market_summary()
            format_output(result, args.format)
            return
        
        # 实时行情
        if args.symbols:
            symbols = [s.strip() for s in args.symbols.split(',')]
            result = get_multi_quotes(symbols)
            format_output(result, args.format)
            return
        
        if args.symbol and not args.kline:
            result = get_realtime_quote(args.symbol)
            format_output(result, args.format)
            return
        
        # K 线数据
        if args.symbol and args.kline:
            result = get_kline_data(args.symbol, args.kline, args.days)
            format_output(result, args.format)
            return
        
        # 股票列表
        if args.list:
            result = get_stock_list(args.list)
            format_output(result, args.format)
            return
        
        # 无参数时显示帮助
        parser.print_help()
        
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
