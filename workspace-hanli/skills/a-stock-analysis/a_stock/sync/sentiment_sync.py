"""
市场情绪数据同步模块
基于 AKShare 实时行情计算市场情绪指标

数据源：
  - 腾讯实时行情（主数据源，优先级 0）
  - 同花顺实时行情（备选数据源，优先级 1）
  - 东方财富实时行情（备选数据源，优先级 2）
  - 新浪财经实时行情（备选数据源，优先级 3）
"""

from datetime import datetime
from typing import Dict, List

import akshare as ak
import requests

from a_stock.db import get_connection
from a_stock.db.cache import log_debug, log_info, log_error
from a_stock.db.datasource import DataSource, get_manager


def save_sentiment(records: List[Dict]):
    """将市场情绪数据写入数据库"""
    if not records:
        return

    conn = get_connection()
    try:
        cursor = conn.cursor()

        for record in records:
            cursor.execute(
                """
                INSERT OR REPLACE INTO sentiment
                (date, limit_up_total, first_board, continuous_board, max_height, 
                 max_height_stock, limit_down_total, seal_rate, broken_rate, broken_count,
                 bull_bear_index, fear_greed_index, limit_up_ratio, limit_down_ratio, turnover_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["date"],
                    record.get("limit_up_total", 0),
                    record.get("first_board", 0),
                    record.get("continuous_board", 0),
                    record.get("max_height", 0),
                    record.get("max_height_stock", ""),
                    record.get("limit_down_total", 0),
                    record.get("seal_rate", 0.0),
                    record.get("broken_rate", 0.0),
                    record.get("broken_count", 0),
                    record.get("bull_bear_index", 0.0),
                    record.get("fear_greed_index", 0.0),
                    record.get("limit_up_ratio", 0.0),
                    record.get("limit_down_ratio", 0.0),
                    record.get("turnover_rate", 0.0),
                ),
            )

        conn.commit()
        log_debug(f"已写入 {len(records)} 条市场情绪数据")
    finally:
        conn.close()


def fetch_sentiment_from_tencent(target_date: str) -> Dict:
    """
    从腾讯获取实时行情并计算情绪指标（主数据源）
    
    Args:
        target_date: 目标日期
        
    Returns:
        情绪指标数据字典
    """
    # 腾讯股票API
    url = "http://qt.gtimg.cn/q="
    
    # 获取主要指数
    index_codes = ["sh000001", "sz399001", "sz399006", "sh000300"]
    codes_str = ",".join(index_codes)
    
    try:
        response = requests.get(url + codes_str, timeout=10)
        response.encoding = 'gbk'
        data_text = response.text
        
        up_count = 0
        down_count = 0
        flat_count = 0
        limit_up_count = 0
        limit_down_count = 0
        
        # 解析数据
        for line in data_text.strip().split(";"):
            if not line or "v_" not in line:
                continue
            
            try:
                parts = line.split('="')
                if len(parts) < 2:
                    continue
                
                data_part = parts[1].rstrip('"')
                fields = data_part.split("~")
                
                if len(fields) >= 45:
                    # 腾讯数据字段: [32]是涨跌幅(%)
                    change_pct = float(fields[32]) if fields[32] else 0
                    
                    if change_pct > 0:
                        up_count += 1
                    elif change_pct < 0:
                        down_count += 1
                    else:
                        flat_count += 1
                    
                    if change_pct >= 2:  # 指数涨幅2%算强势
                        limit_up_count += 1
                    if change_pct <= -2:
                        limit_down_count += 1
            except Exception:
                continue
        
        total = up_count + down_count + flat_count
        if total == 0:
            raise ValueError("腾讯数据源返回空数据")
        
        up_ratio = up_count / total
        down_ratio = down_count / total
        
        # 多空指数
        bull_bear_index = (up_ratio - down_ratio) * 100
        
        # 恐惧贪婪指数
        fear_greed_index = up_ratio * 100
        
        return {
            "date": target_date,
            "bull_bear_index": round(bull_bear_index, 2),
            "fear_greed_index": round(fear_greed_index, 2),
            "new_high_ratio": 0.0,
            "new_low_ratio": 0.0,
            "limit_up_ratio": round(limit_up_count / (up_count + 1), 4),
            "limit_down_ratio": round(limit_down_count / (down_count + 1), 4),
            "turnover_rate": 0.0,
            "limit_up_total": limit_up_count,
            "first_board": 0,
            "continuous_board": 0,
            "max_height": 0,
            "max_height_stock": "",
            "limit_down_total": limit_down_count,
            "seal_rate": 0.0,
            "broken_rate": 0.0,
            "broken_count": 0,
        }
        
    except Exception as e:
        log_debug(f"从腾讯获取情绪数据失败: {e}")
        raise


def fetch_sentiment_from_ths(target_date: str) -> Dict:
    """
    从同花顺获取情绪指标（备选数据源）
    
    Args:
        target_date: 目标日期
        
    Returns:
        情绪指标数据字典
    """
    try:
        # 获取同花顺行业板块数量作为市场情绪参考
        df_industry = ak.stock_board_industry_name_ths()
        industry_count = len(df_industry)
        
        # 基于板块数量估算情绪（简化处理）
        # 实际应该获取板块涨跌幅，但同花顺接口限制
        sentiment_score = min(industry_count / 100, 1.0) * 50 + 25  # 25-75范围
        
        return {
            "date": target_date,
            "bull_bear_index": 0.0,
            "fear_greed_index": round(sentiment_score, 2),
            "new_high_ratio": 0.0,
            "new_low_ratio": 0.0,
            "limit_up_ratio": 0.0,
            "limit_down_ratio": 0.0,
            "turnover_rate": 0.0,
            "limit_up_total": 0,
            "first_board": 0,
            "continuous_board": 0,
            "max_height": 0,
            "max_height_stock": "",
            "limit_down_total": 0,
            "seal_rate": 0.0,
            "broken_rate": 0.0,
            "broken_count": 0,
        }
        
    except Exception as e:
        log_debug(f"从同花顺获取情绪数据失败: {e}")
        raise


def fetch_sentiment_from_eastmoney(target_date: str) -> Dict:
    """
    从东方财富获取实时行情并计算情绪指标（主数据源）
    
    Args:
        target_date: 目标日期
        
    Returns:
        情绪指标数据字典
    """
    # 获取全市场实时行情
    df = ak.stock_zh_a_spot_em()
    
    if df is None or df.empty:
        raise ValueError("东财数据源返回空数据")
    
    # 计算涨跌数量
    up_count = len(df[df["涨跌幅"] > 0])
    down_count = len(df[df["涨跌幅"] < 0])
    flat_count = len(df[df["涨跌幅"] == 0])
    
    # 计算涨跌停数量
    limit_up_count = len(df[df["涨跌幅"] >= 9.9])
    limit_down_count = len(df[df["涨跌幅"] <= -9.9])
    
    # 计算创新高/新低数量
    new_high_count = len(df[df["最高"] >= df["昨收"] * 1.09])
    new_low_count = len(df[df["最低"] <= df["昨收"] * 0.91])
    
    # 计算平均换手率
    avg_turnover = df["换手率"].mean() if "换手率" in df.columns else 0
    
    total = up_count + down_count + flat_count
    if total == 0:
        raise ValueError("市场统计数据异常：总股票数为0")
    
    up_ratio = up_count / total
    down_ratio = down_count / total
    
    # 多空指数（-100 到 100）
    bull_bear_index = (up_ratio - down_ratio) * 100
    
    # 恐惧贪婪指数（0 到 100）
    fear_greed_index = (
        up_ratio * 50
        + (limit_up_count / (limit_up_count + limit_down_count + 1)) * 30
        + min(avg_turnover * 2, 20)
    )
    
    return {
        "date": target_date,
        "bull_bear_index": round(bull_bear_index, 2),
        "fear_greed_index": round(fear_greed_index, 2),
        "new_high_ratio": round(new_high_count / (up_count + 1), 4),
        "new_low_ratio": round(new_low_count / (down_count + 1), 4),
        "limit_up_ratio": round(limit_up_count / (up_count + 1), 4),
        "limit_down_ratio": round(limit_down_count / (down_count + 1), 4),
        "turnover_rate": round(avg_turnover, 4),
        "limit_up_total": limit_up_count,
        "first_board": 0,  # 实时行情无法区分首板
        "continuous_board": 0,
        "max_height": 0,
        "max_height_stock": "",
        "limit_down_total": limit_down_count,
        "seal_rate": 0.0,  # 实时行情无法计算
        "broken_rate": 0.0,
        "broken_count": 0,
    }


def fetch_sentiment_from_sina(target_date: str) -> Dict:
    """
    从新浪财经获取实时行情并计算情绪指标（备选数据源）
    
    Args:
        target_date: 目标日期
        
    Returns:
        情绪指标数据字典
    """
    # 获取全市场实时行情（新浪接口）
    df = ak.stock_zh_a_spot()
    
    if df is None or df.empty:
        raise ValueError("新浪数据源返回空数据")
    
    # 计算涨跌数量
    up_count = len(df[df["涨跌幅"] > 0])
    down_count = len(df[df["涨跌幅"] < 0])
    flat_count = len(df[df["涨跌幅"] == 0])
    
    # 计算涨跌停数量（新浪接口涨跌幅字段可能不同）
    limit_up_count = len(df[df["涨跌幅"] >= 9.9])
    limit_down_count = len(df[df["涨跌幅"] <= -9.9])
    
    # 计算创新高/新低数量
    new_high_count = len(df[df["最高"] >= df["昨收"] * 1.09]) if "昨收" in df.columns else 0
    new_low_count = len(df[df["最低"] <= df["昨收"] * 0.91]) if "昨收" in df.columns else 0
    
    # 计算平均换手率
    avg_turnover = df["换手率"].mean() if "换手率" in df.columns else 0
    
    total = up_count + down_count + flat_count
    if total == 0:
        raise ValueError("市场统计数据异常：总股票数为0")
    
    up_ratio = up_count / total
    down_ratio = down_count / total
    
    # 多空指数（-100 到 100）
    bull_bear_index = (up_ratio - down_ratio) * 100
    
    # 恐惧贪婪指数（0 到 100）
    fear_greed_index = (
        up_ratio * 50
        + (limit_up_count / (limit_up_count + limit_down_count + 1)) * 30
        + min(avg_turnover * 2, 20)
    )
    
    return {
        "date": target_date,
        "bull_bear_index": round(bull_bear_index, 2),
        "fear_greed_index": round(fear_greed_index, 2),
        "new_high_ratio": round(new_high_count / (up_count + 1), 4),
        "new_low_ratio": round(new_low_count / (down_count + 1), 4),
        "limit_up_ratio": round(limit_up_count / (up_count + 1), 4),
        "limit_down_ratio": round(limit_down_count / (down_count + 1), 4),
        "turnover_rate": round(avg_turnover, 4),
        "limit_up_total": limit_up_count,
        "first_board": 0,
        "continuous_board": 0,
        "max_height": 0,
        "max_height_stock": "",
        "limit_down_total": limit_down_count,
        "seal_rate": 0.0,
        "broken_rate": 0.0,
        "broken_count": 0,
    }


def register_sentiment_datasources():
    """注册情绪数据源"""
    manager = get_manager()
    
    # 注册东财数据源（优先级 0，主数据源 - 全市场实时行情）
    manager.register(
        "sentiment",
        DataSource(
            name="eastmoney",
            fetch_func=fetch_sentiment_from_eastmoney,
            priority=0,
            retry_count=3,
            retry_delay=2.0,
        )
    )
    
    # 注册新浪数据源（优先级 1，备用 - 全市场数据）
    manager.register(
        "sentiment",
        DataSource(
            name="sina",
            fetch_func=fetch_sentiment_from_sina,
            priority=1,
            retry_count=3,
            retry_delay=2.0,
        )
    )
    
    # 注意：腾讯和同花顺接口只获取少量指数数据，无法计算全市场情绪
    # 不再注册为 sentiment 数据源，避免产生错误数据


def sync_sentiment_from_market_stats(target_date: str) -> bool:
    """
    从 market_stats 表聚合计算市场情绪数据（降级兜底方案）

    当实时行情接口不可用时（如收盘后），从已有的 market_stats 数据计算情绪指标。

    Args:
        target_date: 目标日期

    Returns:
        是否成功
    """
    from a_stock.db.cache import get_connection
    conn = get_connection()
    try:
        cursor = conn.cursor()

        row = cursor.execute(
            "SELECT up_count, down_count, flat_count, limit_up_count, limit_down_count FROM market_stats WHERE date = ?",
            (target_date,)
        ).fetchone()

        if not row:
            log_error(f"market_stats 表没有 {target_date} 的数据，无法聚合 sentiment")
            return False

        up_count = row[0] or 0
        down_count = row[1] or 0
        flat_count = row[2] or 0
        limit_up_count = row[3] or 0
        limit_down_count = row[4] or 0
        total = up_count + down_count + flat_count

        if total == 0:
            log_error(f"market_stats 表 {target_date} 数据异常（总股票数为0）")
            return False

        up_ratio = up_count / total
        bull_bear_index = round((up_count - down_count) / total * 100, 2)
        fear_greed_index = round(
            up_ratio * 50
            + limit_up_count / (limit_up_count + limit_down_count + 1) * 30,
            2
        )

        # 从 limit_up_detail 提取连板情绪指标
        first_board = 0
        continuous_board = 0
        max_height = 0
        max_height_stock = ""
        seal_rate = None
        broken_rate = None
        broken_count = 0

        limit_detail_row = cursor.execute(
            """
            SELECT 
                SUM(CASE WHEN status IN ('涨停','limit_up') AND continuous_board = 1 THEN 1 ELSE 0 END) as first_board,
                SUM(CASE WHEN status IN ('涨停','limit_up') AND continuous_board >= 2 THEN 1 ELSE 0 END) as continuous_board,
                MAX(CASE WHEN status IN ('涨停','limit_up') THEN continuous_board ELSE 0 END) as max_height,
                SUM(CASE WHEN status IN ('涨停','limit_up') THEN 1 ELSE 0 END) as total_up,
                SUM(CASE WHEN status = 'broken' THEN 1 ELSE 0 END) as broken_count
            FROM limit_up_detail WHERE date = ?
            """,
            (target_date,)
        ).fetchone()

        if limit_detail_row and limit_detail_row[0] is not None:
            first_board = limit_detail_row[0] or 0
            continuous_board = limit_detail_row[1] or 0
            max_height = limit_detail_row[2] or 0
            total_up_in_detail = limit_detail_row[3] or 0
            broken_count = limit_detail_row[4] or 0

            # 封板率 = 涨停数 / (涨停数 + 炸板数)
            if total_up_in_detail + broken_count > 0:
                seal_rate = round(total_up_in_detail / (total_up_in_detail + broken_count) * 100, 2)
                broken_rate = round(broken_count / (total_up_in_detail + broken_count) * 100, 2)

            # 获取最高板股票名称
            max_stock_row = cursor.execute(
                """
                SELECT name FROM limit_up_detail 
                WHERE date = ? AND status IN ('涨停','limit_up') 
                ORDER BY continuous_board DESC LIMIT 1
                """,
                (target_date,)
            ).fetchone()
            if max_stock_row:
                max_height_stock = max_stock_row[0] or ""

        data = {
            "date": target_date,
            "limit_up_total": limit_up_count,
            "limit_down_total": limit_down_count,
            "bull_bear_index": bull_bear_index,
            "fear_greed_index": fear_greed_index,
            "first_board": first_board,
            "continuous_board": continuous_board,
            "max_height": max_height,
            "max_height_stock": max_height_stock,
            "seal_rate": seal_rate,
            "broken_rate": broken_rate,
            "broken_count": broken_count,
            "limit_up_ratio": round(limit_up_count / (up_count + 1), 4),
            "limit_down_ratio": round(limit_down_count / (down_count + 1), 4),
            "turnover_rate": 0.0,
        }

        conn.close()
        save_sentiment([data])
        log_info(
            f"从 market_stats+limit_up_detail 聚合情绪数据完成: 多空={bull_bear_index}, "
            f"恐贪={fear_greed_index}, 涨停={limit_up_count}, "
            f"首板={first_board}, 连板={continuous_board}, 最高={max_height}板({max_height_stock})"
        )
        return True

    except Exception as e:
        log_error(f"从 market_stats 聚合情绪数据失败: {e}")
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass


def sync_sentiment(date: str = None):
    """
    同步市场情绪数据

    策略：直接从 market_stats + limit_up_detail 表聚合计算（最准确、最稳定）。
    不再依赖实时行情接口（东财容易封IP，腾讯/新浪数据不全）。

    前置依赖：market_stats 需要先完成同步（依赖 stock_daily + limit_up_detail）。

    Args:
        date: 指定日期（可选，默认为今天）
    """
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    log_info(f"开始同步市场情绪数据: {target_date}")

    if not sync_sentiment_from_market_stats(target_date):
        log_error(f"同步市场情绪数据失败: market_stats 数据不足，无法聚合")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="市场情绪数据同步")
    parser.add_argument("--date", help="指定日期")
    
    args = parser.parse_args()
    sync_sentiment(date=args.date)
