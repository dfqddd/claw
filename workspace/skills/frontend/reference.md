# 技术参考文档

完整的配置、API 和高级用法参考。

## 目录

- [IceJS v3 配置](#icejs-v3-配置)
- [TypeScript 类型定义](#typescript-类型定义)
- [接口请求详解](#接口请求详解)
- [Ant Design 高级用法](#ant-design-高级用法)
- [ECharts 集成详解](#echarts-集成详解)
- [icestark 微前端详解](#icestark-微前端详解)
- [AEM 监控详解](#aem-监控详解)
- [自定义 Hooks](#自定义-hooks)
- [路由配置](#路由配置)
- [环境变量](#环境变量)

## IceJS v3 配置

### build.json 完整配置

```json
{
  "vite": true,
  "plugins": [
    ["@ice/plugin-request"],
    ["@ice/plugin-store"],
    ["@ice/plugin-antd"]
  ],
  "routes": {
    "defineRoutes": true
  },
  "proxy": {
    "/api": {
      "target": "http://localhost:3000",
      "changeOrigin": true,
      "rewrite": { "^/api": "" }
    }
  },
  "alias": {
    "@": "./src"
  },
  "minify": "esbuild",
  "outputDir": "build",
  "sourceMap": false
}
```

### app.tsx 应用配置

```typescript
import { defineAppConfig } from 'ice';

export default defineAppConfig(() => ({
  app: {
    rootId: 'app',
    strict: true,
    errorBoundary: true,
  },
  router: {
    type: 'browser',
    basename: '/',
    fallback: <div>Loading...</div>,
  },
  request: {
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    timeout: 30000,
    withCredentials: true,
    interceptors: {
      request: {
        onConfig: (config) => {
          // 添加认证 token
          const token = localStorage.getItem('token');
          if (token) {
            config.headers = {
              ...config.headers,
              Authorization: `Bearer ${token}`,
            };
          }
          // 添加请求 ID
          config.headers = {
            ...config.headers,
            'X-Request-Id': Math.random().toString(36).substring(7),
          };
          return config;
        },
        onError: (error) => {
          console.error('Request Config Error:', error);
          return Promise.reject(error);
        },
      },
      response: {
        onConfig: (response) => {
          // 统一处理响应数据
          if (response.data && !response.data.success) {
            return Promise.reject(new Error(response.data.message || '请求失败'));
          }
          return response;
        },
        onError: (error) => {
          // 统一错误处理
          if (error.response) {
            switch (error.response.status) {
              case 401:
                // 未授权，跳转登录
                window.location.href = '/login';
                break;
              case 403:
                console.error('无权限访问');
                break;
              case 404:
                console.error('资源不存在');
                break;
              case 500:
                console.error('服务器错误');
                break;
              default:
                console.error('请求失败:', error.message);
            }
          }
          return Promise.reject(error);
        },
      },
    },
  },
}));
```

## TypeScript 类型定义

### API 响应类型

```typescript
// src/types/api.ts

// 基础响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  code: number;
  message: string;
  timestamp?: number;
}

// 分页请求参数
export interface PaginationParams {
  current: number;
  pageSize: number;
  sortField?: string;
  sortOrder?: 'ascend' | 'descend';
}

// 分页响应数据
export interface PaginatedResponse<T> {
  list: T[];
  total: number;
  current: number;
  pageSize: number;
}

// 用户信息
export interface UserInfo {
  id: string;
  name: string;
  email: string;
  phone?: string;
  avatar?: string;
  role: string;
  status: 'active' | 'inactive';
  createdAt: string;
  updatedAt: string;
}

// 表格列数据
export interface TableColumn {
  key: string;
  title: string;
  dataIndex: string;
  width?: number;
  fixed?: 'left' | 'right';
  sorter?: boolean;
  filters?: Array<{ text: string; value: string }>;
}
```

### 组件 Props 类型

```typescript
// src/types/components.ts
import { ReactNode, CSSProperties } from 'react';

// 基础组件 Props
export interface BaseComponentProps {
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

// 表单字段配置
export interface FormFieldConfig {
  name: string;
  label: string;
  type: 'input' | 'select' | 'date' | 'textarea';
  required?: boolean;
  placeholder?: string;
  options?: Array<{ label: string; value: string | number }>;
  rules?: any[];
}

// 模态框 Props
export interface ModalProps extends BaseComponentProps {
  visible: boolean;
  title: string;
  onOk?: () => void;
  onCancel?: () => void;
  loading?: boolean;
  width?: number;
}
```

## 接口请求详解

### 请求方法封装

```typescript
// src/services/base.ts
import { request } from 'ice';
import type { ApiResponse } from '@/types/api';

/**
 * GET 请求封装
 */
export async function get<T>(
  url: string,
  params?: Record<string, any>
): Promise<ApiResponse<T>> {
  return request.get<ApiResponse<T>>(url, { params });
}

/**
 * POST 请求封装
 */
export async function post<T>(
  url: string,
  data?: Record<string, any>
): Promise<ApiResponse<T>> {
  return request.post<ApiResponse<T>>(url, data);
}

/**
 * PUT 请求封装
 */
export async function put<T>(
  url: string,
  data?: Record<string, any>
): Promise<ApiResponse<T>> {
  return request.put<ApiResponse<T>>(url, data);
}

/**
 * DELETE 请求封装
 */
export async function del<T>(url: string): Promise<ApiResponse<T>> {
  return request.delete<ApiResponse<T>>(url);
}

/**
 * 文件上传
 */
export async function upload(
  url: string,
  file: File,
  onProgress?: (percent: number) => void
): Promise<ApiResponse<{ url: string }>> {
  const formData = new FormData();
  formData.append('file', file);

  return request.post(url, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress?.(percent);
      }
    },
  });
}
```

### 业务 API 示例

```typescript
// src/services/user.ts
import { get, post, put, del } from './base';
import type { ApiResponse, UserInfo, PaginatedResponse, PaginationParams } from '@/types/api';

/**
 * 获取用户列表
 */
export const getUserList = (
  params: PaginationParams & { keyword?: string }
): Promise<ApiResponse<PaginatedResponse<UserInfo>>> => {
  return get('/user/list', params);
};

/**
 * 获取用户详情
 */
export const getUserDetail = (userId: string): Promise<ApiResponse<UserInfo>> => {
  return get(`/user/${userId}`);
};

/**
 * 创建用户
 */
export const createUser = (data: Partial<UserInfo>): Promise<ApiResponse<UserInfo>> => {
  return post('/user', data);
};

/**
 * 更新用户
 */
export const updateUser = (
  userId: string,
  data: Partial<UserInfo>
): Promise<ApiResponse<void>> => {
  return put(`/user/${userId}`, data);
};

/**
 * 删除用户
 */
export const deleteUser = (userId: string): Promise<ApiResponse<void>> => {
  return del(`/user/${userId}`);
};

/**
 * 批量删除用户
 */
export const batchDeleteUsers = (userIds: string[]): Promise<ApiResponse<void>> => {
  return post('/user/batch-delete', { ids: userIds });
};
```

## Ant Design 高级用法

### Table 完整示例

```typescript
import { Table, Button, Space, Tag, Popconfirm, message } from 'antd';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import type { FilterValue, SorterResult } from 'antd/es/table/interface';

interface DataType {
  id: string;
  name: string;
  email: string;
  status: 'active' | 'inactive';
  role: string;
  createdAt: string;
}

interface TableProps {
  loading: boolean;
  dataSource: DataType[];
  pagination: TablePaginationConfig;
  onChange: (
    pagination: TablePaginationConfig,
    filters: Record<string, FilterValue | null>,
    sorter: SorterResult<DataType> | SorterResult<DataType>[]
  ) => void;
  onEdit: (record: DataType) => void;
  onDelete: (id: string) => void;
}

const UserTable: FC<TableProps> = ({
  loading,
  dataSource,
  pagination,
  onChange,
  onEdit,
  onDelete,
}) => {
  const columns: ColumnsType<DataType> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
      fixed: 'left',
    },
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      width: 150,
      sorter: true,
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 200,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      filters: [
        { text: '激活', value: 'active' },
        { text: '停用', value: 'inactive' },
      ],
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {status === 'active' ? '激活' : '停用'}
        </Tag>
      ),
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 120,
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
      sorter: true,
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" onClick={() => onEdit(record)}>
            编辑
          </Button>
          <Popconfirm
            title="确定要删除该用户吗？"
            description="此操作不可恢复"
            onConfirm={() => {
              onDelete(record.id);
              message.success('删除成功');
            }}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={dataSource}
      loading={loading}
      rowKey="id"
      pagination={{
        ...pagination,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total) => `共 ${total} 条记录`,
        pageSizeOptions: ['10', '20', '50', '100'],
      }}
      onChange={onChange}
      scroll={{ x: 1200 }}
      bordered
    />
  );
};
```

### Form 完整示例

```typescript
import { Form, Input, Select, DatePicker, Button, Space, message } from 'antd';
import type { FormInstance } from 'antd';

interface FormValues {
  name: string;
  email: string;
  phone?: string;
  role: string;
  status: string;
  birthday?: string;
}

interface UserFormProps {
  initialValues?: FormValues;
  onSubmit: (values: FormValues) => Promise<void>;
  onCancel: () => void;
}

const UserForm: FC<UserFormProps> = ({ initialValues, onSubmit, onCancel }) => {
  const [form] = Form.useForm<FormValues>();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values: FormValues) => {
    setLoading(true);
    try {
      await onSubmit(values);
      message.success('保存成功');
      form.resetFields();
    } catch (error) {
      message.error('保存失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={initialValues}
      onFinish={handleSubmit}
      autoComplete="off"
    >
      <Form.Item
        label="姓名"
        name="name"
        rules={[
          { required: true, message: '请输入姓名' },
          { min: 2, max: 50, message: '姓名长度在2-50个字符之间' },
        ]}
      >
        <Input placeholder="请输入姓名" />
      </Form.Item>

      <Form.Item
        label="邮箱"
        name="email"
        rules={[
          { required: true, message: '请输入邮箱' },
          { type: 'email', message: '请输入有效的邮箱地址' },
        ]}
      >
        <Input placeholder="请输入邮箱" />
      </Form.Item>

      <Form.Item
        label="手机号"
        name="phone"
        rules={[
          { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' },
        ]}
      >
        <Input placeholder="请输入手机号（选填）" />
      </Form.Item>

      <Form.Item
        label="角色"
        name="role"
        rules={[{ required: true, message: '请选择角色' }]}
      >
        <Select placeholder="请选择角色">
          <Select.Option value="admin">管理员</Select.Option>
          <Select.Option value="user">普通用户</Select.Option>
          <Select.Option value="guest">访客</Select.Option>
        </Select>
      </Form.Item>

      <Form.Item
        label="状态"
        name="status"
        rules={[{ required: true, message: '请选择状态' }]}
      >
        <Select placeholder="请选择状态">
          <Select.Option value="active">激活</Select.Option>
          <Select.Option value="inactive">停用</Select.Option>
        </Select>
      </Form.Item>

      <Form.Item label="生日" name="birthday">
        <DatePicker style={{ width: '100%' }} placeholder="请选择生日" />
      </Form.Item>

      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit" loading={loading}>
            提交
          </Button>
          <Button onClick={() => form.resetFields()}>
            重置
          </Button>
          <Button onClick={onCancel}>
            取消
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};
```

## ECharts 集成详解

### Chart 组件封装

```typescript
// src/components/Chart/index.tsx
import { useEffect, useRef, FC } from 'react';
import * as echarts from 'echarts';
import type { EChartsOption, ECharts } from 'echarts';

interface ChartProps {
  option: EChartsOption;
  height?: number | string;
  width?: number | string;
  loading?: boolean;
  theme?: string | object;
  onChartReady?: (chart: ECharts) => void;
  onClick?: (params: any) => void;
}

const Chart: FC<ChartProps> = ({
  option,
  height = 400,
  width = '100%',
  loading = false,
  theme,
  onChartReady,
  onClick,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<ECharts | null>(null);

  // 初始化图表
  useEffect(() => {
    if (chartRef.current) {
      chartInstance.current = echarts.init(chartRef.current, theme);
      onChartReady?.(chartInstance.current);

      // 绑定点击事件
      if (onClick) {
        chartInstance.current.on('click', onClick);
      }
    }

    return () => {
      chartInstance.current?.dispose();
      chartInstance.current = null;
    };
  }, [theme, onChartReady, onClick]);

  // 更新配置
  useEffect(() => {
    if (chartInstance.current) {
      if (loading) {
        chartInstance.current.showLoading('default', {
          text: '加载中...',
          color: '#1890ff',
          textColor: '#000',
          maskColor: 'rgba(255, 255, 255, 0.8)',
        });
      } else {
        chartInstance.current.hideLoading();
        chartInstance.current.setOption(option, true);
      }
    }
  }, [option, loading]);

  // 响应式
  useEffect(() => {
    const handleResize = () => {
      chartInstance.current?.resize();
    };

    window.addEventListener('resize', handleResize);
    // 使用 ResizeObserver 监听容器大小变化
    const resizeObserver = new ResizeObserver(handleResize);
    if (chartRef.current) {
      resizeObserver.observe(chartRef.current);
    }

    return () => {
      window.removeEventListener('resize', handleResize);
      resizeObserver.disconnect();
    };
  }, []);

  return (
    <div
      ref={chartRef}
      style={{
        height: typeof height === 'number' ? `${height}px` : height,
        width: typeof width === 'number' ? `${width}px` : width,
      }}
    />
  );
};

export default Chart;
```

### 常用图表配置

```typescript
// src/utils/chartOptions.ts
import type { EChartsOption } from 'echarts';

/**
 * 折线图配置
 */
export const getLineChartOption = (data: {
  xAxis: string[];
  series: Array<{ name: string; data: number[] }>;
  title?: string;
}): EChartsOption => ({
  title: { text: data.title, left: 'center' },
  tooltip: { trigger: 'axis' },
  legend: { top: 30, data: data.series.map((s) => s.name) },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', boundaryGap: false, data: data.xAxis },
  yAxis: { type: 'value' },
  series: data.series.map((s) => ({
    name: s.name,
    type: 'line',
    data: s.data,
    smooth: true,
  })),
});

/**
 * 柱状图配置
 */
export const getBarChartOption = (data: {
  xAxis: string[];
  series: Array<{ name: string; data: number[] }>;
  title?: string;
}): EChartsOption => ({
  title: { text: data.title, left: 'center' },
  tooltip: { trigger: 'axis' },
  legend: { top: 30, data: data.series.map((s) => s.name) },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: data.xAxis },
  yAxis: { type: 'value' },
  series: data.series.map((s) => ({
    name: s.name,
    type: 'bar',
    data: s.data,
    emphasis: { focus: 'series' },
  })),
});

/**
 * 饼图配置
 */
export const getPieChartOption = (data: {
  data: Array<{ name: string; value: number }>;
  title?: string;
}): EChartsOption => ({
  title: { text: data.title, left: 'center' },
  tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
  legend: { orient: 'vertical', left: 'left', top: 'middle' },
  series: [
    {
      name: '数据',
      type: 'pie',
      radius: '50%',
      data: data.data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)',
        },
      },
    },
  ],
});
```

## icestark 微前端详解

### 主应用完整配置

```typescript
// 主应用 src/app.tsx
import { useState } from 'react';
import { AppRouter, AppRoute, AppLink } from '@ice/stark';
import { Layout, Menu } from 'antd';
import type { MenuProps } from 'antd';

const { Header, Content, Sider } = Layout;

export default function MainApp() {
  const [loading, setLoading] = useState(false);

  const menuItems: MenuProps['items'] = [
    {
      key: 'app1',
      label: <AppLink to="/app1">应用1</AppLink>,
    },
    {
      key: 'app2',
      label: <AppLink to="/app2">应用2</AppLink>,
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header>
        <div style={{ color: 'white', fontSize: 20 }}>主应用</div>
      </Header>
      <Layout>
        <Sider width={200}>
          <Menu mode="inline" items={menuItems} />
        </Sider>
        <Content style={{ padding: 24, background: '#fff' }}>
          {loading && <div>加载中...</div>}
          <AppRouter
            onRouteChange={(pathname, query, hash) => {
              console.log('路由变化:', pathname, query, hash);
            }}
            onAppEnter={(appConfig) => {
              console.log('子应用加载:', appConfig.name);
              setLoading(false);
            }}
            onAppLeave={(appConfig) => {
              console.log('子应用卸载:', appConfig.name);
            }}
            onLoadingApp={() => {
              setLoading(true);
            }}
            onFinishLoading={() => {
              setLoading(false);
            }}
            onError={(err) => {
              console.error('子应用错误:', err);
              setLoading(false);
            }}
          >
            <AppRoute
              path="/app1"
              title="应用1"
              name="app1"
              url={[
                '//localhost:3001/js/index.js',
                '//localhost:3001/css/index.css',
              ]}
              // 传递给子应用的数据
              props={{
                user: { id: '123', name: 'Admin' },
              }}
            />
            <AppRoute
              path="/app2"
              title="应用2"
              name="app2"
              url={[
                '//localhost:3002/js/index.js',
                '//localhost:3002/css/index.css',
              ]}
            />
          </AppRouter>
        </Content>
      </Layout>
    </Layout>
  );
}
```

### 子应用完整配置

```typescript
// 子应用 src/app.tsx
import { defineAppConfig } from 'ice';
import {
  isInIcestark,
  getMountNode,
  registerAppEnter,
  registerAppLeave,
  getBasename,
} from '@ice/stark-app';

// 注册生命周期
registerAppEnter((props) => {
  console.log('子应用加载完成', props);
  // 可以获取主应用传递的数据
  console.log('主应用数据:', props.user);
});

registerAppLeave(() => {
  console.log('子应用卸载');
  // 清理操作
});

export default defineAppConfig(() => ({
  app: {
    rootId: isInIcestark() ? getMountNode() : 'app',
  },
  router: {
    type: 'browser',
    basename: isInIcestark() ? getBasename() : '/',
  },
}));
```

### 应用间通信

```typescript
// 共享数据
import { store } from '@ice/stark-data';

// 主应用设置数据
store.set('user', { id: '123', name: 'Admin' });
store.set('theme', { primaryColor: '#1890ff' });

// 子应用获取数据
const user = store.get('user');
const theme = store.get('theme');

// 监听数据变化
store.on('user', (newUser) => {
  console.log('用户信息更新:', newUser);
});

// 取消监听
store.off('user', callback);

// 清空数据
store.clear();
```

## AEM 监控详解

### 完整监控配置

```typescript
// src/utils/aem.ts

interface AEMConfig {
  pid: string;
  appName: string;
  env: 'dev' | 'pre' | 'prod';
  uid?: string;
  enablePerformance?: boolean;
  enableError?: boolean;
  enableApi?: boolean;
}

/**
 * 初始化 AEM
 */
export const initAEM = (config: AEMConfig) => {
  if (typeof window === 'undefined' || !(window as any).aem) {
    console.warn('AEM SDK 未加载');
    return;
  }

  (window as any).aem.init({
    pid: config.pid,
    appName: config.appName,
    env: config.env,
    uid: config.uid,
    // 自动捕获配置
    performance: config.enablePerformance !== false,
    error: config.enableError !== false,
    api: config.enableApi !== false,
    // 采样率
    sampleRate: config.env === 'prod' ? 0.1 : 1,
  });
};

/**
 * 设置用户 ID
 */
export const setAEMUser = (uid: string) => {
  if ((window as any).aem) {
    (window as any).aem.setUid(uid);
  }
};

/**
 * 上报错误
 */
export const reportError = (error: Error, extra?: Record<string, any>) => {
  if ((window as any).aem) {
    (window as any).aem.error({
      message: error.message,
      stack: error.stack,
      category: 'javascript',
      level: 'error',
      ...extra,
    });
  }
};

/**
 * 上报性能指标
 */
export const reportPerformance = (metrics: {
  name: string;
  duration: number;
  extra?: Record<string, any>;
}) => {
  if ((window as any).aem) {
    (window as any).aem.performance({
      name: metrics.name,
      duration: metrics.duration,
      ...metrics.extra,
    });
  }
};

/**
 * 上报用户行为
 */
export const reportAction = (action: {
  name: string;
  category?: string;
  data?: Record<string, any>;
}) => {
  if ((window as any).aem) {
    (window as any).aem.action({
      name: action.name,
      category: action.category || 'user_action',
      data: action.data,
      timestamp: Date.now(),
    });
  }
};

/**
 * 上报 API 请求
 */
export const reportAPI = (api: {
  url: string;
  method: string;
  duration: number;
  status: number;
  success: boolean;
}) => {
  if ((window as any).aem) {
    (window as any).aem.api({
      url: api.url,
      method: api.method,
      duration: api.duration,
      status: api.status,
      success: api.success,
      timestamp: Date.now(),
    });
  }
};

/**
 * 上报自定义指标
 */
export const reportCustom = (name: string, value: number | string, extra?: Record<string, any>) => {
  if ((window as any).aem) {
    (window as any).aem.custom({
      name,
      value,
      ...extra,
    });
  }
};
```

### 错误边界组件

```typescript
// src/components/ErrorBoundary/index.tsx
import { Component, ReactNode } from 'react';
import { Result, Button } from 'antd';
import { reportError } from '@/utils/aem';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: any;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error Boundary 捕获错误:', error, errorInfo);
    
    // 上报到 AEM
    reportError(error, {
      componentStack: errorInfo.componentStack,
      errorBoundary: true,
    });

    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Result
          status="error"
          title="页面出错了"
          subTitle={
            process.env.NODE_ENV === 'development'
              ? this.state.error?.message
              : '抱歉，页面遇到了一些问题'
          }
          extra={[
            <Button type="primary" key="reload" onClick={() => window.location.reload()}>
              刷新页面
            </Button>,
            <Button key="reset" onClick={this.handleReset}>
              返回
            </Button>,
          ]}
        />
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

## 自定义 Hooks

### useRequest Hook

```typescript
// src/hooks/useRequest.ts
import { useState, useEffect, useCallback, useRef } from 'react';
import { message } from 'antd';

interface UseRequestOptions<T> {
  manual?: boolean;
  initialData?: T;
  onSuccess?: (data: T, params: any[]) => void;
  onError?: (error: Error, params: any[]) => void;
  onFinally?: (params: any[]) => void;
  debounceWait?: number;
  throttleWait?: number;
  pollingInterval?: number;
  refreshDeps?: any[];
}

export const useRequest = <T,>(
  requestFn: (...args: any[]) => Promise<T>,
  options: UseRequestOptions<T> = {}
) => {
  const {
    manual = false,
    initialData,
    onSuccess,
    onError,
    onFinally,
    debounceWait,
    throttleWait,
    pollingInterval,
    refreshDeps = [],
  } = options;

  const [data, setData] = useState<T | undefined>(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | undefined>();
  
  const unmountedRef = useRef(false);
  const pollingTimerRef = useRef<NodeJS.Timeout>();
  const debounceTimerRef = useRef<NodeJS.Timeout>();
  const lastCallTimeRef = useRef(0);

  const run = useCallback(
    async (...args: any[]) => {
      // 防抖
      if (debounceWait) {
        return new Promise<T>((resolve, reject) => {
          if (debounceTimerRef.current) {
            clearTimeout(debounceTimerRef.current);
          }
          debounceTimerRef.current = setTimeout(async () => {
            try {
              const result = await executeRequest(args);
              resolve(result);
            } catch (err) {
              reject(err);
            }
          }, debounceWait);
        });
      }

      // 节流
      if (throttleWait) {
        const now = Date.now();
        if (now - lastCallTimeRef.current < throttleWait) {
          return Promise.reject(new Error('请求过于频繁'));
        }
        lastCallTimeRef.current = now;
      }

      return executeRequest(args);
    },
    [requestFn, onSuccess, onError, onFinally]
  );

  const executeRequest = async (args: any[]) => {
    setLoading(true);
    setError(undefined);
    
    try {
      const result = await requestFn(...args);
      if (!unmountedRef.current) {
        setData(result);
        onSuccess?.(result, args);
      }
      return result;
    } catch (err) {
      const error = err as Error;
      if (!unmountedRef.current) {
        setError(error);
        onError?.(error, args);
        message.error(error.message || '请求失败');
      }
      throw error;
    } finally {
      if (!unmountedRef.current) {
        setLoading(false);
        onFinally?.(args);
      }
    }
  };

  const cancel = () => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current);
    }
  };

  const refresh = () => {
    return run();
  };

  const mutate = (newData: T | ((oldData: T | undefined) => T)) => {
    if (typeof newData === 'function') {
      setData((oldData) => (newData as Function)(oldData));
    } else {
      setData(newData);
    }
  };

  // 自动请求
  useEffect(() => {
    if (!manual) {
      run();
    }
  }, [manual, ...refreshDeps]);

  // 轮询
  useEffect(() => {
    if (pollingInterval && pollingInterval > 0) {
      pollingTimerRef.current = setInterval(() => {
        run();
      }, pollingInterval);
    }

    return () => {
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
      }
    };
  }, [pollingInterval, run]);

  // 清理
  useEffect(() => {
    unmountedRef.current = false;
    return () => {
      unmountedRef.current = true;
      cancel();
    };
  }, []);

  return {
    data,
    loading,
    error,
    run,
    cancel,
    refresh,
    mutate,
  };
};
```

### usePagination Hook

```typescript
// src/hooks/usePagination.ts
import { useState, useCallback } from 'react';
import type { TablePaginationConfig } from 'antd';

interface UsePaginationOptions {
  initialCurrent?: number;
  initialPageSize?: number;
  initialTotal?: number;
}

export const usePagination = (options: UsePaginationOptions = {}) => {
  const {
    initialCurrent = 1,
    initialPageSize = 10,
    initialTotal = 0,
  } = options;

  const [pagination, setPagination] = useState<TablePaginationConfig>({
    current: initialCurrent,
    pageSize: initialPageSize,
    total: initialTotal,
  });

  const onChange = useCallback((page: number, pageSize: number) => {
    setPagination((prev) => ({
      ...prev,
      current: page,
      pageSize,
    }));
  }, []);

  const setTotal = useCallback((total: number) => {
    setPagination((prev) => ({
      ...prev,
      total,
    }));
  }, []);

  const reset = useCallback(() => {
    setPagination({
      current: initialCurrent,
      pageSize: initialPageSize,
      total: 0,
    });
  }, [initialCurrent, initialPageSize]);

  const goToPage = useCallback((page: number) => {
    setPagination((prev) => ({
      ...prev,
      current: page,
    }));
  }, []);

  return {
    pagination,
    onChange,
    setTotal,
    reset,
    goToPage,
  };
};
```

### useDebounce Hook

```typescript
// src/hooks/useDebounce.ts
import { useState, useEffect } from 'react';

export const useDebounce = <T,>(value: T, delay: number = 500): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
};
```

### useThrottle Hook

```typescript
// src/hooks/useThrottle.ts
import { useState, useEffect, useRef } from 'react';

export const useThrottle = <T,>(value: T, wait: number = 500): T => {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const lastCallTime = useRef(0);

  useEffect(() => {
    const now = Date.now();
    if (now - lastCallTime.current >= wait) {
      setThrottledValue(value);
      lastCallTime.current = now;
    } else {
      const timer = setTimeout(() => {
        setThrottledValue(value);
        lastCallTime.current = Date.now();
      }, wait - (now - lastCallTime.current));

      return () => clearTimeout(timer);
    }
  }, [value, wait]);

  return throttledValue;
};
```

## 路由配置

### 路由定义

```typescript
// src/routes.tsx
import { defineRoutes } from 'ice';
import { lazy } from 'react';
import BasicLayout from '@/layouts/BasicLayout';
import Login from '@/pages/Login';

// 路由懒加载
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const UserList = lazy(() => import('@/pages/User/List'));
const UserDetail = lazy(() => import('@/pages/User/Detail'));

export default defineRoutes(() => [
  // 登录页
  {
    path: '/login',
    component: Login,
  },
  // 主应用路由
  {
    path: '/',
    component: BasicLayout,
    children: [
      {
        path: '/',
        redirect: '/dashboard',
      },
      {
        path: '/dashboard',
        component: Dashboard,
      },
      {
        path: '/user',
        children: [
          {
            path: '/user/list',
            component: UserList,
          },
          {
            path: '/user/detail/:id',
            component: UserDetail,
          },
        ],
      },
    ],
  },
  // 404 页面
  {
    path: '*',
    component: lazy(() => import('@/pages/NotFound')),
  },
]);
```

### 路由守卫

```typescript
// src/app.tsx
import { defineAppConfig, history } from 'ice';

export default defineAppConfig(() => ({
  router: {
    type: 'browser',
    modifyRoutes: (routes) => {
      return routes;
    },
  },
  app: {
    onShow: () => {
      // 路由守卫
      const token = localStorage.getItem('token');
      const pathname = history.location.pathname;
      
      // 白名单
      const whitelist = ['/login', '/register'];
      
      if (!token && !whitelist.includes(pathname)) {
        history.push('/login');
      }
    },
  },
}));
```

## 环境变量

### 环境变量配置

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:3000
VITE_AEM_PID=dev-project-id
VITE_APP_ENV=development

# .env.production
VITE_API_BASE_URL=https://api.production.com
VITE_AEM_PID=prod-project-id
VITE_APP_ENV=production
```

### 使用环境变量

```typescript
// src/config/index.ts
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
  aemPid: import.meta.env.VITE_AEM_PID,
  appEnv: import.meta.env.VITE_APP_ENV,
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
};
```

