### 一、**ETF/基金数据** 📊

- **ETF 实时行情 + 历史K线**：跟踪行业 ETF 资金流入流出，比板块指数更真实反映资金动向
- **ETF 份额变化**：份额增加 = 资金申购流入，比北向资金更灵敏
- AKShare API：`fund_etf_spot_em`、`fund_etf_hist_em`
- **价值**：ETF 份额变化是机构资金最直接的信号，比北向资金更早反映趋势

### 二、**个股资金流向** 💰

- 当前只有整体主力资金，缺少**个股级别**的主力/超大单/大单/中单/小单净流入
- AKShare API：`stock_individual_fund_flow_rank`、`stock_individual_fund_flow`
- **价值**：判断个股是主力吸筹还是出货，配合量价分析更精准

### 三、**大宗交易** 🏦

- 机构大宗交易数据（折价/溢价率、买卖方营业部）
- AKShare API：`stock_dzjy_sctj`（大宗交易统计）、`stock_dzjy_mrmx`（每日明细）
- **价值**：大宗交易折价率是机构减持的重要信号

### 四、**股东/机构持仓** 👥

- 十大股东变动、基金重仓股、社保/QFII 持仓
- AKShare API：`stock_gdfx_free_holding_detail_em`（十大流通股东）
- **价值**：跟踪聪明钱的中长期布局

### 五、**期权数据** 📈

- 50ETF/300ETF 期权的 PCR（看跌/看涨比率）、隐含波动率
- AKShare API：`option_sse_daily_sina`
- **价值**：PCR 是经典的市场情绪反向指标，极端值预示拐点

### 六、**可转债数据** 🔄

- 可转债实时行情、转股溢价率、强赎预警
- AKShare API：`bond_cb_index_jsl`、`bond_cb_jsl`
- **价值**：转债市场活跃度是小盘股情绪的风向标

### 七、**外围市场历史数据** 🌍

- 当前只有实时快照，缺少美股/港股/商品期货的**历史数据**
- 美股三大指数历史K线、VIX 恐慌指数、美债收益率
- AKShare API：`index_us_stock_sina`、`bond_zh_us_rate`
- **价值**：A股开盘前判断外围影响，VIX 是全球风险偏好的温度计

### 八、**宏观经济数据** 📋

- CPI/PPI、PMI、社融、M2、LPR 利率
- AKShare API：`macro_china_cpi`、`macro_china_pmi`、`macro_china_lpr`
- **价值**：中长期趋势判断的基础，政策面分析的数据支撑

### 九、**板块资金流向** 💹

- 当前板块只有涨跌幅排名，缺少**板块级别的主力资金流入流出**
- AKShare API：`stock_sector_fund_flow_rank`
- **价值**：判断板块轮动的资金驱动力，区分"涨但资金在撤"vs"涨且资金在进"

### 十、**涨停股详情** 🎯

- 当前 sentiment 表只有汇总数据，缺少**每只涨停股的具体信息**（涨停原因、封单金额、首次涨停时间、连板数）
- AKShare API：`stock_zt_pool_em`（涨停池）、`stock_zt_pool_previous_em`（昨日涨停）
- **价值**：分析涨停生态链，识别主线龙头