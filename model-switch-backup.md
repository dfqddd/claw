# 模型切换记录

## 2026-03-24 17:12 - 切换到 DogFooding 模型

### 切换前
- **模型**: `bailian/qwen3.5-plus`（通义千问 3.5 Plus）

### 切换后
- **模型**: `custom-dogfooding/pitaya-03-20`（DogFooding 测试模型）

---

## 🔄 如何切回原模型

### 方法 1：修改配置文件
编辑 `~/.openclaw/openclaw.json`，找到 `hanli` agent：
```json
{
  "id": "hanli",
  "model": {
    "primary": "bailian/qwen3.5-plus"  // 改回这个
  }
}
```

然后重启：
```bash
openclaw gateway restart
```

### 方法 2：使用命令（临时）
在当前会话：
```
/models bailian/qwen3.5-plus
```

---

## 📋 可用模型列表

| 模型 | 说明 | 切换命令 |
|------|------|---------|
| `custom-dogfooding/pitaya-03-20` | DogFooding 测试模型（当前） | `/models custom-dogfooding/pitaya-03-20` |
| `bailian/qwen3.5-plus` | 通义千问 3.5 Plus（原配置） | `/models bailian/qwen3.5-plus` |
| `bailian/qwen-plus` | 通义千问 Plus | `/models bailian/qwen-plus` |

---

**创建时间**: 2026-03-24 17:12
