# OpenClaw 定时任务清单

**更新时间**: 2026-03-04 15:05  
**状态**: ✅ 全部已创建并加载

---

## 📋 任务总览

| 序号 | 任务名称 | 执行时间 | 脚本 | 状态 |
|------|---------|---------|------|------|
| 1 | 每日复盘 | 每天 21:00 | `daily-review.sh` | ✅ 已加载 |
| 2 | 每周回顾 | 每周日 20:00 | `weekly-review.sh` | ✅ 已加载 |
| 3 | 每月升级 | 每月最后一天 20:00 | `monthly-upgrade.sh` | ✅ 已加载 |
| 4 | 自动更新 | 每天 10:00 | `self-update.sh` | ✅ 已加载 |
| 5 | 技能更新 | 每周一 9:00 | `skill-update.sh` | ✅ 已加载 |
| 6 | 开机自启 | 登录时 | `start-gateway.sh` | ✅ 已加载 |

---

## 🔧 详细配置

### 1. 每日复盘 ⭐
**LaunchAgent**: `ai.openclaw.daily-review`  
**执行时间**: 每天 21:00  
**脚本**: `~/.openclaw/scripts/daily-review.sh`  
**输出**: `~/.openclaw/reviews/YYYY-MM-DD-review.md`  
**日志**: `~/.openclaw/logs/daily-review.log`

**功能**:
- 记录当日工作
- 统计 Gateway 运行状态
- 记录问题与改进
- 生成明日计划

---

### 2. 每周回顾 ⭐
**LaunchAgent**: `ai.openclaw.weekly-review`  
**执行时间**: 每周日 20:00  
**脚本**: `~/.openclaw/scripts/weekly-review.sh`  
**输出**: `~/.openclaw/reviews/YYYY-MM-DD-weekly-summary.md`  
**日志**: `~/.openclaw/logs/weekly-review.log`

**功能**:
- 汇总 7 篇每日复盘
- 提炼共性问题
- 生成改进建议
- 规划下周重点

---

### 3. 每月升级 ⭐
**LaunchAgent**: `ai.openclaw.monthly-upgrade`  
**执行时间**: 每月最后一天 20:00  
**脚本**: `~/.openclaw/scripts/monthly-upgrade.sh`  
**输出**: `~/.openclaw/reviews/YYYY-MM-monthly-summary.md`  
**日志**: `~/.openclaw/logs/monthly-upgrade.log`

**功能**:
- 汇总当月所有复盘
- 提炼核心经验
- 更新 SOUL.md/TOOLS.md
- 规划下月重点

---

### 4. 自动更新 ⭐
**LaunchAgent**: `ai.openclaw.daily-update`  
**执行时间**: 每天 10:00  
**脚本**: `~/.openclaw/scripts/self-update.sh`  
**日志**: `~/.openclaw/logs/self-update.log`

**功能**:
- 检查 npm 最新版本
- 停止 Gateway → 更新 → 启动
- 验证状态 + 发送通知

**流程**:
```
1. 检查版本
2. stop Gateway
3. npm install -g openclaw@latest
4. start Gateway
5. 验证 + 通知
```

---

### 5. 技能更新 ⭐
**LaunchAgent**: `ai.openclaw.weekly-skill-update`  
**执行时间**: 每周一 9:00  
**脚本**: `~/.openclaw/scripts/skill-update.sh`  
**日志**: `~/.openclaw/logs/skill-update.log`

**功能**:
- 检查市场技能更新
- 跳过自定义技能
- 备份 → 更新 → 验证
- 失败自动回滚

**技能分类**:
- **市场技能**: yuque-kit, free-a-stock → ✅ 自动更新
- **自定义技能**: 修改过的技能 → ❌ 跳过保护

---

### 6. 开机自启 ⭐
**LaunchAgent**: `ai.openclaw.gateway-autostart`  
**执行时间**: 登录时  
**脚本**: `~/.openclaw/scripts/start-gateway.sh`  
**日志**: `~/.openclaw/logs/gateway-autostart.log`

**功能**:
- 加载 nvm 环境
- 检查 Gateway 状态
- 未运行则启动
- 验证端口监听

---

## 📊 LaunchAgent 状态

```bash
# 查看所有任务状态
launchctl list | grep "ai.openclaw"

# 当前状态 (2026-03-04 15:05):
-	0	ai.openclaw.daily-update          # ✅ 已加载
-	0	ai.openclaw.gateway-autostart     # ✅ 已加载
-	0	ai.openclaw.daily-review          # ✅ 已加载
-	0	ai.openclaw.weekly-review         # ✅ 已加载
-	0	ai.openclaw.monthly-upgrade       # ✅ 已加载
-	0	ai.openclaw.weekly-skill-update   # ✅ 已加载
95227	0	ai.openclaw.gateway               # ✅ 运行中
```

---

## 📂 文件位置

```
~/Library/LaunchAgents/
├── ai.openclaw.daily-review.plist       # 每日复盘
├── ai.openclaw.weekly-review.plist      # 每周回顾
├── ai.openclaw.monthly-upgrade.plist    # 每月升级
├── ai.openclaw.daily-update.plist       # 自动更新
├── ai.openclaw.weekly-skill-update.plist # 技能更新
└── ai.openclaw.gateway-autostart.plist  # 开机自启

~/.openclaw/scripts/
├── daily-review.sh          # 每日复盘脚本
├── weekly-review.sh         # 每周回顾脚本
├── monthly-upgrade.sh       # 每月升级脚本
├── self-update.sh           # 自动更新脚本
├── skill-update.sh          # 技能更新脚本
├── skill-manager.sh         # 技能管理脚本
├── custom-skill-backup.sh   # 自定义技能备份
└── start-gateway.sh         # 开机启动脚本
```

---

## 🔧 管理命令

### 查看状态
```bash
# 查看所有任务
launchctl list | grep "ai.openclaw"

# 查看某个任务详情
launchctl list | grep "daily-review"
```

### 禁用/启用
```bash
# 禁用
launchctl unload ~/Library/LaunchAgents/ai.openclaw.daily-review.plist

# 启用
launchctl load ~/Library/LaunchAgents/ai.openclaw.daily-review.plist
```

### 手动触发
```bash
# 每日复盘
~/.openclaw/scripts/daily-review.sh

# 每周回顾
~/.openclaw/scripts/weekly-review.sh

# 每月升级
~/.openclaw/scripts/monthly-upgrade.sh

# 自动更新
~/.openclaw/scripts/self-update.sh

# 技能更新
~/.openclaw/scripts/skill-update.sh

# 开机启动
~/.openclaw/scripts/start-gateway.sh
```

### 查看日志
```bash
# 实时查看
tail -f ~/.openclaw/logs/daily-review.log
tail -f ~/.openclaw/logs/skill-update.log

# 查看最近 100 行
tail -100 ~/.openclaw/logs/weekly-review.log
```

---

## 📅 执行时间表

```
每天:
├── 10:00 → 自动更新 (self-update.sh)
└── 21:00 → 每日复盘 (daily-review.sh)

每周:
├── 周一 9:00 → 技能更新 (skill-update.sh)
└── 周日 20:00 → 每周回顾 (weekly-review.sh)

每月:
└── 最后一天 20:00 → 每月升级 (monthly-upgrade.sh)

每次开机:
└── 登录时 → Gateway 自启动 (start-gateway.sh)
```

---

## ✅ 验证方法

### 1. 检查文件是否存在
```bash
ls -la ~/Library/LaunchAgents/ai.openclaw.*.plist
ls -la ~/.openclaw/scripts/*.sh
```

### 2. 检查是否加载
```bash
launchctl list | grep "ai.openclaw"
```

### 3. 测试执行
```bash
# 手动执行一次，看是否正常工作
~/.openclaw/scripts/daily-review.sh
```

### 4. 查看日志
```bash
# 看是否有输出
tail -20 ~/.openclaw/logs/daily-review.log
```

---

## ⚠️ 注意事项

1. **日志轮转**
   - 日志文件会持续增长
   - 建议每月清理一次（保留最近 100MB）

2. **备份清理**
   - 技能更新备份保留最近 10 次
   - 复盘文件建议按年归档

3. **通知权限**
   - macOS 通知需要首次授权
   - 如果没收到通知，检查系统设置

4. **网络依赖**
   - 自动更新需要 npm 网络
   - 技能更新需要内网（contextlab）

---

## 📝 创建历史

| 日期 | 任务 | 说明 |
|------|------|------|
| 2026-03-03 20:03 | 开机自启 | Gateway 登录自启动 |
| 2026-03-03 20:28 | 自动更新 | 每天 10:00 检查更新 |
| 2026-03-03 21:52 | 每日复盘 | 每天 21:00 复盘 |
| 2026-03-03 22:11 | 每周回顾 | 每周日 20:00 回顾 |
| 2026-03-03 22:11 | 每月升级 | 每月最后一天 20:00 |
| 2026-03-04 14:27 | 技能更新 | 每周一 9:00 更新技能 |

---

_所有定时任务已创建并加载 | 最后更新：2026-03-04 15:05_
