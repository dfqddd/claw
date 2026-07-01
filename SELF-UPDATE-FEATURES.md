# OpenClaw 自启动 + 自动更新功能文档

**创建时间**: 2026-03-03 20:30  
**创建者**: 厉飞雨 ⚡

---

## 📋 功能概述

| 功能 | 触发时机 | 说明 |
|------|---------|------|
| 开机自启 | 登录系统时 | 自动启动 Gateway 服务 |
| 每日更新 | 每天 10:00 | 检查并更新到最新版本 |

---

## 📂 创建的文件清单

### 1️⃣ 核心脚本

#### `/Users/dfq/.openclaw/scripts/self-update.sh` ⭐
**功能**: OpenClaw 自我更新脚本（独立运行）

**关键特性**:
- 通过 `nohup + &` 后台执行，独立于 Gateway
- 完整流程：检查版本 → stop → update → start → 验证
- 失败自动回滚
- macOS 系统通知

**执行流程**:
```bash
1. 检查当前版本
2. 检查 npm 最新版本
3. 停止 Gateway（安全更新）
4. npm install -g openclaw@latest
5. 启动 Gateway
6. 验证状态 + 发送通知
```

---

#### `/Users/dfq/.openclaw/scripts/start-gateway.sh`
**功能**: 开机启动 Gateway 脚本

**关键特性**:
- 自动加载 nvm 环境
- 检查 Gateway 状态（避免重复启动）
- 验证端口监听

---

#### `/Users/dfq/.openclaw/scripts/update-openclaw.sh`
**功能**: 旧版更新脚本（已废弃，保留备份）

**状态**: ⚠️ 不再使用，被 `self-update.sh` 替代

---

### 2️⃣ LaunchAgent 配置

#### `/Users/dfq/Library/LaunchAgents/ai.openclaw.gateway-autostart.plist`
**功能**: 开机自启配置

**触发条件**: `RunAtLoad = true`（登录即启动）

**关键配置**:
```xml
<key>RunAtLoad</key>
<true/>
<key>KeepAlive</key>
<dict>
    <key>Crashed</key>
    <true/>
</dict>
```

---

#### `/Users/dfq/Library/LaunchAgents/ai.openclaw.daily-update.plist` ⭐
**功能**: 每日自动更新配置

**触发时间**: 每天 10:00

**关键配置**:
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>10</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
<key>ProgramArguments</key>
<array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>nohup /bin/bash -l /Users/dfq/.openclaw/scripts/self-update.sh >/dev/null 2>&1 &</string>
</array>
```

**核心设计**: 使用 `nohup + &` 确保脚本独立于 Gateway 运行

---

### 3️⃣ 日志文件

**目录**: `/Users/dfq/.openclaw/logs/`

| 日志文件 | 说明 |
|---------|------|
| `gateway-autostart.log` | 开机启动日志 |
| `gateway-startup.log` | 手动启动日志 |
| `self-update.log` | 自动更新日志 ⭐ |
| `update-check.log` | 旧版更新检查日志 |
| `gateway.log` | Gateway 主日志 |
| `gateway.err.log` | Gateway 错误日志 |

---

### 4️⃣ 文档

#### `/Users/dfq/.openclaw/AUTOSTART-README.md`
**功能**: 配置说明文档（第一版）

#### `/Users/dfq/.openclaw/SELF-UPDATE-FEATURES.md` ⭐
**功能**: 本文档（完整版）

---

## 🔧 管理命令

### 查看状态
```bash
# 查看 LaunchAgent 状态
launchctl list | grep openclaw

# 查看 Gateway 状态
openclaw gateway status

# 查看自启动日志
tail -f ~/.openclaw/logs/gateway-autostart.log

# 查看更新日志
tail -f ~/.openclaw/logs/self-update.log
```

### 手动触发
```bash
# 手动启动 Gateway
~/.openclaw/scripts/start-gateway.sh

# 手动更新（测试用）
nohup ~/.openclaw/scripts/self-update.sh > /tmp/test-update.log 2>&1 &
```

### 禁用/启用
```bash
# 禁用开机启动
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway-autostart.plist

# 启用开机启动
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway-autostart.plist

# 禁用每日更新
launchctl unload ~/Library/LaunchAgents/ai.openclaw.daily-update.plist

# 启用每日更新
launchctl load ~/Library/LaunchAgents/ai.openclaw.daily-update.plist
```

---

## 🎯 核心设计思路

### 问题：为什么需要独立脚本？

**错误方案** ❌:
```bash
# Gateway 自己执行更新
openclaw gateway stop
npm install -g openclaw  # ← Gateway 停了，谁来继续执行？
openclaw gateway start   # ← 无法执行到这里！
```

**正确方案** ✅:
```bash
# LaunchAgent 触发独立脚本
nohup self-update.sh &  # ← 后台运行，独立于 Gateway

# 脚本内部流程
openclaw gateway stop   # ← 停 Gateway
npm install -g openclaw # ← 更新 npm 包
openclaw gateway start  # ← 重启 Gateway
```

---

## 📊 运行状态

```
当前状态 (2026-03-03 20:30):
├── Gateway: ✅ 运行中 (pid 91607)
├── 开机自启: ✅ 已加载 (ai.openclaw.gateway-autostart)
├── 每日更新: ✅ 已加载 (ai.openclaw.daily-update)
└── 当前版本: ✅ 2026.3.2 (最新)
```

---

## ⚠️ 注意事项

1. **日志清理**: 日志文件会持续增长，建议定期清理（>100MB 时）
2. **重启生效**: 开机启动需要重启电脑后验证
3. **通知权限**: macOS 通知需要系统权限（首次运行时授予）
4. **网络依赖**: 更新需要网络连接（npm registry）

---

## 🧪 测试建议

```bash
# 1. 测试开机启动（重启电脑）
# 重启后检查：
openclaw gateway status

# 2. 测试每日更新（修改触发时间）
# 临时修改 plist 为 1 分钟后触发，观察日志

# 3. 测试手动更新
nohup ~/.openclaw/scripts/self-update.sh > /tmp/test.log 2>&1 &
tail -f ~/.openclaw/logs/self-update.log
```

---

## 📝 更新历史

| 日期 | 变更 | 说明 |
|------|------|------|
| 2026-03-03 20:02 | 初始版本 | 创建开机自启 + 每日更新 |
| 2026-03-03 20:23 | 修复更新逻辑 | 修正 npm 更新命令 |
| 2026-03-03 20:27 | 重构为独立脚本 | 使用 nohup + & 后台执行 |
| 2026-03-03 20:30 | 完善文档 | 创建本文档 |

---

**配置完成！重启电脑后自动生效** 🎉
