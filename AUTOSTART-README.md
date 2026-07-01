# OpenClaw 自动启动与更新配置

## 📋 配置完成时间
2026-03-03 20:02

---

## ✅ 已配置项目

### 1. 开机自动启动 Gateway
**LaunchAgent**: `ai.openclaw.gateway-autostart`  
**脚本**: `~/.openclaw/scripts/start-gateway.sh`  
**触发时机**: 登录时自动启动（延迟 10 秒）  
**日志**: `~/.openclaw/logs/gateway-autostart.log`

### 2. 每日版本检查更新
**LaunchAgent**: `ai.openclaw.daily-update`  
**脚本**: `~/.openclaw/scripts/update-openclaw.sh`  
**执行时间**: 每天早上 10:00  
**日志**: `~/.openclaw/logs/update-check.log`  
**通知**: macOS 系统通知（更新成功/失败时）

---

## 📂 文件清单

```
/Users/dfq/
├── .openclaw/
│   ├── scripts/
│   │   ├── start-gateway.sh      # 开机启动脚本
│   │   └── update-openclaw.sh    # 每日更新脚本
│   └── logs/
│       ├── gateway-autostart.log
│       ├── gateway-autostart.err
│       ├── update-check.log
│       └── update-check.err
└── Library/LaunchAgents/
    ├── ai.openclaw.gateway-autostart.plist
    └── ai.openclaw.daily-update.plist
```

---

## 🔧 管理命令

### 查看状态
```bash
# 查看 LaunchAgent 状态
launchctl list | grep openclaw

# 查看 Gateway 状态
openclaw gateway status

# 查看启动日志
tail -f ~/.openclaw/logs/gateway-autostart.log

# 查看更新日志
tail -f ~/.openclaw/logs/update-check.log
```

### 手动触发
```bash
# 手动启动 Gateway
~/.openclaw/scripts/start-gateway.sh

# 手动检查更新
~/.openclaw/scripts/update-openclaw.sh

# 手动更新版本
npm update -g openclaw
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

## 📝 注意事项

1. **nvm 环境**: 脚本会自动加载 nvm 环境，确保使用正确的 Node.js 版本
2. **日志轮转**: 日志文件会持续增长，建议定期清理（>100MB 时）
3. **更新通知**: 更新成功/失败时会收到 macOS 系统通知
4. **重启生效**: 开机启动需要重启电脑后生效
5. **测试更新**: 可以手动运行更新脚本测试功能

---

## 🧪 测试建议

```bash
# 1. 测试启动脚本
~/.openclaw/scripts/start-gateway.sh

# 2. 测试更新脚本（不会真的更新，除非有新版本）
~/.openclaw/scripts/update-openclaw.sh

# 3. 查看日志确认
cat ~/.openclaw/logs/gateway-autostart.log
cat ~/.openclaw/logs/update-check.log
```

---

## ⚠️ 故障排查

### Gateway 未自动启动
```bash
# 检查 LaunchAgent 是否加载
launchctl list | grep gateway-autostart

# 查看错误日志
cat ~/.openclaw/logs/gateway-autostart.err

# 手动重新加载
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway-autostart.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway-autostart.plist
```

### 更新未执行
```bash
# 检查 LaunchAgent 状态
launchctl list | grep daily-update

# 手动执行一次
~/.openclaw/scripts/update-openclaw.sh

# 查看日志
cat ~/.openclaw/logs/update-check.log
```

---

配置完成！重启电脑后会自动启动 Gateway，每天早上 10 点自动检查更新 🎉
