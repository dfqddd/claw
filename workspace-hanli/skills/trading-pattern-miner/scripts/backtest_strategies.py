#!/usr/bin/env python3
"""
5 大交易策略批量回测
基于淘股吧知名选手交易模式
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent))

# ============================================================
# 配置
# ============================================================

BASE_DIR = Path(__file__).parent.parent
# 使用 a-stock-analysis 技能的数据库
DB_PATH = Path.home() / ".openclaw/workspace-hanli/skills/a-stock-analysis/data/market.db"
OUTPUT_DIR = BASE_DIR / "analysis" / "backtest_results"

OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# 回测引擎
# ============================================================

class BacktestEngine:
    """策略回测引擎"""
    
    def __init__(self, db_path: str, initial_capital: float = 100000):
        self.db_path = db_path
        self.initial_capital = initial_capital
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        self.conn.close()
    
    def get_stock_data(self, code: str, start_date: str, end_date: str) -> List[Dict]:
        """获取股票历史数据"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT date, open, close, high, low, change_pct, volume, amount
            FROM stock_daily
            WHERE code = ? AND date BETWEEN ? AND ?
            ORDER BY date ASC
        """, (code, start_date, end_date))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_stocks(self) -> List[str]:
        """获取所有股票代码"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT code FROM stock_daily ORDER BY code")
        return [row[0] for row in cursor.fetchall()]
    
    def get_trading_days(self, start_date: str, end_date: str) -> List[str]:
        """获取交易日列表"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT date FROM stock_daily 
            WHERE date BETWEEN ? AND ? 
            ORDER BY date ASC
        """, (start_date, end_date))
        return [row[0] for row in cursor.fetchall()]
    
    def run_backtest(self, strategy_func, start_date: str, end_date: str, 
                     stock_pool: Optional[List[str]] = None,
                     initial_capital: float = 100000) -> Dict:
        """运行回测"""
        
        # 初始化账户
        capital = initial_capital
        positions = {}  # {code: {'shares': x, 'cost': y, 'buy_date': '2026-01-01'}}
        trades = []     # 交易记录
        daily_values = []  # 每日市值
        
        # 获取股票池
        if not stock_pool:
            stock_pool = self.get_all_stocks()[:200]  # 默认前 200 只
        
        # 获取所有交易日
        trading_days = self.get_trading_days(start_date, end_date)
        
        print(f"\n回测周期：{start_date} ~ {end_date}")
        print(f"交易日数：{len(trading_days)}")
        print(f"股票池：{len(stock_pool)} 只")
        print(f"初始资金：{initial_capital:,.0f}")
        print("-" * 70)
        
        # 逐日回测
        for date in trading_days:
            # 生成信号
            signals = strategy_func(self, date, stock_pool, positions)
            
            # 执行卖出
            for signal in signals.get('sell', []):
                code = signal['code']
                if code in positions:
                    # 获取当日收盘价
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT close FROM stock_daily WHERE code=? AND date=?", 
                                 (code, date))
                    row = cursor.fetchone()
                    if row:
                        sell_price = row[0]
                        pos = positions[code]
                        
                        # 计算盈亏
                        sell_value = sell_price * pos['shares']
                        profit = sell_value - pos['cost']
                        profit_pct = profit / pos['cost'] * 100
                        
                        # 更新资金
                        capital += sell_value
                        
                        # 记录交易
                        trades.append({
                            'date': date,
                            'code': code,
                            'action': 'sell',
                            'price': sell_price,
                            'shares': pos['shares'],
                            'profit': profit,
                            'profit_pct': profit_pct,
                            'reason': signal.get('reason', '')
                        })
                        
                        # 清除持仓
                        del positions[code]
            
            # 执行买入
            for signal in signals.get('buy', []):
                code = signal['code']
                if code not in positions and capital > 0:
                    # 获取当日收盘价
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT close FROM stock_daily WHERE code=? AND date=?", 
                                 (code, date))
                    row = cursor.fetchone()
                    if row:
                        buy_price = row[0]
                        
                        # 计算买入数量 (每只股票最多 20% 仓位)
                        buy_value = min(initial_capital * 0.2, capital)
                        shares = int(buy_value / buy_price / 100) * 100
                        
                        if shares > 0:
                            # 更新资金和持仓
                            capital -= buy_price * shares
                            positions[code] = {
                                'shares': shares,
                                'cost': buy_price * shares,
                                'buy_date': date
                            }
                            
                            # 记录交易
                            trades.append({
                                'date': date,
                                'code': code,
                                'action': 'buy',
                                'price': buy_price,
                                'shares': shares,
                                'reason': signal.get('reason', '')
                            })
            
            # 计算当日总市值
            total_value = capital
            for code, pos in positions.items():
                cursor = self.conn.cursor()
                cursor.execute("SELECT close FROM stock_daily WHERE code=? AND date=?", 
                             (code, date))
                row = cursor.fetchone()
                if row:
                    total_value += row[0] * pos['shares']
            
            daily_values.append({'date': date, 'value': total_value})
        
        # 计算回测结果
        return self._calculate_results(daily_values, trades, start_date, end_date)
    
    def _calculate_results(self, daily_values: List[Dict], trades: List[Dict], 
                          start_date: str, end_date: str) -> Dict:
        """计算回测结果"""
        
        if not daily_values:
            return {}
        
        # 总收益率
        final_value = daily_values[-1]['value']
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100
        
        # 年化收益率
        days = (datetime.strptime(end_date, '%Y-%m-%d') - 
                datetime.strptime(start_date, '%Y-%m-%d')).days
        years = days / 365.25
        if years > 0:
            annual_return = ((final_value / self.initial_capital) ** (1 / years) - 1) * 100
        else:
            annual_return = 0
        
        # 最大回撤
        peak = daily_values[0]['value']
        max_drawdown = 0
        max_drawdown_date = ''
        for dv in daily_values:
            if dv['value'] > peak:
                peak = dv['value']
            drawdown = (peak - dv['value']) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_drawdown_date = dv['date']
        
        # 胜率
        sell_trades = [t for t in trades if t['action'] == 'sell']
        profitable_trades = [t for t in sell_trades if t.get('profit', 0) > 0]
        losing_trades = [t for t in sell_trades if t.get('profit', 0) <= 0]
        
        win_rate = len(profitable_trades) / len(sell_trades) * 100 if sell_trades else 0
        
        # 盈亏比
        if profitable_trades and losing_trades:
            avg_profit = sum(t['profit'] for t in profitable_trades) / len(profitable_trades)
            avg_loss = abs(sum(t['profit'] for t in losing_trades) / len(losing_trades))
            profit_loss_ratio = avg_profit / avg_loss if avg_loss > 0 else 0
        else:
            profit_loss_ratio = 0
        
        # 夏普比率 (简化计算)
        if len(daily_values) > 1:
            daily_returns = []
            for i in range(1, len(daily_values)):
                ret = (daily_values[i]['value'] - daily_values[i-1]['value']) / daily_values[i-1]['value']
                daily_returns.append(ret)
            
            if daily_returns:
                import statistics
                avg_return = statistics.mean(daily_returns)
                std_return = statistics.stdev(daily_returns) if len(daily_returns) > 1 else 1
                sharpe = (avg_return / std_return) * (252 ** 0.5) if std_return > 0 else 0
            else:
                sharpe = 0
        else:
            sharpe = 0
        
        # 交易统计
        total_trades = len(trades)
        buy_trades = len([t for t in trades if t['action'] == 'buy'])
        sell_trades_count = len(sell_trades)
        avg_hold_days = 0
        
        if sell_trades:
            hold_days = []
            for t in sell_trades:
                # 查找对应的买入日期
                buy_trade = next((tr for tr in trades if tr['code'] == t['code'] 
                                and tr['action'] == 'buy' and tr['date'] < t['date']), None)
                if buy_trade:
                    days = (datetime.strptime(t['date'], '%Y-%m-%d') - 
                           datetime.strptime(buy_trade['date'], '%Y-%m-%d')).days
                    hold_days.append(days)
            if hold_days:
                avg_hold_days = sum(hold_days) / len(hold_days)
        
        return {
            'total_return': round(total_return, 2),
            'annual_return': round(annual_return, 2),
            'max_drawdown': round(max_drawdown, 2),
            'max_drawdown_date': max_drawdown_date,
            'win_rate': round(win_rate, 2),
            'profit_loss_ratio': round(profit_loss_ratio, 2),
            'sharpe_ratio': round(sharpe, 2),
            'total_trades': total_trades,
            'buy_trades': buy_trades,
            'sell_trades': sell_trades_count,
            'avg_hold_days': round(avg_hold_days, 1),
            'final_value': round(final_value, 2),
            'trades': trades
        }

# ============================================================
# 策略实现
# ============================================================

def strategy_long_huitou(engine, date, stock_pool, positions):
    """
    STRATEGY-001: 龙回头
    龙头股连续涨停后首次分歧，回踩 10 日线买入
    """
    signals = {'buy': [], 'sell': []}
    
    # 获取近 10 日数据
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    start_10d = (date_obj - timedelta(days=15)).strftime('%Y-%m-%d')
    
    for code in stock_pool[:50]:  # 只检查前 50 只
        if code in positions:
            # 持仓股：跌破 5 日线卖出
            cursor = engine.conn.cursor()
            cursor.execute("SELECT close FROM stock_daily WHERE code=? AND date=?", (code, date))
            row = cursor.fetchone()
            if row:
                current_price = row[0]
                # 获取 5 日线
                cursor.execute("""
                    SELECT close FROM stock_daily 
                    WHERE code=? AND date BETWEEN ? AND ?
                    ORDER BY date DESC LIMIT 5
                """, (code, start_10d, date))
                closes = [r[0] for r in cursor.fetchall()]
                if len(closes) >= 5:
                    ma5 = sum(closes) / 5
                    if current_price < ma5 * 0.95:  # 跌破 5 日线 -5%
                        signals['sell'].append({'code': code, 'reason': '跌破 5 日线'})
        else:
            # 选股：连板后回踩 10 日线
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close, volume FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (code, start_10d, date))
            rows = cursor.fetchall()
            
            if len(rows) >= 5:
                closes = [r[0] for r in rows]
                volumes = [r[1] for r in rows]
                
                # 检查是否有 3 连板
                has_3_lianban = False
                for i in range(len(closes)-1):
                    if (closes[i] / closes[i+1] > 1.095 and 
                        i+2 < len(closes) and closes[i+1] / closes[i+2] > 1.095 and
                        i+3 < len(closes) and closes[i+2] / closes[i+3] > 1.095):
                        has_3_lianban = True
                        break
                
                if has_3_lianban:
                    # 首次分歧：今天未涨停
                    today_change = (closes[0] - closes[1]) / closes[1] if len(closes) > 1 else 0
                    
                    if today_change < 0.095:  # 今天未涨停
                        # 回踩 10 日线
                        ma10 = sum(closes[:10]) / len(closes[:10]) if len(closes) >= 10 else sum(closes) / len(closes)
                        
                        if closes[0] <= ma10 * 1.02 and closes[0] > ma10:
                            # 放量
                            if len(volumes) >= 5:
                                avg_vol = sum(volumes[1:6]) / 5
                                if volumes[0] > avg_vol * 1.5:
                                    signals['buy'].append({
                                        'code': code,
                                        'reason': '龙回头：3 连板后回踩 10 日线'
                                    })
    
    return signals

def strategy_longtou_shouyin(engine, date, stock_pool, positions):
    """
    STRATEGY-002: 龙头首阴
    龙头股连续涨停后首次收阴
    """
    signals = {'buy': [], 'sell': []}
    
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    start_10d = (date_obj - timedelta(days=15)).strftime('%Y-%m-%d')
    
    for code in stock_pool[:50]:
        if code in positions:
            # 持仓股：次日不涨停卖出
            cursor = engine.conn.cursor()
            cursor.execute("SELECT close FROM stock_daily WHERE code=? AND date=?", (code, date))
            row = cursor.fetchone()
            if row:
                today_change = (row[0] - positions[code]['cost'] / positions[code]['shares']) / (positions[code]['cost'] / positions[code]['shares'])
                if today_change < 0.05:  # 涨幅<5% 卖出
                    signals['sell'].append({'code': code, 'reason': '次日不强势'})
        else:
            # 选股：5 连板后首阴
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close, volume FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (code, start_10d, date))
            rows = cursor.fetchall()
            
            if len(rows) >= 6:
                closes = [r[0] for r in rows]
                
                # 检查 5 连板
                has_5_lianban = True
                for i in range(5):
                    if closes[i] / closes[i+1] < 1.095:
                        has_5_lianban = False
                        break
                
                if has_5_lianban:
                    # 首阴：今天收阴但未跌停
                    today_change = (closes[0] - closes[1]) / closes[1]
                    
                    if today_change < 0 and today_change > -0.1:  # 收阴但未跌停
                        # 成交量未失控
                        if len(rows) > 1:
                            if rows[0][1] < rows[1][1] * 2:
                                signals['buy'].append({
                                    'code': code,
                                    'reason': '龙头首阴：5 连板后首阴'
                                })
    
    return signals

def strategy_ershirixian(engine, date, stock_pool, positions):
    """
    STRATEGY-003: 20 日线趋势
    回踩 20 日线不破，放量突破
    """
    signals = {'buy': [], 'sell': []}
    
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    start_30d = (date_obj - timedelta(days=40)).strftime('%Y-%m-%d')
    
    for code in stock_pool[:100]:
        if code in positions:
            # 持仓股：跌破 20 日线卖出
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC LIMIT 20
            """, (code, start_30d, date))
            closes = [r[0] for r in cursor.fetchall()]
            
            if len(closes) >= 20:
                ma20 = sum(closes) / 20
                cursor.execute("SELECT close FROM stock_daily WHERE code=? AND date=?", (code, date))
                row = cursor.fetchone()
                if row and row[0] < ma20 * 0.98:
                    signals['sell'].append({'code': code, 'reason': '跌破 20 日线'})
        else:
            # 选股：回踩 20 日线
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close, volume FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (code, start_30d, date))
            rows = cursor.fetchall()
            
            if len(rows) >= 25:
                closes = [r[0] for r in rows]
                volumes = [r[1] for r in rows]
                
                # 均线多头
                ma5 = sum(closes[:5]) / 5
                ma10 = sum(closes[:10]) / 10
                ma20 = sum(closes[:20]) / 20
                
                if ma5 > ma10 > ma20:
                    # 回踩 20 日线
                    if closes[0] <= ma20 * 1.02 and closes[0] > ma20:
                        # 放量
                        avg_vol = sum(volumes[5:10]) / 5
                        if volumes[0] > avg_vol * 1.5:
                            signals['buy'].append({
                                'code': code,
                                'reason': '20 日线趋势：回踩放量'
                            })
    
    return signals

def strategy_shouban(engine, date, stock_pool, positions):
    """
    STRATEGY-004: 首板挖掘
    突发利好 + 板块效应 + 最先涨停
    """
    signals = {'buy': [], 'sell': []}
    
    # 简化版：只抓首板，次日卖出
    for code in stock_pool[:100]:
        if code in positions:
            # 持仓股：次日不涨停卖出
            cursor = engine.conn.cursor()
            cursor.execute("SELECT change_pct FROM stock_daily WHERE code=? AND date=?", (code, date))
            row = cursor.fetchone()
            if row and row[0] < 0.03:  # 涨幅<3% 卖出
                signals['sell'].append({'code': code, 'reason': '次日不强'})
        else:
            # 选股：首板涨停
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT change_pct, volume FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC LIMIT 2
            """, (code, (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=5)).strftime('%Y-%m-%d'), date))
            rows = cursor.fetchall()
            
            if len(rows) == 2:
                today_change = rows[0][0]
                yesterday_change = rows[1][0]
                
                # 今日涨停，昨日未涨停
                if today_change > 0.095 and yesterday_change < 0.095:
                    # 放量
                    if rows[0][1] > rows[1][1] * 2:
                        signals['buy'].append({
                            'code': code,
                            'reason': '首板挖掘'
                        })
    
    return signals

def strategy_chaodie(engine, date, stock_pool, positions):
    """
    STRATEGY-005: 超跌反弹
    5 日跌幅>15%，RSI 超卖，阳线确认
    """
    signals = {'buy': [], 'sell': []}
    
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    start_15d = (date_obj - timedelta(days=20)).strftime('%Y-%m-%d')
    
    for code in stock_pool[:100]:
        if code in positions:
            # 持仓股：反弹至 10 日线卖出
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC LIMIT 10
            """, (code, start_15d, date))
            closes = [r[0] for r in cursor.fetchall()]
            
            if len(closes) >= 10:
                ma10 = sum(closes) / 10
                if closes[0] > ma10 * 0.98:
                    signals['sell'].append({'code': code, 'reason': '反弹至 10 日线'})
        else:
            # 选股：超跌反弹
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close, volume FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (code, start_15d, date))
            rows = cursor.fetchall()
            
            if len(rows) >= 10:
                closes = [r[0] for r in rows]
                
                # 5 日跌幅>15%
                drop_5d = (closes[4] - closes[0]) / closes[4] if len(closes) > 4 else 0
                
                if drop_5d > 0.15:
                    # RSI 超卖 (简化计算)
                    rsi = closes[0] / max(closes[:10]) * 100
                    
                    if rsi < 30:
                        # 阳线确认
                        today_change = (closes[0] - closes[1]) / closes[1] if len(closes) > 1 else 0
                        
                        if today_change > 0.03:  # 涨幅>3%
                            signals['buy'].append({
                                'code': code,
                                'reason': '超跌反弹：5 日跌 15%+RSI 超卖 + 阳线'
                            })
    
    return signals

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 70)
    print("5 大交易策略批量回测")
    print("=" * 70)
    
    # 检查数据库
    if not DB_PATH.exists():
        print(f"❌ 数据库不存在：{DB_PATH}")
        print("   请先运行数据同步脚本")
        return
    
    # 初始化回测引擎
    engine = BacktestEngine(str(DB_PATH), initial_capital=100000)
    
    # 策略列表
    strategies = [
        ('STRATEGY-001_龙回头', strategy_long_huitou),
        ('STRATEGY-002_龙头首阴', strategy_longtou_shouyin),
        ('STRATEGY-003_20 日线趋势', strategy_ershirixian),
        ('STRATEGY-004_首板挖掘', strategy_shouban),
        ('STRATEGY-005_超跌反弹', strategy_chaodie),
    ]
    
    # 回测周期
    start_date = '2025-01-01'
    end_date = '2026-03-05'
    
    results = {}
    
    for name, strategy_func in strategies:
        print(f"\n{'='*70}")
        print(f"回测策略：{name}")
        print(f"{'='*70}")
        
        result = engine.run_backtest(
            strategy_func,
            start_date,
            end_date,
            stock_pool=None  # 使用默认股票池
        )
        
        results[name] = result
        
        # 输出结果
        print(f"\n📊 回测结果:")
        print(f"  总收益率：{result['total_return']:+.2f}%")
        print(f"  年化收益：{result['annual_return']:+.2f}%")
        print(f"  最大回撤：{result['max_drawdown']:.2f}% ({result['max_drawdown_date']})")
        print(f"  胜率：{result['win_rate']:.2f}%")
        print(f"  盈亏比：1:{result['profit_loss_ratio']:.2f}")
        print(f"  夏普比率：{result['sharpe_ratio']:.2f}")
        print(f"  交易次数：{result['buy_trades']} 买 / {result['sell_trades']} 卖")
        print(f"  平均持仓：{result['avg_hold_days']:.1f} 天")
        print(f"  最终资金：{result['final_value']:,.2f} 元")
    
    # 保存结果
    output_file = OUTPUT_DIR / "backtest_summary.json"
    
    # 移除 trades 详细数据以减小文件大小
    results_summary = {}
    for name, result in results.items():
        results_summary[name] = {k: v for k, v in result.items() if k != 'trades'}
        results_summary[name]['trade_count'] = len(result.get('trades', []))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results_summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ 回测完成！")
    print(f"✅ 结果保存：{output_file}")
    print(f"{'='*70}")
    
    # 生成对比报告
    generate_comparison_report(results)
    
    engine.close()

def generate_comparison_report(results):
    """生成策略对比报告"""
    
    report = f"""# 5 大策略回测对比报告

**回测周期**: 2025-01-01 ~ 2026-03-05  
**初始资金**: 100,000 元  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 策略对比

| 策略 | 总收益 | 年化 | 最大回撤 | 胜率 | 盈亏比 | 夏普 | 交易次数 |
|------|--------|------|---------|------|--------|------|---------|
"""
    
    for name, result in results.items():
        report += f"| {name.replace('STRATEGY-', '').replace('_', ' ')} | "
        report += f"{result['total_return']:+.1f}% | "
        report += f"{result['annual_return']:+.1f}% | "
        report += f"{result['max_drawdown']:.1f}% | "
        report += f"{result['win_rate']:.1f}% | "
        report += f"1:{result['profit_loss_ratio']:.2f} | "
        report += f"{result['sharpe_ratio']:.2f} | "
        report += f"{result['buy_trades']} |\n"
    
    report += f"""
---

## 🏆 策略排名

### 按总收益率
"""
    
    sorted_by_return = sorted(results.items(), key=lambda x: x[1]['total_return'], reverse=True)
    for i, (name, result) in enumerate(sorted_by_return, 1):
        report += f"{i}. **{name}**: {result['total_return']:+.2f}%\n"
    
    report += f"""
### 按夏普比率
"""
    
    sorted_by_sharpe = sorted(results.items(), key=lambda x: x[1]['sharpe_ratio'], reverse=True)
    for i, (name, result) in enumerate(sorted_by_sharpe, 1):
        report += f"{i}. **{name}**: {result['sharpe_ratio']:.2f}\n"
    
    report += f"""
### 按最大回撤 (越小越好)
"""
    
    sorted_by_drawdown = sorted(results.items(), key=lambda x: x[1]['max_drawdown'])
    for i, (name, result) in enumerate(sorted_by_drawdown, 1):
        report += f"{i}. **{name}**: {result['max_drawdown']:.2f}%\n"
    
    report += f"""
---

## 💡 结论

"""
    
    # 最佳策略
    best_return = max(results.items(), key=lambda x: x[1]['total_return'])
    best_sharpe = max(results.items(), key=lambda x: x[1]['sharpe_ratio'])
    lowest_drawdown = min(results.items(), key=lambda x: x[1]['max_drawdown'])
    
    report += f"- **收益最高**: {best_return[0]} ({best_return[1]['total_return']:+.2f}%)\n"
    report += f"- **风险收益比最优**: {best_sharpe[0]} (夏普{best_sharpe[1]['sharpe_ratio']:.2f})\n"
    report += f"- **回撤最小**: {lowest_drawdown[0]} ({lowest_drawdown[1]['max_drawdown']:.2f}%)\n"
    
    report += f"""
---

## 📋 配置建议

基于回测结果，建议聪哥采用以下配置:

```
核心策略 (60%):
- {sorted_by_sharpe[0][0]}: 30%
- {sorted_by_sharpe[1][0]}: 30%

进攻策略 (30%):
- {sorted_by_return[0][0]}: 30%

防守策略 (10%):
- {lowest_drawdown[0][0]}: 10%
```

---

**报告生成**: 淘股吧交易模式挖掘工具
"""
    
    # 保存报告
    report_file = OUTPUT_DIR / "backtest_comparison.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 对比报告：{report_file}")

if __name__ == "__main__":
    main()
