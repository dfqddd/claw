#!/usr/bin/env python3
"""
从实盘记录中提取交易模式
分析买卖条件、仓位管理、止损止盈规则
"""

import json
import re
from pathlib import Path
from datetime import datetime

# ============================================================
# 配置
# ============================================================

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# ============================================================
# 模式识别规则
# ============================================================

# 买入条件关键词
BUY_PATTERNS = {
    '突破': ['突破', '创新高', '站上', '放量突破'],
    '低吸': ['低吸', '回调', '支撑位', '企稳'],
    '打板': ['打板', '涨停', '封板', '排板'],
    '半路': ['半路', '启动', '拉升'],
    '龙头': ['龙头', '连板', '高度板'],
}

# 卖出条件关键词
SELL_PATTERNS = {
    '止盈': ['止盈', '获利', '目标位'],
    '止损': ['止损', '割肉', '离场'],
    '跌破': ['跌破', '下穿', '破位'],
    '断板': ['断板', '开板', '炸板'],
}

# 仓位管理关键词
POSITION_PATTERNS = {
    '重仓': ['重仓', '满仓', '大仓位'],
    '轻仓': ['轻仓', '小仓位', '试仓'],
    '分批': ['分批', '加仓', '减仓'],
}

# ============================================================
# 模式提取函数
# ============================================================

def extract_buy_reason(text):
    """提取买入理由"""
    reasons = []
    
    for category, keywords in BUY_PATTERNS.items():
        for kw in keywords:
            if kw in text:
                reasons.append(category)
                break
    
    # 提取具体条件
    conditions = []
    
    # 均线条件
    if '20 日线' in text or '20 日均线' in text:
        conditions.append('突破 20 日均线')
    if '5 日线' in text or '5 日均线' in text:
        conditions.append('突破 5 日均线')
    if '60 日线' in text or '60 日均线' in text:
        conditions.append('突破 60 日均线')
    
    # 量能条件
    if '放量' in text:
        conditions.append('放量')
    if '缩量' in text:
        conditions.append('缩量')
    if '倍量' in text:
        conditions.append('倍量')
    
    # 形态条件
    if '平台' in text:
        conditions.append('突破平台')
    if '新高' in text:
        conditions.append('创新高')
    if '新低' in text:
        conditions.append('创新低')
    
    return {
        'category': reasons[0] if reasons else '其他',
        'conditions': conditions,
    }

def extract_sell_reason(text):
    """提取卖出理由"""
    reasons = []
    
    for category, keywords in SELL_PATTERNS.items():
        for kw in keywords:
            if kw in text:
                reasons.append(category)
                break
    
    # 提取止损止盈
    stop_loss = None
    take_profit = None
    
    # 止损比例
    match = re.search(r'止损[%-]?(\d+)', text)
    if match:
        stop_loss = f"-{match.group(1)}%"
    
    # 止盈比例
    match = re.search(r'止盈[%-]?(\d+)', text)
    if match:
        take_profit = f"+{match.group(1)}%"
    
    return {
        'category': reasons[0] if reasons else '其他',
        'stop_loss': stop_loss,
        'take_profit': take_profit,
    }

def extract_position_rule(text):
    """提取仓位规则"""
    for category, keywords in POSITION_PATTERNS.items():
        for kw in keywords:
            if kw in text:
                return category
    
    return '未明确'

def analyze_trader_trades(trades):
    """分析选手的交易模式"""
    if not trades:
        return None
    
    buy_reasons = []
    sell_reasons = []
    hold_days = []
    profits = []
    
    for trade in trades:
        # 买入分析
        if 'buy_reason' in trade:
            buy_info = extract_buy_reason(trade['buy_reason'])
            buy_reasons.append(buy_info['category'])
        
        # 卖出分析
        if 'sell_reason' in trade:
            sell_info = extract_sell_reason(trade['sell_reason'])
            sell_reasons.append(sell_info['category'])
        
        # 持仓天数
        if 'buy_date' in trade and 'sell_date' in trade:
            try:
                buy_date = datetime.strptime(trade['buy_date'], '%Y-%m-%d')
                sell_date = datetime.strptime(trade['sell_date'], '%Y-%m-%d')
                hold_days.append((sell_date - buy_date).days)
            except:
                pass
        
        # 盈亏
        if 'profit_pct' in trade:
            profits.append(trade['profit_pct'])
    
    # 统计
    from collections import Counter
    
    return {
        'buy_pattern': Counter(buy_reasons).most_common(3),
        'sell_pattern': Counter(sell_reasons).most_common(3),
        'avg_hold_days': sum(hold_days) / len(hold_days) if hold_days else 0,
        'win_rate': len([p for p in profits if p > 0]) / len(profits) * 100 if profits else 0,
        'avg_profit': sum(profits) / len(profits) if profits else 0,
        'total_trades': len(trades),
    }

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("交易模式提取")
    print("=" * 60)
    
    # 读取交易记录
    trades_file = DATA_DIR / "all_trades.json"
    
    if not trades_file.exists():
        print(f"❌ 文件不存在：{trades_file}")
        print("   请先运行爬取脚本")
        return
    
    with open(trades_file, 'r', encoding='utf-8') as f:
        all_trades = json.load(f)
    
    print(f"\n读取到 {len(all_trades)} 条交易记录")
    
    # 按选手分组分析
    from collections import defaultdict
    trader_trades = defaultdict(list)
    
    for trade in all_trades:
        trader_id = trade.get('trader_id', 'unknown')
        trader_trades[trader_id].append(trade)
    
    print(f"共 {len(trader_trades)} 个选手")
    
    # 分析每个选手的模式
    patterns = []
    
    for trader_id, trades in trader_trades.items():
        if len(trades) < 10:  # 至少 10 次交易才有统计意义
            continue
        
        analysis = analyze_trader_trades(trades)
        if analysis:
            patterns.append({
                'trader_id': trader_id,
                'total_trades': analysis['total_trades'],
                'win_rate': round(analysis['win_rate'], 2),
                'avg_profit': round(analysis['avg_profit'], 2),
                'avg_hold_days': round(analysis['avg_hold_days'], 1),
                'buy_pattern': analysis['buy_pattern'],
                'sell_pattern': analysis['sell_pattern'],
            })
    
    # 按胜率排序
    patterns.sort(key=lambda x: x['win_rate'], reverse=True)
    
    # 保存结果
    output_file = DATA_DIR / "trading_patterns.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 保存至：{output_file}")
    print(f"✅ 共 {len(patterns)} 个有效模式")
    
    # 输出 Top10
    print("\n" + "=" * 60)
    print("Top10 交易模式（按胜率）")
    print("=" * 60)
    
    for i, p in enumerate(patterns[:10], 1):
        print(f"\n{i}. 选手 {p['trader_id']}")
        print(f"   交易次数：{p['total_trades']}")
        print(f"   胜率：{p['win_rate']}%")
        print(f"   平均盈利：{p['avg_profit']}%")
        print(f"   平均持仓：{p['avg_hold_days']} 天")
        print(f"   主要买入模式：{p['buy_pattern']}")

if __name__ == "__main__":
    main()
