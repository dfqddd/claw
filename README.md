# OpenClaw 配置与技能仓库

个人 [OpenClaw](https://github.com/anthropics/openclaw) 实例的配置备份与自定义技能集合。

## 仓库结构

```
.
├── openclaw.json              # 主配置文件（API Key 已脱敏）
├── gateway.env                # 网关环境变量（Token 已脱敏）
├── exec-approvals.json        # 执行审批配置（Token 已脱敏）
├── .gitignore                 # 敏感文件排除规则
│
├── AUTOSTART-README.md        # 开机自启配置说明
├── CUSTOM-SKILL-GUIDE.md      # 自定义技能开发指南
├── REVIEW-SYSTEM.md           # 代码审查系统设计
├── SCHEDULED-TASKS.md         # 定时任务配置说明
├── SELF-UPDATE-FEATURES.md    # 自更新功能说明
├── SKILL-MANAGEMENT.md        # 技能管理手册
├── model-switch-backup.md     # 模型切换备份记录
│
├── workspace/                 # 主 Agent 工作空间
│   └── skills/                # 技能集合
│       ├── 1688-shopkeeper/   # 1688 商品查询
│       ├── a-stock-info/      # A 股行情查询
│       ├── free-a-stock/      # 免费 A 股数据
│       ├── frontend/          # 前端开发辅助
│       ├── productivity/      # 生产力框架集
│       ├── real-hot-list/     # 实时热榜
│       ├── self-improving-agent/  # 自我改进 Agent
│       ├── smart-expense-tracker-cn-v1-1/  # 智能记账
│       ├── superpowers-*/     # 超能力系列（脑暴/调试/计划/执行/并行）
│       ├── tavily-*/          # Tavily 搜索/研究/抓取系列
│       └── yuque-kit/         # 语雀同步工具（见下方说明）
│
└── workspace-hanli/           # 韩立 Agent 工作空间
    └── skills/                # 技能集合
        ├── a-stock-analysis/  # A 股深度分析（含同步调度）
        ├── mx_data/           # 妙想金融数据
        ├── mx_search/         # 妙想资讯搜索
        ├── mx_select_stock/   # 妙想智能选股
        ├── mx_selfselect/     # 妙想自选股
        ├── nuwa-skill/        # 女娲造人（名人视角模拟）
        ├── trading-pattern-miner/  # 交易模式挖掘
        ├── wechatsync/        # 微信公众号多平台同步
        └── ...                # 其他技能（部分与 workspace 共享）
```

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/dfqddd/claw.git ~/.openclaw-backup
```

### 2. 恢复配置

将配置文件复制到 OpenClaw 目录，并替换占位符为你的真实凭证：

```bash
cp openclaw.json ~/.openclaw/openclaw.json
cp gateway.env ~/.openclaw/gateway.env
cp exec-approvals.json ~/.openclaw/exec-approvals.json
```

需要替换的占位符：

| 占位符 | 说明 |
|--------|------|
| `<YOUR_BAILIAN_API_KEY>` | 百炼 DashScope API Key |
| `<YOUR_BAILIAN_INTERNAL_API_KEY>` | 百炼内部 API Key |
| `<YOUR_DOGFOODING_API_KEY>` | DogFooding 模型 API Key |
| `<YOUR_DOGFOODING_BASE_URL>` | DogFooding 模型 Base URL |
| `<YOUR_DINGTALK_CLIENT_SECRET>` | 钉钉机器人 Client Secret |
| `<YOUR_DINGTALK_GATEWAY_TOKEN>` | 钉钉网关 Token |
| `<YOUR_DINGTALK_ACCESS_TOKEN>` | 钉钉 JWT Access Token |
| `<YOUR_GATEWAY_AUTH_TOKEN>` | 本地网关认证 Token |
| `<YOUR_1688_AK>` | 1688 API Key |
| `<YOUR_YUQUE_TOKEN>` | 语雀 API Token |
| `<YOUR_YUQUE_API_URL>` | 语雀 API 地址 |
| `<YOUR_OPENCLAW_SERVER_ADDRESS>` | OpenClaw 服务器地址 |
| `<YOUR_SOCKET_TOKEN>` | 执行审批 Socket Token |
| `<YOUR_SKILL_REGISTRY_URL>` | 技能 Registry URL |

### 3. 安装技能

将所需技能复制到 OpenClaw 的 workspace 目录：

```bash
cp -r workspace/skills/* ~/.openclaw/workspace/skills/
cp -r workspace-hanli/skills/* ~/.openclaw/workspace-hanli/skills/
```

部分技能需要额外配置 `.env` 文件，参考各技能目录下的 `.env.example`。

## 安全说明

本仓库遵循数据安全规范，所有敏感信息已脱敏处理：

- **API Key / Token / Secret**：替换为 `<YOUR_*_KEY>` 占位符
- **内网域名**：替换为 `<YOUR_*_URL>` 占位符
- **设备身份文件**：已排除（含私钥和配对凭证）
- **运行时数据**：已排除（数据库、日志、会话记录等）
- **备份目录**：已排除（含历史敏感数据副本）

以下数据**未包含**在本仓库中：

- `identity/` 和 `devices/`（设备身份与配对凭证）
- `memory/`、`tasks/`、`flows/`（SQLite 数据库）
- `logs/`、`browser/`、`delivery-queue/`（运行时数据）
- `backup-*/`、`skills/market/`（历史备份，约 29G）
- `extensions/`、`plugins/`、`agents/`（已安装扩展与会话数据）

## 技能分类

### 数据查询类

| 技能 | 说明 | 数据源 |
|------|------|--------|
| a-stock-info | A 股实时行情 | 公开 API |
| free-a-stock | 免费 A 股数据 | 公开 API |
| mx_data | 妙想金融数据 | 妙想 API |
| mx_search | 妙想资讯搜索 | 妙想 API |
| mx_select_stock | 妙想智能选股 | 妙想 API |
| mx_selfselect | 妙想自选股管理 | 妙想 API |
| 1688-shopkeeper | 1688 商品查询 | 1688 API |

### 分析研究类

| 技能 | 说明 |
|------|------|
| a-stock-analysis | A 股深度分析（含数据同步、调度、通知） |
| trading-pattern-miner | 交易模式挖掘与识别 |
| tavily-research | 基于 Tavily 的深度研究 |
| tavily-search | Tavily 搜索 |
| tavily-crawl / tavily-extract | 网页抓取与内容提取 |

### 生产力类

| 技能 | 说明 |
|------|------|
| productivity | 生产力框架集（ADHD/ burnout/ 创意/ 管理等） |
| self-improving-agent | 自我改进 Agent |
| smart-expense-tracker | 智能记账 |
| wechatsync | 微信公众号多平台同步 |

### 超能力系列

| 技能 | 说明 |
|------|------|
| superpowers-brainstorming | 脑暴模式 |
| superpowers-writing-plans | 计划编写 |
| superpowers-executing-plans | 计划执行 |
| superpowers-dispatching-parallel-agents | 并行 Agent 调度 |
| superpowers-systematic-debugging | 系统化调试 |

### 名人视角模拟（nuwa-skill）

模拟名人的思维框架与表达方式，支持 Feynman、Elon Musk、Paul Graham、Naval Ravikant、Charlie Munger、Steve Jobs、张一鸣 等 20+ 位名人。

## 许可证

本仓库仅供个人学习备份使用。技能文件版权归各自作者所有。
