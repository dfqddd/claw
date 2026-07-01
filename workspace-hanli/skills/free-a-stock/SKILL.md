---
name: free-a-stock
description: "免费 A 股数据查询服务 - 基于腾讯/新浪财经 API，无需 Token，完全免费"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
---

# 免费 A 股数据查询服务

基于腾讯财经、新浪财经等免费 API 的 A 股数据查询服务，**无需任何 API Key 或 Token**，完全免费使用。

## 核心功能

- 📊 **实时行情**: 最新股价、涨跌幅、成交量
- 📈 **K 线数据**: 日线、周线、月线历史数据
- 🏢 **股票列表**: A 股全部股票信息
- 💰 **盘口数据**: 买卖五档报价
- 📉 **指数行情**: 上证指数、深证成指等

## 配置要求

### 无需配置！
- ❌ 不需要 API Key
- ❌ 不需要 Token
- ❌ 不需要注册

### 依赖安装
```bash
pip install pandas requests
```

## 使用方法

### 市场汇总查询（推荐）
```bash
# 获取完整市场汇总（含沪市、深市、北交所）
python3 {baseDir}/scripts/stock_query.py --market-summary
```

### 实时行情查询
```bash
# 单只股票
python3 {baseDir}/scripts/stock_query.py --symbol 600000.SH

# 多只股票
python3 {baseDir}/scripts/stock_query.py --symbol 600000.SH,000001.SZ,000002.SZ

# 上证指数
python3 {baseDir}/scripts/stock_query.py --symbol 000001.SH

# 北交所股票
python3 {baseDir}/scripts/stock_query.py --symbol 899050.BJ
```

### K 线数据查询
```bash
# 日线数据（最近 100 天）
python3 {baseDir}/scripts/stock_query.py --symbol 600000.SH --kline daily --days 100

# 周线数据
python3 {baseDir}/scripts/stock_query.py --symbol 000001.SZ --kline weekly --days 365

# 月线数据
python3 {baseDir}/scripts/stock_query.py --symbol 600000.SH --kline monthly --days 720
```

### 股票列表查询
```bash
# 全部 A 股列表
python3 {baseDir}/scripts/stock_query.py --list all

# 上证指数成分股
python3 {baseDir}/scripts/stock_query.py --list sz50
```

## 输出格式

### 实时行情 (JSON)
```json
{
  "symbol": "600000.SH",
  "name": "浦发银行",
  "current": 9.69,
  "open": 9.69,
  "high": 9.72,
  "low": 9.58,
  "pre_close": 9.72,
  "change": -0.03,
  "change_pct": -0.31,
  "volume": 73404604,
  "amount": 710795804,
  "timestamp": "2026-03-02 16:14:02"
}
```

### 市场汇总 (JSON)
```json
{
  "markets": [
    {"market": "沪市", "index": "上证指数", "current": 4122.68, "change_pct": -1.43, "amount": 1425790202336},
    {"market": "深市", "index": "深证成指", "current": 14022.39, "change_pct": -3.07, "amount": 1703720230871},
    {"market": "北交所", "index": "北证 50", "current": 1415.15, "change_pct": -4.11, "amount": 28480463630}
  ],
  "total_amount": 3157990896837,
  "total_amount_formatted": "31579.91 亿",
  "timestamp": "2026-03-03 17:00:02"
}
```

### K 线数据 (JSON)
```json
{
  "symbol": "600000.SH",
  "type": "daily",
  "data": [
    {
      "date": "2026-03-02",
      "open": 9.69,
      "high": 9.72,
      "low": 9.58,
      "close": 9.69,
      "volume": 73404604,
      "amount": 710795804
    }
  ]
}
```

## 股票代码格式

- **上海股票**: `600000.SH` (浦发银行)
- **深圳股票**: `000001.SZ` (平安银行)
- **创业板**: `300001.SZ` (特锐德)
- **科创板**: `688001.SH` (华兴源创)
- **上证指数**: `000001.SH`
- **深证成指**: `399001.SZ`

## 数据源说明

| 数据源 | 用途 | 限制 |
|--------|------|------|
| 腾讯财经 | 实时行情、K 线、盘口 | 无 |

## 适用场景

- ✅ 个人投资者日常看盘
- ✅ 量化策略数据获取
- ✅ 股票数据分析
- ✅ 投资组合跟踪
- ✅ 市场研究分析

## 优势特点

- 🆓 **完全免费**: 无需任何付费订阅
- 🔓 **无需注册**: 直接使用，无门槛
- ⚡ **实时数据**: 交易时间内实时更新
- 📊 **数据齐全**: 覆盖全部 A 股
- 🛡️ **稳定可靠**: 多家数据源备份

## 注意事项

- **交易时间**: 实时行情仅在交易时段更新（9:30-11:30, 13:00-15:00）
- **请求频率**: 建议控制查询频率，避免被限流
- **数据延迟**: 免费数据可能有 1-5 分钟延迟

## 版本信息

- **当前版本**: 1.0.0
- **数据源**: 腾讯财经、新浪财经
- **更新日期**: 2026-03-02

---

*免费 A 股数据查询服务 - 无需 Token，开箱即用* 🆓📊⚡
