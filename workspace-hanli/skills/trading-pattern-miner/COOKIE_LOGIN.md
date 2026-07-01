# 淘股吧 Cookie 登录方案

**问题**: 短信验证码每次都要输入，太麻烦  
**解决**: 登录一次后保存 Cookie，以后自动使用

---

## 方案 A: 手动提取 Cookie（推荐）

### 步骤 1: 浏览器登录

1. 打开 https://www.tgb.cn/login
2. 用手机号 + 验证码登录
3. 登录成功后按 F12 打开开发者工具

### 步骤 2: 提取 Cookie

在浏览器控制台运行：
```javascript
// 复制所有 Cookie
console.log(document.cookie);
```

或者手动查找：
1. F12 → Application → Cookies → https://www.tgb.cn
2. 复制以下 Cookie：
   - `TB_TOKEN`
   - `user_id`
   - `username`

### 步骤 3: 保存 Cookie

创建文件 `~/.openclaw/workspace-hanli/skills/trading-pattern-miner/.cookies`:

```ini
[taoguba]
TB_TOKEN=你的 TB_TOKEN
user_id=你的 user_id
username=你的 username
```

设置权限：
```bash
chmod 600 ~/.openclaw/workspace-hanli/skills/trading-pattern-miner/.cookies
```

---

## 方案 B: 浏览器插件自动提取

安装 Cookie 编辑器插件：
- Chrome: "EditThisCookie"
- Firefox: "Cookies.txt"

登录后点击插件 → 导出 Cookie → 保存到 `.cookies` 文件

---

## 使用 Cookie 登录

保存好 Cookie 后运行：
```bash
cd ~/.openclaw/workspace-hanli/skills/trading-pattern-miner
python3 scripts/crawl_taoguba.py --use-cookies
```

---

## Cookie 有效期

- **TB_TOKEN**: 通常 30-90 天
- **过期后**: 重新登录一次，更新 Cookie

---

## 安全提示

1. **不要分享** `.cookies` 文件
2. **已添加到** `.gitignore`
3. **权限设置** 为 600（仅自己可读）
4. **定期更新** Cookie（过期后）

---

**聪哥，你现在登录一次，然后按上面步骤提取 Cookie 保存，以后就不需要验证码了！**
