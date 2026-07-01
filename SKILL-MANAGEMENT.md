# OpenClaw 技能管理系统

**创建时间**: 2026-03-04  
**创建者**: 厉飞雨 ⚡

---

## 🎯 系统目标

1. **区分自定义技能和市场技能**
2. **自动更新市场技能，保护自定义技能**
3. **版本管理 + 备份恢复机制**

---

## 📂 目录结构

```
~/.openclaw/
├── workspace/skills/           # 技能工作目录（所有技能都在这里）
│   ├── yuque-kit/              # 语雀技能
│   └── ...                     # 其他技能
│
├── skills/                     # 技能管理目录
│   ├── custom/                 # 自定义技能（备份/模板）
│   ├── market/                 # 市场技能备份
│   └── config/
│       └── skills-registry.json  # 技能注册表
│
└── scripts/
│   ├── skill-update.sh         # 技能更新脚本
│   └── skill-manager.sh        # 技能管理脚本
```

---

## 🔧 管理命令

### 1. 技能管理脚本 (`skill-manager.sh`)

```bash
# 添加自定义技能
~/.openclaw/scripts/skill-manager.sh add <技能名> [来源] [备注]

# 示例
~/.openclaw/scripts/skill-manager.sh add my-custom-skill local "聪哥自定义的技能"
~/.openclaw/scripts/skill-manager.sh add yuque-kit contextlab "从 contextlab 安装"

# 移除自定义技能
~/.openclaw/scripts/skill-manager.sh remove <技能名>

# 列出所有自定义技能
~/.openclaw/scripts/skill-manager.sh list

# 添加到自动更新排除列表
~/.openclaw/scripts/skill-manager.sh exclude <技能名>

# 从排除列表移除
~/.openclaw/scripts/skill-manager.sh include <技能名>
```

### 2. 技能更新脚本 (`skill-update.sh`)

```bash
# 手动执行更新
~/.openclaw/scripts/skill-update.sh

# 查看更新日志
tail -f ~/.openclaw/logs/skill-update.log

# 查看备份
ls -la ~/.openclaw/skills/market/
```

---

## 📋 技能注册表

**文件位置**: `~/.openclaw/skills/config/skills-registry.json`

**结构**:
```json
{
  "version": "1.0",
  "lastUpdate": "2026-03-04 14:27:53",
  "customSkills": [
    {
      "name": "yuque-kit",
      "source": "contextlab",
      "path": "~/.openclaw/workspace/skills/yuque-kit",
      "modified": true,
      "note": "从 contextlab 安装，版本 0.2.0",
      "createdAt": "2026-03-04 14:27:53"
    }
  ],
  "marketSkills": [],
  "excludeFromAutoUpdate": ["yuque-kit"]
}
```

**字段说明**:
| 字段 | 说明 |
|------|------|
| `customSkills` | 自定义技能列表 |
| `marketSkills` | 市场技能列表（未来扩展） |
| `excludeFromAutoUpdate` | 排除自动更新的技能 |
| `lastUpdate` | 最后更新时间 |

---

## 🔄 自动更新流程

### 执行时间
**每周一 9:00** 自动执行

### 流程
```
1. 读取技能注册表
   ↓
2. 备份当前所有技能
   ↓
3. 检查每个市场技能（排除自定义技能）
   ↓
4. 对比版本 → 有新版本则更新
   ↓
5. 更新失败则恢复备份
   ↓
6. 更新注册表
   ↓
7. 发送通知
```

### 安全机制
1. **更新前备份** - 每次更新前完整备份
2. **失败回滚** - 更新失败自动恢复旧版本
3. **排除保护** - 自定义技能不自动更新
4. **日志记录** - 详细记录每个步骤

---

## 📊 技能分类

### 自定义技能（排除自动更新）
| 技能名 | 来源 | 说明 |
|--------|------|------|
| yuque-kit | contextlab | 语雀知识库管理，版本 0.2.0 |

### 市场技能（自动更新）
| 技能名 | 来源 | 说明 |
|--------|------|------|
| (暂无) | - | - |

---

## 🎯 使用场景

### 场景 1: 安装新技能
```bash
# 1. 从市场安装
npm config set registry <YOUR_SKILL_REGISTRY_URL>
npm install skill-name@latest

# 2. 复制到 workspace
cp -r node_modules/skill-name ~/.openclaw/workspace/skills/

# 3. 注册为自定义技能
~/.openclaw/scripts/skill-manager.sh add skill-name contextlab "备注"
```

### 场景 2: 修改技能
```bash
# 1. 修改技能文件
vim ~/.openclaw/workspace/skills/skill-name/xxx.py

# 2. 标记为自定义（如果还不是）
~/.openclaw/scripts/skill-manager.sh add skill-name custom "已修改"

# 3. 验证排除
~/.openclaw/scripts/skill-manager.sh list
```

### 场景 3: 恢复技能
```bash
# 从备份恢复
BACKUP_DIR=~/.openclaw/skills/market/skill-name-20260304
SKILL_DIR=~/.openclaw/workspace/skills/skill-name

rm -rf "${SKILL_DIR}"
cp -r "${BACKUP_DIR}" "${SKILL_DIR}"
```

---

## 📝 日志管理

### 日志位置
- **更新日志**: `~/.openclaw/logs/skill-update.log`
- **错误日志**: `~/.openclaw/logs/skill-update.err`

### 日志清理
```bash
# 清理 30 天前的日志
find ~/.openclaw/logs -name "skill-*.log" -mtime +30 -delete
```

### 备份清理
```bash
# 保留最近 10 次备份
ls -t ~/.openclaw/skills/market/ | tail -n +11 | xargs -I {} rm -rf "~/.openclaw/skills/market/{}"
```

---

## ⚠️ 注意事项

1. **修改技能前先注册**
   - 使用 `skill-manager.sh add` 标记为自定义
   - 避免被自动更新覆盖

2. **定期检查备份**
   - 备份会占用磁盘空间
   - 建议保留最近 10 次

3. **更新失败处理**
   - 查看日志：`tail -100 ~/.openclaw/logs/skill-update.log`
   - 手动恢复：从 `~/.openclaw/skills/market/` 复制备份

4. **内部源访问**
   - contextlab 需要内网环境
   - 更新失败可能是网络问题

---

## 🧪 测试命令

```bash
# 测试技能管理
~/.openclaw/scripts/skill-manager.sh list

# 测试更新（手动执行一次）
~/.openclaw/scripts/skill-update.sh

# 查看 LaunchAgent 状态
launchctl list | grep skill

# 测试通知
osascript -e 'display notification "测试通知" with title "技能管理"'
```

---

## 📅 配置清单

| 项目 | 配置 | 状态 |
|------|------|------|
| 技能管理脚本 | `skill-manager.sh` | ✅ |
| 技能更新脚本 | `skill-update.sh` | ✅ |
| LaunchAgent | `ai.openclaw.weekly-skill-update` | ✅ |
| 执行时间 | 每周一 9:00 | ✅ |
| 注册表 | `skills-registry.json` | ✅ |
| 备份目录 | `skills/market/` | ✅ |

---

## 🔗 相关文档

- [复盘系统](REVIEW-SYSTEM.md)
- [自启动配置](AUTOSTART-README.md)
- [自更新功能](SELF-UPDATE-FEATURES.md)

---

_技能管理系统 v1.0 | 最后更新：2026-03-04_
