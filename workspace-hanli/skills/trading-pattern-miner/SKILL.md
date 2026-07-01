---
name: trading-pattern-miner
description: "A 股交易模式挖掘工具。从淘股吧、东财等论坛收集实盘选手的交易记录，甄别筛选后总结有效交易模式。核心：只信实盘，不信嘴炮。"
metadata:
  openclaw:
    emoji: "⛏️"
    requires:
      bins: ["python3"]
---

# 交易模式挖掘工具

从股市论坛挖掘**经过实盘验证**的交易模式，只信交割单，不信嘴炮。

## 核心理念

```
市场已经证明的 > 自己凭空设计的
实盘验证的 > 理论推导的
长期稳定的 > 短期暴利的
```

## 数据源

### 一级数据源（高可信度）

| 来源 | 类型 | 筛选标准 |
|------|------|---------|
| **淘股吧实盘大赛** | 比赛 | 前 100 名，有交割单 |
| **淘股吧实盘帖** | 论坛 | 连续更新 3 个月 +，有交割单 |
| **券商实盘比赛** | 比赛 | 官方验证收益率 |

### 二级数据源（中可信度）

| 来源 | 类型 | 筛选标准 |
|------|------|---------|
| **雪球组合** | 组合 | 跟踪 6 个月 +，收益稳定 |
| **东财实盘帖** | 论坛 | 有交割单截图 |
| **微信公众号** | 文章 | 长期复盘，逻辑清晰 |

### 排除标准

```
❌ 只有理论没有实盘
❌ 晒单不连续（超过 7 天断更）
❌ 只报喜不报忧（从不提亏损）
❌ 推荐股票收费
❌ 收益率异常（月收益>100%）
```

## 依赖安装

```bash
pip install requests beautifulsoup4 pandas
```

## 使用方法

### 1. 收集实盘数据

```bash
# 爬取淘股吧实盘帖
python3 scripts/crawl_taoguba.py --limit 100

# 爬取东财实盘帖
python3 scripts/crawl_eastmoney.py --limit 100

# 爬取雪球组合
python3 scripts/crawl_xueqiu.py --limit 50
```

### 2. 甄别筛选

```bash
# 自动筛选（有交割单 + 连续更新）
python3 scripts/filter_traders.py

# 手动审核
python3 scripts/review_traders.py
```

### 3. 总结模式

```bash
# 提取交易模式
python3 scripts/extract_patterns.py

# 生成模式报告
python3 scripts/generate_report.py
```

### 4. 回测验证

```bash
# 用历史数据验证模式
python3 scripts/backtest_pattern.py --pattern "龙空龙"
```

## 数据库设计

### traders 表（实盘选手）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 网名 |
| source | TEXT | 来源（淘股吧/雪球等） |
| url | TEXT | 主页链接 |
| start_date | TEXT | 开始实盘日期 |
| total_return | REAL | 总收益率 |
| max_drawdown | REAL | 最大回撤 |
| win_rate | REAL | 胜率 |
| has_receipt | BOOLEAN | 是否有交割单 |
| is_verified | BOOLEAN | 是否已验证 |

### trades 表（交易记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| trader_id | INTEGER | 选手 ID |
| date | TEXT | 交易日期 |
| code | TEXT | 股票代码 |
| name | TEXT | 股票名称 |
| action | TEXT | 买入/卖出 |
| price | REAL | 成交价 |
| shares | INTEGER | 股数 |
| amount | REAL | 金额 |
| profit | REAL | 盈亏（卖出时） |
| reason | TEXT | 买卖理由 |

### patterns 表（交易模式）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 模式名称 |
| category | TEXT | 类型（打板/低吸/半路等） |
| trader_ids | TEXT | 使用者 ID 列表（JSON） |
| buy_conditions | TEXT | 买入条件（JSON） |
| sell_conditions | TEXT | 卖出条件（JSON） |
| position_rule | TEXT | 仓位规则 |
| stop_loss | TEXT | 止损规则 |
| win_rate | REAL | 历史胜率 |
| profit_loss_ratio | REAL | 盈亏比 |
| sample_count | INTEGER | 样本数量 |

## 模式分类框架

### 按操作方式分类

```
1. 打板
   - 首板
   - 连板
   - 反包板

2. 低吸
   - 支撑位低吸
   - 均线低吸
   - 超跌低吸

3. 半路
   - 突破半路
   - 加速半路
   - 回调半路

4. 龙头
   - 龙空龙
   - 龙头首阴
   - 龙头反抽

5. 套利
   - 板块套利
   - 可转债套利
   - ETF 套利
```

### 按持仓周期分类

```
- 超短线：1-2 天
- 短线：3-5 天
- 中线：5-20 天
- 长线：20 天 +
```

## 模式模板

```json
{
  "name": "20 日线突破",
  "category": "半路",
  "description": "股价突破 20 日均线，配合放量",
  
  "buy_conditions": {
    "technical": [
      "收盘价 > 20 日均线",
      "成交量 > 5 日均量 1.5 倍",
      "股价创 20 日新高"
    ],
    "fundamental": [
      "业绩预增（可选）",
      "行业景气（可选）"
    ],
    "sentiment": [
      "所属板块当日涨幅前 10（可选）"
    ]
  },
  
  "sell_conditions": {
    "stop_loss": "跌破买入价 -8%",
    "take_profit": "涨幅>20% 或跌破 10 日线",
    "time_limit": "持仓超过 15 天卖出"
  },
  
  "position_rule": "单只股票不超过 20% 仓位",
  "stop_loss": "-8% 坚决止损",
  
  "statistics": {
    "win_rate": 0.55,
    "profit_loss_ratio": 2.3,
    "sample_count": 150,
    "avg_hold_days": 8
  },
  
  "traders": ["淘股吧 - 作手新一", "淘股吧 - asking"],
  "source_urls": ["..."]
}
```

## 质量控制

### 实盘验证标准

```
Level 1: 有交割单截图
Level 2: 交割单连续 3 个月
Level 3: 收益率与大盘对比合理
Level 4: 买卖逻辑一致
Level 5: 模式可复制
```

### 模式有效性标准

```
✅ 有效模式：
  - 样本数 > 50 次交易
  - 胜率 > 50%
  - 盈亏比 > 1.5
  - 最大回撤 < 20%
  - 至少 3 个选手使用

⚠️ 待验证模式：
  - 样本数 20-50 次
  - 胜率 45-50%
  - 需要更多数据

❌ 无效模式：
  - 样本数 < 20 次
  - 胜率 < 45%
  - 盈亏比 < 1
```

## 输出报告

### 月度模式报告

```markdown
# A 股交易模式月报（2026 年 3 月）

## 本月新增模式
1. XX 模式（胜率 55%，样本 30 次）
2. XX 模式（胜率 50%，样本 50 次）

## 模式表现排名
| 模式 | 胜率 | 盈亏比 | 本月收益 |
|------|------|--------|---------|
| 龙空龙 | 52% | 3.5 | +15% |
| 首板 | 48% | 2.8 | +12% |
| 低吸 | 55% | 2.0 | +8% |

## 失效模式预警
- XX 模式（连续 3 周亏损）
- XX 模式（市场环境变化）
```

## 参考资源

- 淘股吧：https://www.taoguba.com.cn/
- 东财股吧：https://guba.eastmoney.com/
- 雪球：https://xueqiu.com/

---

**交易模式挖掘 | 只信实盘，不信嘴炮** ⛏️
