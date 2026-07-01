# 自定义技能管理指南

**创建时间**: 2026-03-04  
**聪哥指示**: 区分市场技能和自定义技能

---

## 📋 技能分类

### 1. 市场技能（Market Skills）
**定义**: 从市场安装的原始技能，包括：
- 阿里内部技能（如 yuque-kit）
- ClawHub 技能（如 free-a-stock）
- 其他公开技能

**特点**:
- ✅ 可以自动更新
- ✅ 从市场源安装
- ❌ 不建议直接修改（会被更新覆盖）

**管理方式**:
```bash
# 每周一 9:00 自动检查更新
~/.openclaw/scripts/skill-update.sh
```

---

### 2. 自定义技能（Custom Skills）
**定义**: 我们**创建或修改过**的技能，包括：
- 从头创建的技能
- 修改过的市场技能
- 优化过的技能逻辑

**特点**:
- ❌ 不自动更新（保护修改）
- ✅ 备份到 `~/.openclaw/skills/custom/`
- ✅ 有版本记录

**示例**:
- `free-a-stock` - 昨天更新过，需要备份保护

---

## 🎯 使用场景

### 场景 1: 修改了市场技能
```bash
# 1. 修改技能文件
vim ~/.openclaw/workspace/skills/free-a-stock/SKILL.md

# 2. 备份到自定义库（保护修改）
~/.openclaw/scripts/custom-skill-backup.sh backup free-a-stock "修改了查询逻辑"

# 3. 验证
~/.openclaw/scripts/custom-skill-backup.sh list
```

**效果**:
- 工作区技能：继续正常使用
- 自定义库：保存修改版本
- 周一更新：跳过此技能（因为已在自定义库）

---

### 场景 2: 创建新技能
```bash
# 1. 在 workspace 创建技能
mkdir -p ~/.openclaw/workspace/skills/my-skill
# ... 创建技能文件 ...

# 2. 备份到自定义库
~/.openclaw/scripts/custom-skill-backup.sh backup my-skill "聪哥要求创建的 XXX 技能"

# 3. 验证
~/.openclaw/scripts/custom-skill-backup.sh list
```

---

### 场景 3: 恢复修改
```bash
# 如果改坏了，从自定义库恢复
~/.openclaw/scripts/custom-skill-backup.sh restore free-a-stock
```

---

### 场景 4: 比较差异
```bash
# 查看工作区和自定义库的差异
~/.openclaw/scripts/custom-skill-backup.sh diff free-a-stock
```

---

## 📂 目录结构

```
~/.openclaw/
├── workspace/skills/              # 工作区（所有技能都在这里）
│   ├── yuque-kit/                 # 市场技能（阿里内部）
│   ├── free-a-stock/              # 市场技能（已修改）
│   └── ...
│
├── skills/
│   ├── custom/                    # ⭐ 自定义技能库
│   │   ├── free-a-stock/          # 备份的修改版本
│   │   └── .backup/               # 旧版本备份
│   ├── market/                    # 市场技能备份
│   └── config/
│       └── skills-registry.json   # 技能注册表
│
└── scripts/
    ├── skill-update.sh            # 市场技能更新
    ├── custom-skill-backup.sh     # ⭐ 自定义技能备份
    └── skill-manager.sh           # 技能管理
```

---

## 🔧 管理命令

### 自定义技能备份
```bash
# 备份技能到自定义库
~/.openclaw/scripts/custom-skill-backup.sh backup <技能名> [备注]

# 示例
~/.openclaw/scripts/custom-skill-backup.sh backup free-a-stock "更新了查询接口"
~/.openclaw/scripts/custom-skill-backup.sh backup yuque-kit "修改了同步逻辑"
```

### 列出自定义技能
```bash
~/.openclaw/scripts/custom-skill-backup.sh list
```

### 恢复技能
```bash
~/.openclaw/scripts/custom-skill-backup.sh restore <技能名>
```

### 比较差异
```bash
~/.openclaw/scripts/custom-skill-backup.sh diff <技能名>
```

---

## 📊 技能注册表

**文件**: `~/.openclaw/skills/config/skills-registry.json`

**结构**:
```json
{
  "version": "1.0",
  "marketSkills": [
    {
      "name": "yuque-kit",
      "source": "contextlab",
      "path": "~/.openclaw/workspace/skills/yuque-kit",
      "note": "阿里内部技能"
    },
    {
      "name": "free-a-stock",
      "source": "clawhub",
      "path": "~/.openclaw/workspace/skills/free-a-stock",
      "note": "免费 A 股查询"
    }
  ],
  "customSkills": [
    {
      "name": "free-a-stock",
      "path": "~/.openclaw/skills/custom/free-a-stock",
      "backupDate": "20260304-145229",
      "note": "2026-03-03 更新：免费 A 股数据查询",
      "createdAt": "2026-03-04 14:52:29"
    }
  ]
}
```

---

## 🔄 更新流程

### 周一自动更新（9:00）
```
1. 读取技能注册表
   ↓
2. 获取市场技能列表
   ↓
3. 检查每个市场技能的新版本
   ↓
4. 有新版本 → 备份 → 更新 → 验证
   ↓
5. 自定义技能 → 跳过（保护修改）
   ↓
6. 发送通知
```

### 手动更新
```bash
# 手动执行一次
~/.openclaw/scripts/skill-update.sh

# 查看日志
tail -50 ~/.openclaw/logs/skill-update.log
```

---

## ✅ 最佳实践

### 1. 修改前先备份
```bash
# 修改技能文件前，先备份当前版本
~/.openclaw/scripts/custom-skill-backup.sh backup skill-name "修改前的版本"
```

### 2. 修改后更新备份
```bash
# 修改完成后，更新自定义库
~/.openclaw/scripts/custom-skill-backup.sh backup skill-name "修改内容说明"
```

### 3. 定期检查差异
```bash
# 看看工作区和自定义库有什么不同
~/.openclaw/scripts/custom-skill-backup.sh diff skill-name
```

### 4. 清理旧备份
```bash
# 保留最近 10 个备份
ls -t ~/.openclaw/skills/custom/.backup/ | tail -n +11 | xargs -I {} rm -rf "~/.openclaw/skills/custom/.backup/{}"
```

---

## 📝 当前状态

### 市场技能
| 技能名 | 来源 | 版本 | 状态 |
|--------|------|------|------|
| yuque-kit | contextlab | 0.2.0 | ✅ 正常 |
| free-a-stock | clawhub | - | ⚠️ 已修改 |

### 自定义技能
| 技能名 | 备份时间 | 备注 |
|--------|---------|------|
| free-a-stock | 2026-03-04 14:52 | 2026-03-03 更新：免费 A 股数据查询 |

---

## ⚠️ 注意事项

1. **自定义技能不自动更新**
   - 如果需要市场新版本，手动恢复后重新备份

2. **备份会占用空间**
   - 定期清理 `.backup/` 目录

3. **修改前一定要备份**
   - 避免改坏后无法恢复

4. **备注要清晰**
   - 说明修改了什么，方便后续 review

---

## 🔗 相关文档

- [技能管理系统](SKILL-MANAGEMENT.md)
- [复盘系统](REVIEW-SYSTEM.md)
- [自启动配置](AUTOSTART-README.md)

---

_自定义技能管理 v1.0 | 最后更新：2026-03-04_
