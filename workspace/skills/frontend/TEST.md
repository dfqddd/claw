# Skill 测试指南

验证 `frontend-react-icejs` Skill 是否正常工作。

## 快速测试

在 Claude Code 中尝试以下问题，应该会触发此 Skill：

### 1. 查看可用 Skills
```
有哪些可用的 Skills？
```

**预期结果**: 应该列出 `frontend-react-icejs` Skill

### 2. 创建 React 组件
```
创建一个用户列表页面，使用 Ant Design Table 组件，支持分页和搜索
```

**预期结果**: 
- 使用 TypeScript
- 使用 Ant Design 5+ 组件
- 包含类型定义
- 使用 ICE request 进行 API 调用

### 3. 配置请求拦截器
```
如何配置 IceJS v3 的请求拦截器，添加 token 认证？
```

**预期结果**: 
- 提供 app.tsx 配置示例
- 使用 defineAppConfig
- 配置 request.interceptors

### 4. 集成 ECharts
```
帮我实现一个销售趋势图表组件，使用 ECharts
```

**预期结果**:
- 封装的 Chart 组件
- EChartsOption 类型定义
- 响应式处理

### 5. 微前端配置
```
如何使用 icestark 配置微前端主应用？
```

**预期结果**:
- AppRouter 和 AppRoute 配置
- 生命周期钩子
- 应用间通信方案

### 6. AEM 监控集成
```
如何集成 AEM 前端监控平台？
```

**预期结果**:
- initAEM 配置
- 错误上报
- 性能监控

## 验证 Skill 规范

### YAML Frontmatter 检查

```bash
head -5 .claude/skills/frontend-react-icejs/SKILL.md
```

应该看到：
```yaml
---
name: frontend-react-icejs
description: 企业级前端开发规范，使用 React 18+、TypeScript...
---
```

### 文件结构检查

```bash
ls -la .claude/skills/frontend-react-icejs/
```

应该包含：
- SKILL.md (必需)
- reference.md (可选)
- examples.md (可选)
- TEST.md (此文件)

## 常见触发关键词

此 Skill 应该在以下关键词出现时被触发：

- React, TypeScript, Ant Design, Antd
- IceJS, Ice
- tnpm
- icestark, 微前端
- AEM, 监控
- ECharts, 图表
- 前端项目, 前端开发
- 组件, 页面, 路由
- API, 请求, 接口

## Skill 激活确认

当 Skill 被激活时，Claude 应该：

1. ✅ 使用 React 18+ 和 TypeScript
2. ✅ 使用 Ant Design 5+ 组件
3. ✅ 使用 IceJS v3 框架约定
4. ✅ 使用 tnpm 作为包管理器
5. ✅ 使用 ICE 内置请求方案
6. ✅ 提供类型安全的代码
7. ✅ 遵循项目结构规范

## 故障排除

### 如果 Skill 未被触发

1. **检查 description 是否包含足够的关键词**
   ```bash
   grep "description:" .claude/skills/frontend-react-icejs/SKILL.md
   ```

2. **验证 YAML 格式**
   - 确保有开始和结束的 `---`
   - 没有 Tab 字符，只有空格
   - 字符串无需引号（除非包含特殊字符）

3. **确认文件位置**
   ```bash
   # 项目级 Skill
   ls .claude/skills/frontend-react-icejs/SKILL.md
   
   # 或个人级 Skill
   ls ~/.claude/skills/frontend-react-icejs/SKILL.md
   ```

4. **重启 Claude Code**
   - 有时需要重启以重新加载 Skills

## 反馈和改进

测试过程中如果发现问题：

1. **Skill 未被触发**: 在 description 中添加更多相关关键词
2. **信息不足**: 在 reference.md 或 examples.md 中补充
3. **示例不清晰**: 在 examples.md 中添加更详细的示例
4. **冲突**: 调整 description 使其更具特异性

## 成功标准

Skill 正常工作的标志：

- ✅ Claude 能识别并使用此 Skill
- ✅ 生成的代码符合技术栈规范
- ✅ 使用正确的包管理器（tnpm）
- ✅ 代码类型安全（TypeScript）
- ✅ 遵循最佳实践
- ✅ 提供完整可用的代码示例

## 持续改进

根据使用反馈：

1. 记录常见问题并添加到 SKILL.md
2. 补充更多实用示例到 examples.md
3. 更新 reference.md 中的最新配置
4. 优化 description 提高触发准确度

