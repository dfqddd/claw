# 淘股吧数据收集指南

**版本**: v1.0  
**更新日期**: 2026-03-05

---

## 🚀 快速开始

### 步骤 1: 配置账号

**方式 A: 运行配置脚本**
```bash
cd ~/.openclaw/workspace-hanli/skills/trading-pattern-miner
./scripts/setup_account.sh
```

**方式 B: 手动编辑**
```bash
# 编辑 ~/.zshrc，添加：
export TAOGUBA_USERNAME="你的用户名"
export TAOGUBA_PASSWORD="你的密码"
```

然后生效：
```bash
source ~/.zshrc
```

---

### 步骤 2: 测试登录

```bash
cd ~/.openclaw/workspace-hanli/skills/trading-pattern-miner
python3 scripts/test_login.py
```

**预期输出**:
```
============================================================
交易模式挖掘 - 账号登录测试
============================================================

找到 1 个账号配置

============================================================
测试淘股吧登录...
============================================================
✅ 淘股吧登录成功!
   用户名：你的用户名

============================================================
登录测试总结
============================================================

✅ 成功登录 1 个网站:
   - taoguba

可以开始爬取数据了!
```

---

### 步骤 3: 爬取实盘数据

```bash
# 爬取 100 个实盘选手
python3 scripts/crawl_taoguba.py --limit 100

# 爬取 500 个实盘选手（更完整）
python3 scripts/crawl_taoguba.py --limit 500
```

**输出**: `data/taoguba_traders.json`

---

### 步骤 4: 提取交易模式

```bash
python3 scripts/extract_patterns.py
```

**输出**: `data/trading_patterns.json`

---

## 📊 数据说明

### 爬取内容

| 数据类型 | 说明 | 数量 |
|---------|------|------|
| 实盘选手 | 有交割单的选手 | 100-500 |
| 交易记录 | 买卖记录 + 理由 | 每人 10-100 条 |
| 收益数据 | 总收益/回撤/胜率 | 每人 1 份 |

### 数据格式

**taoguba_traders.json**:
```json
[
  {
    "trader_id": "淘股吧 - 作手新一",
    "source": "淘股吧",
    "url": "https://www.taoguba.com.cn/user/123456",
    "total_return": 156.8,
    "max_drawdown": -12.5,
    "has_receipt": true,
    "trades": [
      {
        "date": "2026-02-28",
        "code": "000001",
        "name": "平安银行",
        "action": "买入",
        "price": 10.50,
        "reason": "突破 20 日均线，放量"
      }
    ]
  }
]
```

---

## ⚙️ 高级用法

### 指定页码范围
```bash
# 只爬取前 10 页
python3 scripts/crawl_taoguba.py --pages 1-10
```

### 指定板块
```bash
# 只爬取实盘大赛专区
python3 scripts/crawl_taoguba.py --board 1000006
```

### 增量爬取
```bash
# 只爬取新数据（跳过已存在的）
python3 scripts/crawl_taoguba.py --incremental
```

---

## 🔍 数据验证

### 检查数据质量
```bash
python3 -c "
import json
with open('data/taoguba_traders.json') as f:
    data = json.load(f)
print(f'选手数量：{len(data)}')
print(f'有交割单：{sum(1 for t in data if t.get(\"has_receipt\"))}')
print(f'平均交易数：{sum(len(t.get(\"trades\", [])) for t in data) / len(data):.1f}')
"
```

### 查看 Top10 选手
```bash
python3 -c "
import json
with open('data/taoguba_traders.json') as f:
    data = json.load(f)
# 按总收益排序
data.sort(key=lambda x: x.get('total_return', 0), reverse=True)
for i, t in enumerate(data[:10], 1):
    print(f'{i}. {t[\"trader_id\"]} - {t.get(\"total_return\", 0):.1f}%')
"
```

---

## ⚠️ 注意事项

### 爬取频率
- **建议**: 每天 1 次，避免被封 IP
- **限制**: 每次最多 500 个选手
- **时间**: 建议凌晨 2-5 点爬取

### 数据更新
```bash
# 每周一更新一次
0 3 * * 1 cd ~/.openclaw/workspace-hanli/skills/trading-pattern-miner && python3 scripts/crawl_taoguba.py --incremental
```

### 数据备份
```bash
# 备份到 git
cp data/taoguba_traders.json data/backup_$(date +%Y%m%d).json
```

---

## 📈 后续分析

### 模式统计
```bash
python3 scripts/analyze_patterns.py
```

### 生成报告
```bash
python3 scripts/generate_report.py --output report.md
```

### 回测验证
```bash
python3 scripts/backtest_pattern.py --pattern "半路趋势"
```

---

## 🛠️ 故障排查

### 登录失败
```
问题：❌ 淘股吧登录失败
解决：
1. 检查账号密码是否正确
2. 是否需要验证码/短信验证
3. 账号是否被封禁
```

### 爬取失败
```
问题：❌ 爬取失败：HTTP 403
解决：
1. 等待 10 分钟再试
2. 检查 IP 是否被封
3. 降低爬取速度（增加 sleep 时间）
```

### 数据为空
```
问题：✅ 共 0 个实盘选手
解决：
1. 检查登录是否成功
2. 检查板块 URL 是否正确
3. 检查 HTML 解析规则是否需要更新
```

---

## 📞 支持

遇到问题？检查以下文件：
- `SKILL.md` - 技能说明
- `README.md` - 完整文档
- `ACCOUNT_SETUP.md` - 账号配置

---

**淘股吧数据收集 | 只信实盘，不信嘴炮** ⛏️
