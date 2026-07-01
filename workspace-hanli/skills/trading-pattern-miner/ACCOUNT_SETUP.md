# 交易模式挖掘 - 数据源账号配置

**安全提示**: 此文件包含敏感信息，请勿上传到 Git 或分享给他人

---

## 配置方式

### 方式 1: 环境变量 (推荐)

在 `~/.bashrc` 或 `~/.zshrc` 中添加:

```bash
# 淘股吧
export TAOGUBA_USERNAME="你的用户名"
export TAOGUBA_PASSWORD="你的密码"

# 东方财富
export EASTMONEY_USERNAME="你的用户名"
export EASTMONEY_PASSWORD="你的密码"

# 雪球
export XUEQIU_PHONE="你的手机号"
export XUEQIU_PASSWORD="你的密码"
```

然后执行 `source ~/.bashrc` 或 `source ~/.zshrc`

### 方式 2: 本地配置文件

在 `~/.openclaw/workspace-hanli/skills/trading-pattern-miner/.credentials` 创建文件:

```ini
[taoguba]
username = 你的用户名
password = 你的密码

[eastmoney]
username = 你的用户名
password = 你的密码

[xueqiu]
phone = 你的手机号
password = 你的密码
```

**权限设置**:
```bash
chmod 600 ~/.openclaw/workspace-hanli/skills/trading-pattern-miner/.credentials
```

---

## 所需账号

### 淘股吧 (优先级 ⭐⭐⭐⭐⭐)
- **用途**: 实盘大赛数据、实盘帖
- **注册**: https://www.taoguba.com.cn/
- **必需**: ✅ 是 (核心数据源)

### 东方财富 (优先级 ⭐⭐⭐⭐)
- **用途**: 股吧实盘帖、组合数据
- **注册**: https://guba.eastmoney.com/
- **必需**: ✅ 是 (重要补充)

### 雪球 (优先级 ⭐⭐⭐)
- **用途**: 投资组合、大 V 实盘
- **注册**: https://xueqiu.com/
- **必需**: ⭕ 可选 (有更好)

---

## 验证配置

配置完成后运行:

```bash
cd ~/.openclaw/workspace-hanli/skills/trading-pattern-miner
python3 scripts/test_login.py
```

---

## 安全说明

1. **文件权限**: `.credentials` 文件设置为仅自己可读 (chmod 600)
2. **不上传 Git**: 已添加到 `.gitignore`
3. **不分享**: 不要将此文件发送给任何人
4. **定期更换密码**: 建议每 3 个月更换一次

---

## 下一步

配置好账号后运行:

```bash
# 1. 测试登录
python3 scripts/test_login.py

# 2. 爬取淘股吧实盘数据
python3 scripts/crawl_taoguba.py --limit 100

# 3. 爬取东财实盘数据
python3 scripts/crawl_eastmoney.py --limit 100

# 4. 提取交易模式
python3 scripts/extract_patterns.py
```

---

**聪哥，请选择配置方式并填写账号信息，完成后告诉我，我帮你测试登录和爬取数据！**
