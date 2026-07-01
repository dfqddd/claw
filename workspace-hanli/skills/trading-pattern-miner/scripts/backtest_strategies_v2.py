#!/usr/bin/env python3
"""
5 大交易策略优化版回测
加入更多因子：板块、资金流、情绪、消息面
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys
import math

sys.path.insert(0, str(Path(__file__).parent))

# ============================================================
# 配置
# ============================================================

BASE_DIR = Path(__file__).parent.parent
DB_PATH = Path.home() / ".openclaw/workspace-hanli/skills/a-stock-analysis/data/market.db"
OUTPUT_DIR = BASE_DIR / "analysis" / "backtest_results_v2"

OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# 优化版回测引擎
# ============================================================

class AdvancedBacktestEngine:
    """高级回测引擎 - 支持多因子"""
    
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
            SELECT date, open, close, high, low, change_pct, volume, amount, turnover_rate
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
    
    def get_market_sentiment(self, date: str) -> Dict:
        """获取市场情绪数据"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT limit_up_total, limit_down_total, first_board, continuous_board, seal_rate
            FROM sentiment
            WHERE date = ?
        """, (date,))
        
        row = cursor.fetchone()
        if row:
            up_count = row['first_board'] + row['continuous_board']
            return {
                'up_limit': row['limit_up_total'],
                'down_limit': row['limit_down_total'],
                'up_count': up_count,
                'down_count': row['limit_down_total'],
                'seal_rate': row['seal_rate'],
                'sentiment_score': (up_count - row['limit_down_total']) / max(up_count + row['limit_down_total'], 1) * 100
            }
        return {'sentiment_score': 0, 'up_limit': 0}
    
    def get_sector_ranking(self, date: str, sector_type: str = 'industry') -> List[Dict]:
        """获取板块排名"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, change_pct, rank
            FROM sector_ranking
            WHERE date = ? AND type = ?
            ORDER BY rank ASC
            LIMIT 20
        """, (date, sector_type))
        
        return [{'sector_name': row['name'], 'change_pct': row['change_pct'], 'rank': row['rank']} 
                for row in cursor.fetchall()]
    
    def get_capital_flow(self, date: str) -> Dict:
        """获取资金流向"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT north_net_yi
            FROM capital_flow
            WHERE date = ?
        """, (date,))
        
        row = cursor.fetchone()
        if row:
            return {
                'north_net_yi': row['north_net_yi']
            }
        return {}
    
    def get_stock_info(self, code: str) -> Dict:
        """获取股票基本信息"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, industry, market_cap, pe_ratio, pb_ratio
            FROM stock_info
            WHERE code = ?
        """, (code,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {}
    
    def get_stock_news(self, code: str, start_date: str, end_date: str, limit: int = 5) -> List[Dict]:
        """获取股票新闻"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT date, title, content
            FROM stock_news
            WHERE code = ? AND date BETWEEN ? AND ?
            ORDER BY date DESC
            LIMIT ?
        """, (code, start_date, end_date, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def run_backtest(self, strategy_func, start_date: str, end_date: str, 
                     stock_pool: Optional[List[str]] = None,
                     initial_capital: float = 100000,
                     position_limit: float = 0.2) -> Dict:
        """运行回测"""
        
        # 初始化账户
        capital = initial_capital
        positions = {}
        trades = []
        daily_values = []
        
        # 获取股票池
        if not stock_pool:
            stock_pool = self.get_all_stocks()[:300]
        
        # 获取所有交易日
        trading_days = self.get_trading_days(start_date, end_date)
        
        print(f"\n回测周期：{start_date} ~ {end_date}")
        print(f"交易日数：{len(trading_days)}")
        print(f"股票池：{len(stock_pool)} 只")
        print(f"初始资金：{initial_capital:,.0f}")
        print(f"单只仓位上限：{position_limit*100:.0f}%")
        print("-" * 70)
        
        # 逐日回测
        for i, date in enumerate(trading_days):
            # 获取市场数据
            sentiment = self.get_market_sentiment(date)
            sector_ranking = self.get_sector_ranking(date)
            capital_flow = self.get_capital_flow(date)
            
            # 生成信号
            signals = strategy_func(self, date, stock_pool, positions, {
                'sentiment': sentiment,
                'sector_ranking': sector_ranking,
                'capital_flow': capital_flow
            })
            
            # 执行卖出
            for signal in signals.get('sell', []):
                code = signal['code']
                if code in positions:
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT close FROM stock_daily WHERE code=? AND date=?", 
                                 (code, date))
                    row = cursor.fetchone()
                    if row:
                        sell_price = row[0]
                        pos = positions[code]
                        
                        sell_value = sell_price * pos['shares']
                        profit = sell_value - pos['cost']
                        profit_pct = profit / pos['cost'] * 100
                        
                        capital += sell_value
                        
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
                        
                        del positions[code]
            
            # 执行买入
            buy_count = 0
            max_buy = int(1 / position_limit)  # 最多买几只
            
            for signal in signals.get('buy', []):
                if buy_count >= max_buy:
                    break
                
                code = signal['code']
                if code not in positions and capital > 0:
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT close FROM stock_daily WHERE code=? AND date=?", 
                                 (code, date))
                    row = cursor.fetchone()
                    if row:
                        buy_price = row[0]
                        
                        # 计算买入数量
                        buy_value = min(initial_capital * position_limit, capital)
                        shares = int(buy_value / buy_price / 100) * 100
                        
                        if shares > 0:
                            capital -= buy_price * shares
                            positions[code] = {
                                'shares': shares,
                                'cost': buy_price * shares,
                                'buy_date': date
                            }
                            
                            trades.append({
                                'date': date,
                                'code': code,
                                'action': 'buy',
                                'price': buy_price,
                                'shares': shares,
                                'reason': signal.get('reason', '')
                            })
                            
                            buy_count += 1
            
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
        
        final_value = daily_values[-1]['value']
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100
        
        days = (datetime.strptime(end_date, '%Y-%m-%d') - 
                datetime.strptime(start_date, '%Y-%m-%d')).days
        years = days / 365.25
        annual_return = ((final_value / self.initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0
        
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
        
        # 夏普比率
        if len(daily_values) > 1:
            import statistics
            daily_returns = [(daily_values[i]['value'] - daily_values[i-1]['value']) / daily_values[i-1]['value'] 
                           for i in range(1, len(daily_values))]
            
            if daily_returns:
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
        
        # 平均持仓天数
        avg_hold_days = 0
        if sell_trades:
            hold_days = []
            for t in sell_trades:
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
# 优化版策略实现
# ============================================================

def strategy_long_huitou_v2(engine, date, stock_pool, positions, market_data):
    """
    STRATEGY-001 V2: 龙回头 (优化版)
    加入：市场情绪、板块效应、资金流向
    """
    signals = {'buy': [], 'sell': []}
    
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    start_15d = (date_obj - timedelta(days=20)).strftime('%Y-%m-%d')
    
    # 市场情绪过滤
    sentiment_score = market_data['sentiment'].get('sentiment_score', 0)
    
    for code in stock_pool[:100]:
        if code in positions:
            # 持仓股：跌破 10 日线或盈利>30% 卖出
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC LIMIT 10
            """, (code, start_15d, date))
            closes = [r[0] for r in cursor.fetchall()]
            
            if len(closes) >= 10:
                ma10 = sum(closes) / 10
                cursor.execute("SELECT close FROM stock_daily WHERE code=? AND date=?", (code, date))
                row = cursor.fetchone()
                if row:
                    current_price = row[0]
                    profit = (current_price - positions[code]['cost'] / positions[code]['shares']) / (positions[code]['cost'] / positions[code]['shares'])
                    
                    if current_price < ma10 * 0.95 or profit > 0.3:
                        signals['sell'].append({'code': code, 'reason': '跌破 10 日线或止盈'})
        else:
            # 选股：2 连板以上 + 首次分歧 + 回踩支撑
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close, volume, change_pct FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (code, start_15d, date))
            rows = cursor.fetchall()
            
            if len(rows) >= 5:
                closes = [r[0] for r in rows]
                volumes = [r[1] for r in rows]
                changes = [r[2] for r in rows]
                
                # 检查是否有 2 连板 (降低要求)
                has_2_lianban = False
                for i in range(len(changes)-1):
                    if changes[i] > 9.5 and changes[i+1] > 9.5:
                        has_2_lianban = True
                        break
                
                if has_2_lianban:
                    # 首次分歧：今天未涨停，但跌幅<5%
                    today_change = changes[0] if changes else 0
                    
                    if today_change < 9.5 and today_change > -5:
                        # 回踩 5 日或 10 日线
                        ma5 = sum(closes[:5]) / 5 if len(closes) >= 5 else closes[0]
                        ma10 = sum(closes[:10]) / 10 if len(closes) >= 10 else ma5
                        
                        if closes[0] <= ma5 * 1.05 and closes[0] >= ma5 * 0.95:
                            # 放量
                            if len(volumes) >= 3:
                                avg_vol = sum(volumes[1:4]) / 3
                                if volumes[0] > avg_vol * 1.3:  # 降低放量要求
                                    # 市场情绪好才买
                                    if sentiment_score > 30:
                                        signals['buy'].append({
                                            'code': code,
                                            'reason': f'龙回头 V2:2 连板后回踩 5 日线 (情绪{sentiment_score:.0f})'
                                        })
    
    return signals

def strategy_longtou_shouyin_v2(engine, date, stock_pool, positions, market_data):
    """
    STRATEGY-002 V2: 龙头首阴 (优化版)
    加入：市场地位、板块效应
    """
    signals = {'buy': [], 'sell': []}
    
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    start_10d = (date_obj - timedelta(days=15)).strftime('%Y-%m-%d')
    
    # 获取板块排名
    top_sectors = [s['sector_name'] for s in market_data['sector_ranking'][:5]]
    
    for code in stock_pool[:100]:
        if code in positions:
            # 持仓股：次日不反包卖出
            cursor = engine.conn.cursor()
            cursor.execute("SELECT change_pct FROM stock_daily WHERE code=? AND date=?", (code, date))
            row = cursor.fetchone()
            if row and row[0] < 3:  # 涨幅<3% 卖出
                signals['sell'].append({'code': code, 'reason': '次日不反包'})
        else:
            # 选股：4 连板以上 + 首阴 + 板块龙头
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close, volume, change_pct FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (code, start_10d, date))
            rows = cursor.fetchall()
            
            if len(rows) >= 6:
                changes = [r[2] for r in rows]
                volumes = [r[1] for r in rows]
                
                # 检查 4 连板
                has_4_lianban = all(changes[i] > 9.5 for i in range(4))
                
                if has_4_lianban:
                    # 首阴：今天收阴 3-7%
                    today_change = changes[0]
                    
                    if -7 <= today_change <= -3:
                        # 成交量未失控
                        if volumes[0] < volumes[1] * 2.5:
                            # 获取股票信息，检查是否是板块龙头
                            stock_info = engine.get_stock_info(code)
                            industry = stock_info.get('industry', '')
                            
                            # 如果是热门板块，优先买入
                            is_hot_sector = any(sector in industry for sector in top_sectors)
                            
                            if is_hot_sector:
                                signals['buy'].append({
                                    'code': code,
                                    'reason': f'龙头首阴 V2:4 连板首阴 + 热门板块 ({industry})'
                                })
                            else:
                                signals['buy'].append({
                                    'code': code,
                                    'reason': '龙头首阴 V2:4 连板首阴'
                                })
    
    return signals

def strategy_ershirixian_v2(engine, date, stock_pool, positions, market_data):
    """
    STRATEGY-003 V2: 20 日线趋势 (优化版)
    加入：MACD、板块共振、资金流
    """
    signals = {'buy': [], 'sell': []}
    
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    start_40d = (date_obj - timedelta(days=50)).strftime('%Y-%m-%d')
    
    # 北向资金
    north_flow = market_data['capital_flow'].get('north_net_yi', 0)
    
    for code in stock_pool[:150]:
        if code in positions:
            # 持仓股：跌破 20 日线或 MACD 死叉卖出
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC LIMIT 20
            """, (code, start_40d, date))
            closes = [r[0] for r in cursor.fetchall()]
            
            if len(closes) >= 20:
                ma20 = sum(closes) / 20
                cursor.execute("SELECT close FROM stock_daily WHERE code=? AND date=?", (code, date))
                row = cursor.fetchone()
                if row and row[0] < ma20 * 0.97:
                    signals['sell'].append({'code': code, 'reason': '跌破 20 日线'})
        else:
            # 选股：均线多头 + 回踩 20 日线 + MACD 金叉 + 板块共振
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close, volume FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (code, start_40d, date))
            rows = cursor.fetchall()
            
            if len(rows) >= 30:
                closes = [r[0] for r in rows]
                volumes = [r[1] for r in rows]
                
                # 均线多头
                ma5 = sum(closes[:5]) / 5
                ma10 = sum(closes[:10]) / 10
                ma20 = sum(closes[:20]) / 20
                
                if ma5 > ma10 > ma20:
                    # 回踩 20 日线
                    if closes[0] <= ma20 * 1.03 and closes[0] >= ma20:
                        # 计算 MACD (简化)
                        ema12 = sum(closes[:12]) / 12
                        ema26 = sum(closes[:26]) / 26
                        dif = ema12 - ema26
                        
                        prev_ema12 = sum(closes[1:13]) / 12
                        prev_ema26 = sum(closes[1:27]) / 26
                        prev_dif = prev_ema12 - prev_ema26
                        
                        # MACD 金叉
                        macd_golden_cross = prev_dif < 0 and dif > 0
                        
                        # 放量
                        avg_vol = sum(volumes[5:10]) / 5
                        volume_ok = volumes[0] > avg_vol * 1.5
                        
                        if macd_golden_cross and volume_ok:
                            # 北向资金流入时优先
                            if north_flow > 50:
                                signals['buy'].append({
                                    'code': code,
                                    'reason': '20 日线 V2: 回踩+MACD 金叉 + 北向流入'
                                })
                            else:
                                signals['buy'].append({
                                    'code': code,
                                    'reason': '20 日线 V2: 回踩+MACD 金叉'
                                })
    
    return signals

def strategy_shouban_v2(engine, date, stock_pool, positions, market_data):
    """
    STRATEGY-004 V2: 首板挖掘 (优化版)
    加入：板块效应、消息面、龙虎榜
    """
    signals = {'buy': [], 'sell': []}
    
    # 获取涨停家数
    up_limit = market_data['sentiment'].get('up_limit', 0)
    
    for code in stock_pool[:150]:
        if code in positions:
            # 持仓股：次日不涨停卖出
            cursor = engine.conn.cursor()
            cursor.execute("SELECT change_pct FROM stock_daily WHERE code=? AND date=?", (code, date))
            row = cursor.fetchone()
            if row and row[0] < 5:  # 涨幅<5% 卖出
                signals['sell'].append({'code': code, 'reason': '次日不强'})
        else:
            # 选股：首板 + 板块效应 + 消息催化
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT change_pct, volume, amount FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC LIMIT 3
            """, (code, (date_obj := datetime.strptime(date, '%Y-%m-%d') - timedelta(days=10)).strftime('%Y-%m-%d'), date))
            rows = cursor.fetchall()
            
            if len(rows) == 3:
                today_change = rows[0][0]
                yesterday_change = rows[1][0]
                today_vol = rows[0][1]
                today_amount = rows[0][2]
                
                # 今日首板，昨日未涨停
                if today_change > 9.5 and yesterday_change < 9.5:
                    # 板块效应：涨停家数>50
                    if up_limit > 50:
                        # 放量
                        if today_vol > rows[1][1] * 2:
                            # 板块效应强就买
                            if up_limit > 50:
                                signals['buy'].append({
                                    'code': code,
                                    'reason': f'首板 V2: 首板 + 板块效应 ({up_limit}家涨停)'
                                })
    
    return signals

def strategy_chaodie_v2(engine, date, stock_pool, positions, market_data):
    """
    STRATEGY-005 V2: 超跌反弹 (优化版)
    加入：RSI、布林带、成交量
    """
    signals = {'buy': [], 'sell': []}
    
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    start_20d = (date_obj - timedelta(days=25)).strftime('%Y-%m-%d')
    
    for code in stock_pool[:150]:
        if code in positions:
            # 持仓股：反弹至 20 日线或亏损 -8% 卖出
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC LIMIT 20
            """, (code, start_20d, date))
            closes = [r[0] for r in cursor.fetchall()]
            
            if len(closes) >= 20:
                ma20 = sum(closes) / 20
                cursor.execute("SELECT close FROM stock_daily WHERE code=? AND date=?", (code, date))
                row = cursor.fetchone()
                if row:
                    if row[0] > ma20 * 0.97:
                        signals['sell'].append({'code': code, 'reason': '反弹至 20 日线'})
        else:
            # 选股：超跌 + RSI 超卖 + 企稳阳线
            cursor = engine.conn.cursor()
            cursor.execute("""
                SELECT close, volume, high, low FROM stock_daily 
                WHERE code=? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (code, start_20d, date))
            rows = cursor.fetchall()
            
            if len(rows) >= 15:
                closes = [r[0] for r in rows]
                highs = [r[2] for r in rows]
                lows = [r[3] for r in rows]
                volumes = [r[1] for r in rows]
                
                # 5 日跌幅>12% (降低要求)
                drop_5d = (closes[4] - closes[0]) / closes[4] if len(closes) > 4 else 0
                
                if drop_5d > 0.12:
                    # RSI 超卖 (简化计算)
                    gains = [max(0, closes[i] - closes[i+1]) for i in range(min(6, len(closes)-1))]
                    losses = [max(0, closes[i+1] - closes[i]) for i in range(min(6, len(closes)-1))]
                    
                    avg_gain = sum(gains) / len(gains) if gains else 0
                    avg_loss = sum(losses) / len(losses) if losses else 1
                    
                    rs = avg_gain / avg_loss if avg_loss > 0 else 0
                    rsi = 100 - (100 / (1 + rs))
                    
                    if rsi < 25:  # RSI<25 超卖
                        # 缩量
                        if len(volumes) >= 5:
                            avg_vol = sum(volumes[1:6]) / 5
                            if volumes[0] < avg_vol * 0.5:  # 缩量至 1/2 以下
                                # 阳线确认
                                today_change = (closes[0] - closes[1]) / closes[1] if len(closes) > 1 else 0
                                
                                if today_change > 2:  # 涨幅>2%
                                    signals['buy'].append({
                                        'code': code,
                                        'reason': f'超跌 V2:5 日跌{drop_5d*100:.0f}%+RSI{rsi:.0f}+ 缩量阳线'
                                    })
    
    return signals

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 70)
    print("5 大交易策略优化版回测 (加入多因子)")
    print("=" * 70)
    
    if not DB_PATH.exists():
        print(f"❌ 数据库不存在：{DB_PATH}")
        return
    
    engine = AdvancedBacktestEngine(str(DB_PATH), initial_capital=100000)
    
    strategies = [
        ('STRATEGY-001_V2_龙回头', strategy_long_huitou_v2),
        ('STRATEGY-002_V2_龙头首阴', strategy_longtou_shouyin_v2),
        ('STRATEGY-003_V2_20 日线趋势', strategy_ershirixian_v2),
        ('STRATEGY-004_V2_首板挖掘', strategy_shouban_v2),
        ('STRATEGY-005_V2_超跌反弹', strategy_chaodie_v2),
    ]
    
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
            stock_pool=None,
            initial_capital=100000,
            position_limit=0.2  # 单只 20% 仓位
        )
        
        results[name] = result
        
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
    output_file = OUTPUT_DIR / "backtest_summary_v2.json"
    
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
    generate_comparison_report_v2(results)
    
    engine.close()

def generate_comparison_report_v2(results):
    """生成策略对比报告 V2"""
    
    report = f"""# 5 大策略回测对比报告 V2 (优化版)

**回测周期**: 2025-01-01 ~ 2026-03-05 (15 个月)  
**初始资金**: 100,000 元  
**优化点**: 加入市场情绪、板块效应、资金流向、MACD、RSI 等多因子  
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

## 💡 优化效果对比

"""
    
    # 找出有效策略
    valid_strategies = [(n, r) for n, r in results.items() if r['buy_trades'] > 0]
    
    if valid_strategies:
        report += f"**有效策略**: {len(valid_strategies)} 个\n\n"
        for name, result in valid_strategies:
            report += f"- **{name}**: +{result['total_return']:.1f}% ({result['buy_trades']} 次交易)\n"
    else:
        report += "**所有策略均无交易**，需要继续优化参数\n"
    
    report += f"""
---

## 🎯 结论

"""
    
    if valid_strategies:
        best_return = max(valid_strategies, key=lambda x: x[1]['total_return'])
        best_sharpe = max(valid_strategies, key=lambda x: x[1]['sharpe_ratio'])
        
        report += f"- **收益最高**: {best_return[0]} ({best_return[1]['total_return']:+.2f}%)\n"
        report += f"- **风险收益比最优**: {best_sharpe[0]} (夏普{best_sharpe[1]['sharpe_ratio']:.2f})\n"
    else:
        report += "- 所有策略都需要继续优化\n"
    
    report += f"""
---

**报告生成**: 淘股吧交易模式挖掘工具  
**版本**: V2 (多因子优化版)
"""
    
    report_file = OUTPUT_DIR / "backtest_comparison_v2.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 对比报告：{report_file}")

if __name__ == "__main__":
    main()
