---
name: frontend
version: 0.1.0
description: 企业级前端开发规范，使用 React 18+、TypeScript、Ant Design 5+、IceJS v3、icestark 微前端、AEM 监控、ECharts 图表。适用于创建/修改前端项目、编写组件、配置路由、集成 API、实现微前端、添加图表等场景。包管理使用 tnpm。
---

# Frontend React + IceJS v3 Development

企业级前端开发 Skill，涵盖完整的技术栈和最佳实践。

## 核心技术栈

- **React**: >= 18.0.0
- **TypeScript**: 类型安全开发
- **Ant Design**: >= 5.0.0 (UI 组件库)
- **IceJS**: v3 (应用框架)
- **包管理器**: tnpm
- **微前端**: icestark
- **前端监控**: AEM
- **接口请求**: ICE 内置请求方案
- **图表库**: ECharts

## 快速开始

### 创建新项目

```bash
# 使用 IceJS v3 初始化项目
tnpm init ice@3
cd project-name
tnpm install

# 启动开发服务器
tnpm start
```

### 标准项目结构

```
src/
├── pages/              # 页面组件
├── components/         # 公共组件
├── services/          # API 服务
├── hooks/             # 自定义 Hooks
├── types/             # TypeScript 类型
├── utils/             # 工具函数
├── constants/         # 常量
├── models/            # 数据模型
└── app.tsx            # 应用入口
```

## 核心开发模式

### 1. TypeScript 组件定义

```typescript
import { FC, ReactNode } from 'react';

interface ComponentProps {
  title: string;
  children?: ReactNode;
  onConfirm?: () => void;
}

const Component: FC<ComponentProps> = ({ title, children, onConfirm }) => {
  return <div>{title}</div>;
};

export default Component;
```

### 2. API 服务封装（ICE 内置方案）

```typescript
// src/services/user.ts
import { request } from 'ice';
import type { ApiResponse, UserInfo } from '@/types/api';

export const getUserInfo = async (): Promise<ApiResponse<UserInfo>> => {
  return request.get<ApiResponse<UserInfo>>('/user/info');
};

export const getUserList = async (params: any) => {
  return request.get('/user/list', { params });
};
```

### 3. 配置请求拦截器

```typescript
// src/app.tsx
import { defineAppConfig } from 'ice';

export default defineAppConfig(() => ({
  request: {
    baseURL: '/api',
    timeout: 30000,
    interceptors: {
      request: {
        onConfig: (config) => {
          const token = localStorage.getItem('token');
          if (token) {
            config.headers = {
              ...config.headers,
              Authorization: `Bearer ${token}`,
            };
          }
          return config;
        },
      },
    },
  },
}));
```

### 4. Ant Design 5.x 主题配置

```typescript
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';

export default function App() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 4,
          fontSize: 14,
        },
      }}
    >
      {/* 应用内容 */}
    </ConfigProvider>
  );
}
```

### 5. ECharts 图表集成

```typescript
// 使用封装的 Chart 组件
import Chart from '@/components/Chart';
import type { EChartsOption } from 'echarts';

const chartOption: EChartsOption = {
  title: { text: '数据统计' },
  xAxis: { type: 'category', data: ['1月', '2月', '3月'] },
  yAxis: { type: 'value' },
  series: [{ type: 'line', data: [100, 200, 300] }],
};

// 使用
<Chart option={chartOption} height={400} />
```

### 6. icestark 微前端配置

**主应用**:
```typescript
import { AppRouter, AppRoute } from '@ice/stark';

<AppRouter>
  <AppRoute
    path="/app1"
    name="app1"
    url={['//localhost:3001/js/index.js']}
  />
</AppRouter>
```

**子应用**:
```typescript
import { isInIcestark, getMountNode } from '@ice/stark-app';

export default defineAppConfig(() => ({
  app: {
    rootId: isInIcestark() ? getMountNode() : 'app',
  },
}));
```

### 7. AEM 监控集成

```typescript
// src/utils/aem.ts
export const initAEM = (config: { pid: string; appName: string; env: string }) => {
  if (typeof window !== 'undefined' && (window as any).aem) {
    (window as any).aem.init(config);
  }
};

// 错误上报
export const reportError = (error: Error, extra?: Record<string, any>) => {
  if ((window as any).aem) {
    (window as any).aem.error({ message: error.message, ...extra });
  }
};
```

## 开发指南

### 创建新页面时
1. 在 `src/pages/` 创建页面组件
2. 定义 TypeScript 接口
3. 使用 Ant Design 组件
4. 通过 `src/services/` 调用 API
5. 在路由配置中注册页面

### 创建 API 服务时
1. 在 `src/types/api.ts` 定义类型
2. 在 `src/services/` 创建服务文件
3. 使用 `request` 从 'ice' 导入
4. 返回类型化的 Promise

### 使用 Ant Design 组件时
- 优先使用 Ant Design 5.x 组件
- 通过 ConfigProvider 统一配置主题
- 使用 Form.useForm() 管理表单
- Table 组件使用 rowKey 指定唯一键

### 集成图表时
- 安装: `tnpm install echarts`
- 使用封装的 Chart 组件
- 定义 EChartsOption 类型
- 响应式处理图表大小

## 重要约定

1. **包管理**: 始终使用 `tnpm` 而非 npm/yarn
2. **TypeScript**: 避免使用 `any`，定义明确类型
3. **样式**: 使用 CSS Modules 或 Ant Design 主题
4. **路径别名**: 使用 `@/` 指向 `src/` 目录
5. **错误处理**: 在请求拦截器中统一处理
6. **监控**: 集成 AEM 进行错误和性能监控

## 性能优化

- 使用 `React.lazy()` 和 `Suspense` 进行代码分割
- 使用 `React.memo()` 优化组件渲染
- 使用 `useMemo()` 和 `useCallback()` 缓存计算和回调
- 图表组件响应式处理和销毁

## 详细文档

- [完整技术参考](reference.md) - 详细配置、API 和高级用法
- [代码示例集](examples.md) - 完整的组件和功能示例

## 常见任务

**安装依赖**:
```bash
tnpm install package-name
```

**构建生产版本**:
```bash
tnpm run build
```

**IceJS 配置**: 编辑 `build.json`
**路由配置**: 编辑 `src/routes.tsx`
**环境变量**: 使用 `.env.development` 和 `.env.production`

## 故障排除

**依赖安装失败**:
```bash
tnpm cache clean --force
rm -rf node_modules
tnpm install
```

**TypeScript 错误**: 检查 `tsconfig.json` 和类型定义

**样式不生效**: 确保 ConfigProvider 正确包裹应用

## 使用此 Skill 时

我会：
- ✅ 使用指定的技术栈和版本
- ✅ 遵循项目结构规范
- ✅ 编写类型安全的 TypeScript 代码
- ✅ 使用 ICE 内置请求方案
- ✅ 集成 AEM 监控
- ✅ 使用 tnpm 管理依赖
- ✅ 应用性能优化最佳实践

需要详细信息时，我会参考 reference.md 和 examples.md。

