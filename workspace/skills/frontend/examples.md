# 代码示例集

完整的组件和功能实现示例。

## 目录

- [完整页面示例](#完整页面示例)
- [布局组件](#布局组件)
- [业务组件](#业务组件)
- [自定义 Hooks 使用](#自定义-hooks-使用)
- [图表示例](#图表示例)
- [微前端示例](#微前端示例)

## 完整页面示例

### 用户列表页面

```typescript
// src/pages/User/List/index.tsx
import { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Space,
  Input,
  Table,
  Modal,
  Form,
  message,
  Popconfirm,
  Tag,
} from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getUserList, createUser, updateUser, deleteUser } from '@/services/user';
import { usePagination, useRequest, useDebounce } from '@/hooks';
import { reportAction } from '@/utils/aem';
import type { UserInfo } from '@/types/api';

const UserList = () => {
  const [keyword, setKeyword] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<UserInfo | null>(null);
  const [form] = Form.useForm();

  const { pagination, onChange, setTotal } = usePagination();
  const debouncedKeyword = useDebounce(keyword, 500);

  // 获取用户列表
  const { data, loading, run: fetchUsers } = useRequest(
    () =>
      getUserList({
        current: pagination.current!,
        pageSize: pagination.pageSize!,
        keyword: debouncedKeyword,
      }),
    {
      manual: true,
      onSuccess: (response) => {
        if (response.success) {
          setTotal(response.data.total);
        }
      },
    }
  );

  // 监听分页和关键词变化
  useEffect(() => {
    fetchUsers();
  }, [pagination.current, pagination.pageSize, debouncedKeyword]);

  // 打开新增/编辑弹窗
  const handleOpenModal = (user?: UserInfo) => {
    setEditingUser(user || null);
    if (user) {
      form.setFieldsValue(user);
    } else {
      form.resetFields();
    }
    setModalVisible(true);
    reportAction({ name: user ? 'edit_user_click' : 'add_user_click' });
  };

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingUser) {
        await updateUser(editingUser.id, values);
        message.success('更新成功');
        reportAction({ name: 'user_updated', data: { userId: editingUser.id } });
      } else {
        await createUser(values);
        message.success('创建成功');
        reportAction({ name: 'user_created' });
      }
      setModalVisible(false);
      fetchUsers();
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  // 删除用户
  const handleDelete = async (userId: string) => {
    try {
      await deleteUser(userId);
      message.success('删除成功');
      reportAction({ name: 'user_deleted', data: { userId } });
      fetchUsers();
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 表格列配置
  const columns: ColumnsType<UserInfo> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 200,
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {status === 'active' ? '激活' : '停用'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" onClick={() => handleOpenModal(record)}>
            编辑
          </Button>
          <Popconfirm
            title="确定要删除该用户吗？"
            onConfirm={() => handleDelete(record.id)}
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
    <Card>
      {/* 搜索和操作栏 */}
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索用户名或邮箱"
          prefix={<SearchOutlined />}
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          style={{ width: 300 }}
          allowClear
        />
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => handleOpenModal()}
        >
          新增用户
        </Button>
      </Space>

      {/* 表格 */}
      <Table
        columns={columns}
        dataSource={data?.data.list || []}
        loading={loading}
        rowKey="id"
        pagination={{
          ...pagination,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange,
        }}
        scroll={{ x: 1200 }}
      />

      {/* 新增/编辑弹窗 */}
      <Modal
        title={editingUser ? '编辑用户' : '新增用户'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="姓名"
            name="name"
            rules={[{ required: true, message: '请输入姓名' }]}
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
        </Form>
      </Modal>
    </Card>
  );
};

export default UserList;
```

### 仪表板页面

```typescript
// src/pages/Dashboard/index.tsx
import { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Space } from 'antd';
import {
  UserOutlined,
  ShoppingCartOutlined,
  DollarOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import Chart from '@/components/Chart';
import { getLineChartOption, getBarChartOption, getPieChartOption } from '@/utils/chartOptions';
import { getDashboardData } from '@/services/dashboard';
import { useRequest } from '@/hooks/useRequest';

const Dashboard = () => {
  const { data, loading } = useRequest(getDashboardData);

  const statistics = [
    {
      title: '总用户数',
      value: data?.data.totalUsers || 0,
      icon: <UserOutlined style={{ fontSize: 24, color: '#1890ff' }} />,
      suffix: '人',
    },
    {
      title: '总订单数',
      value: data?.data.totalOrders || 0,
      icon: <ShoppingCartOutlined style={{ fontSize: 24, color: '#52c41a' }} />,
      suffix: '单',
    },
    {
      title: '总销售额',
      value: data?.data.totalRevenue || 0,
      icon: <DollarOutlined style={{ fontSize: 24, color: '#faad14' }} />,
      prefix: '¥',
    },
    {
      title: '增长率',
      value: data?.data.growthRate || 0,
      icon: <RiseOutlined style={{ fontSize: 24, color: '#f5222d' }} />,
      suffix: '%',
    },
  ];

  // 销售趋势图配置
  const salesLineOption = getLineChartOption({
    title: '销售趋势',
    xAxis: ['1月', '2月', '3月', '4月', '5月', '6月'],
    series: [
      {
        name: '销售额',
        data: data?.data.salesTrend || [120, 200, 150, 300, 280, 350],
      },
    ],
  });

  // 订单统计图配置
  const ordersBarOption = getBarChartOption({
    title: '订单统计',
    xAxis: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    series: [
      {
        name: '订单数',
        data: data?.data.ordersWeekly || [50, 80, 60, 90, 70, 100, 85],
      },
    ],
  });

  // 用户分布图配置
  const userPieOption = getPieChartOption({
    title: '用户分布',
    data: data?.data.userDistribution || [
      { name: '普通用户', value: 335 },
      { name: 'VIP用户', value: 234 },
      { name: '企业用户', value: 135 },
    ],
  });

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {/* 统计卡片 */}
      <Row gutter={16}>
        {statistics.map((stat, index) => (
          <Col span={6} key={index}>
            <Card>
              <Statistic
                title={stat.title}
                value={stat.value}
                prefix={stat.prefix}
                suffix={stat.suffix}
                valueStyle={{ color: '#3f8600' }}
              />
              <div style={{ marginTop: 16 }}>{stat.icon}</div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 图表 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card title="销售趋势" loading={loading}>
            <Chart option={salesLineOption} height={300} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="订单统计" loading={loading}>
            <Chart option={ordersBarOption} height={300} />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="用户分布" loading={loading}>
            <Chart option={userPieOption} height={300} />
          </Card>
        </Col>
      </Row>
    </Space>
  );
};

export default Dashboard;
```

## 布局组件

### 基础布局

```typescript
// src/layouts/BasicLayout/index.tsx
import { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Breadcrumb } from 'antd';
import { Outlet, useNavigate, useLocation } from 'ice';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  HomeOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  DashboardOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { reportAction } from '@/utils/aem';
import styles from './index.module.css';

const { Header, Sider, Content } = Layout;

const BasicLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // 侧边栏菜单
  const menuItems: MenuProps['items'] = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/user',
      icon: <TeamOutlined />,
      label: '用户管理',
      children: [
        {
          key: '/user/list',
          label: '用户列表',
        },
      ],
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ];

  // 用户下拉菜单
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
      onClick: () => {
        navigate('/profile');
        reportAction({ name: 'profile_click' });
      },
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: () => {
        localStorage.removeItem('token');
        navigate('/login');
        reportAction({ name: 'logout_click' });
      },
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
    reportAction({ name: 'menu_click', data: { path: key } });
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 侧边栏 */}
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        width={200}
        className={styles.sider}
      >
        <div className={styles.logo}>
          {collapsed ? 'LOGO' : 'My Application'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>

      <Layout>
        {/* 顶部导航 */}
        <Header className={styles.header}>
          <div className={styles.headerLeft}>
            {collapsed ? (
              <MenuUnfoldOutlined
                className={styles.trigger}
                onClick={() => setCollapsed(false)}
              />
            ) : (
              <MenuFoldOutlined
                className={styles.trigger}
                onClick={() => setCollapsed(true)}
              />
            )}
          </div>

          <div className={styles.headerRight}>
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <div className={styles.userInfo}>
                <Avatar icon={<UserOutlined />} />
                <span className={styles.username}>Admin</span>
              </div>
            </Dropdown>
          </div>
        </Header>

        {/* 面包屑 */}
        <div className={styles.breadcrumb}>
          <Breadcrumb>
            <Breadcrumb.Item>
              <HomeOutlined />
            </Breadcrumb.Item>
            <Breadcrumb.Item>当前页面</Breadcrumb.Item>
          </Breadcrumb>
        </div>

        {/* 内容区域 */}
        <Content className={styles.content}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default BasicLayout;
```

```css
/* src/layouts/BasicLayout/index.module.css */
.sider {
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
}

.logo {
  height: 32px;
  margin: 16px;
  background: rgba(255, 255, 255, 0.3);
  text-align: center;
  line-height: 32px;
  color: #fff;
  font-weight: bold;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.headerLeft {
  display: flex;
  align-items: center;
}

.trigger {
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s;
}

.trigger:hover {
  color: #1890ff;
}

.headerRight {
  display: flex;
  align-items: center;
}

.userInfo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.userInfo:hover {
  background-color: #f0f0f0;
}

.username {
  font-size: 14px;
}

.breadcrumb {
  padding: 16px 24px;
  background: #fff;
}

.content {
  margin: 16px;
  padding: 24px;
  background: #fff;
  border-radius: 4px;
  min-height: 280px;
}
```

## 业务组件

### 文件上传组件

```typescript
// src/components/Upload/index.tsx
import { useState } from 'react';
import { Upload as AntUpload, Button, message, Image } from 'antd';
import { UploadOutlined, PlusOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import { upload } from '@/services/base';

interface CustomUploadProps {
  value?: string | string[];
  onChange?: (value: string | string[]) => void;
  maxCount?: number;
  accept?: string;
  listType?: 'text' | 'picture' | 'picture-card';
}

const CustomUpload: FC<CustomUploadProps> = ({
  value,
  onChange,
  maxCount = 1,
  accept = 'image/*',
  listType = 'picture-card',
}) => {
  const [fileList, setFileList] = useState<UploadFile[]>(() => {
    if (!value) return [];
    const urls = Array.isArray(value) ? value : [value];
    return urls.map((url, index) => ({
      uid: `${index}`,
      name: url.split('/').pop() || '',
      status: 'done',
      url,
    }));
  });

  const handleChange: UploadProps['onChange'] = ({ fileList: newFileList }) => {
    setFileList(newFileList);

    // 过滤出已成功上传的文件
    const doneFiles = newFileList.filter((file) => file.status === 'done');
    const urls = doneFiles
      .map((file) => file.response?.data?.url || file.url)
      .filter(Boolean);

    if (onChange) {
      onChange(maxCount === 1 ? urls[0] : urls);
    }
  };

  const customRequest = async ({ file, onSuccess, onError, onProgress }: any) => {
    try {
      const response = await upload('/api/upload', file, (percent) => {
        onProgress({ percent });
      });

      if (response.success) {
        onSuccess(response, file);
        message.success('上传成功');
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      onError(error);
      message.error('上传失败');
    }
  };

  const beforeUpload = (file: File) => {
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
      message.error('文件大小不能超过 2MB');
      return false;
    }
    return true;
  };

  const uploadButton = (
    <div>
      <PlusOutlined />
      <div style={{ marginTop: 8 }}>上传</div>
    </div>
  );

  return (
    <AntUpload
      listType={listType}
      fileList={fileList}
      onChange={handleChange}
      customRequest={customRequest}
      beforeUpload={beforeUpload}
      maxCount={maxCount}
      accept={accept}
    >
      {fileList.length >= maxCount ? null : uploadButton}
    </AntUpload>
  );
};

export default CustomUpload;
```

### 搜索表单组件

```typescript
// src/components/SearchForm/index.tsx
import { Form, Input, Select, DatePicker, Button, Row, Col, Space } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import type { FormInstance } from 'antd';

const { RangePicker } = DatePicker;

interface SearchFormProps {
  onSearch: (values: any) => void;
  onReset?: () => void;
  loading?: boolean;
}

const SearchForm: FC<SearchFormProps> = ({ onSearch, onReset, loading }) => {
  const [form] = Form.useForm();

  const handleReset = () => {
    form.resetFields();
    onReset?.();
  };

  return (
    <Form
      form={form}
      onFinish={onSearch}
      layout="horizontal"
      style={{ marginBottom: 16 }}
    >
      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name="keyword" label="关键词">
            <Input placeholder="请输入关键词" allowClear />
          </Form.Item>
        </Col>

        <Col span={6}>
          <Form.Item name="status" label="状态">
            <Select placeholder="请选择状态" allowClear>
              <Select.Option value="active">激活</Select.Option>
              <Select.Option value="inactive">停用</Select.Option>
            </Select>
          </Form.Item>
        </Col>

        <Col span={8}>
          <Form.Item name="dateRange" label="日期范围">
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>
        </Col>

        <Col span={4}>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SearchOutlined />}
              loading={loading}
            >
              搜索
            </Button>
            <Button icon={<ReloadOutlined />} onClick={handleReset}>
              重置
            </Button>
          </Space>
        </Col>
      </Row>
    </Form>
  );
};

export default SearchForm;
```

## 自定义 Hooks 使用

### useRequest 使用示例

```typescript
// 自动请求
const { data, loading, error } = useRequest(getUserList);

// 手动请求
const { data, loading, run } = useRequest(getUserList, { manual: true });

useEffect(() => {
  run({ page: 1 });
}, []);

// 带回调
const { run } = useRequest(createUser, {
  manual: true,
  onSuccess: (data) => {
    message.success('创建成功');
    navigate('/user/list');
  },
  onError: (error) => {
    message.error(error.message);
  },
});

// 防抖请求
const { run: debouncedSearch } = useRequest(searchAPI, {
  manual: true,
  debounceWait: 500,
});

// 轮询
const { data } = useRequest(getStatus, {
  pollingInterval: 3000, // 每3秒轮询一次
});

// 刷新数据
const { data, refresh } = useRequest(getUserList);
<Button onClick={refresh}>刷新</Button>

// 手动修改数据
const { data, mutate } = useRequest(getUserList);
<Button onClick={() => mutate({ ...data, name: 'New Name' })}>更新</Button>
```

### usePagination 使用示例

```typescript
const { pagination, onChange, setTotal, reset } = usePagination({
  initialPageSize: 20,
});

// 获取数据后设置总数
const { data } = useRequest(
  () => getUserList(pagination),
  {
    onSuccess: (response) => {
      setTotal(response.data.total);
    },
  }
);

// 在 Table 中使用
<Table
  pagination={{
    ...pagination,
    onChange,
  }}
/>

// 重置分页
<Button onClick={reset}>重置</Button>
```

### useDebounce 使用示例

```typescript
const [searchValue, setSearchValue] = useState('');
const debouncedValue = useDebounce(searchValue, 500);

useEffect(() => {
  // 只在防抖后的值变化时请求
  if (debouncedValue) {
    fetchData(debouncedValue);
  }
}, [debouncedValue]);

<Input
  value={searchValue}
  onChange={(e) => setSearchValue(e.target.value)}
  placeholder="搜索..."
/>
```

## 图表示例

### 复杂图表示例

```typescript
// src/pages/Analytics/index.tsx
import { useState, useEffect } from 'react';
import { Card, Row, Col, Select, DatePicker } from 'antd';
import Chart from '@/components/Chart';
import type { EChartsOption } from 'echarts';

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('week');

  // 多轴图表
  const multiAxisOption: EChartsOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['销售额', '订单数'] },
    xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五'] },
    yAxis: [
      { type: 'value', name: '销售额', position: 'left' },
      { type: 'value', name: '订单数', position: 'right' },
    ],
    series: [
      {
        name: '销售额',
        type: 'bar',
        data: [320, 432, 301, 534, 490],
      },
      {
        name: '订单数',
        type: 'line',
        yAxisIndex: 1,
        data: [120, 182, 191, 234, 290],
      },
    ],
  };

  // 堆叠区域图
  const stackedAreaOption: EChartsOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['直接访问', '搜索引擎', '社交媒体'] },
    xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月'] },
    yAxis: { type: 'value' },
    series: [
      {
        name: '直接访问',
        type: 'line',
        stack: 'Total',
        areaStyle: {},
        data: [320, 332, 301, 334, 390],
      },
      {
        name: '搜索引擎',
        type: 'line',
        stack: 'Total',
        areaStyle: {},
        data: [220, 182, 191, 234, 290],
      },
      {
        name: '社交媒体',
        type: 'line',
        stack: 'Total',
        areaStyle: {},
        data: [150, 232, 201, 154, 190],
      },
    ],
  };

  // 雷达图
  const radarOption: EChartsOption = {
    title: { text: '产品评分' },
    radar: {
      indicator: [
        { name: '功能', max: 100 },
        { name: '性能', max: 100 },
        { name: '易用性', max: 100 },
        { name: '稳定性', max: 100 },
        { name: '文档', max: 100 },
      ],
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [80, 90, 85, 95, 70],
            name: '产品A',
          },
          {
            value: [70, 80, 90, 80, 85],
            name: '产品B',
          },
        ],
      },
    ],
  };

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col>
          <Select
            value={timeRange}
            onChange={setTimeRange}
            style={{ width: 120 }}
          >
            <Select.Option value="week">最近一周</Select.Option>
            <Select.Option value="month">最近一月</Select.Option>
            <Select.Option value="year">最近一年</Select.Option>
          </Select>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="销售与订单">
            <Chart option={multiAxisOption} height={400} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="流量来源">
            <Chart option={stackedAreaOption} height={400} />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="产品评分">
            <Chart option={radarOption} height={400} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Analytics;
```

## 微前端示例

### 完整微前端应用

```typescript
// 主应用 src/MicroApp.tsx
import { useState, useEffect } from 'react';
import { AppRouter, AppRoute, AppLink } from '@ice/stark';
import { store as microStore } from '@ice/stark-data';
import { Layout, Menu, Spin } from 'antd';

export default function MicroApp() {
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // 从本地存储获取用户信息
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
    setUser(userInfo);
    
    // 共享用户信息给子应用
    microStore.set('user', userInfo);
    
    // 共享全局配置
    microStore.set('config', {
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
      theme: {
        primaryColor: '#1890ff',
      },
    });
  }, []);

  return (
    <Layout>
      <Layout.Header>
        <Menu mode="horizontal">
          <Menu.Item key="home">
            <AppLink to="/">首页</AppLink>
          </Menu.Item>
          <Menu.Item key="app1">
            <AppLink to="/micro-app1">应用1</AppLink>
          </Menu.Item>
          <Menu.Item key="app2">
            <AppLink to="/micro-app2">应用2</AppLink>
          </Menu.Item>
        </Menu>
      </Layout.Header>

      <Layout.Content style={{ padding: 24 }}>
        <Spin spinning={loading}>
          <AppRouter
            onLoadingApp={() => setLoading(true)}
            onFinishLoading={() => setLoading(false)}
            onError={(err) => {
              console.error('微应用加载错误:', err);
              setLoading(false);
            }}
          >
            <AppRoute
              path="/micro-app1"
              name="microApp1"
              title="微应用1"
              url={['//localhost:3001/js/index.js']}
              props={{ user }}
            />
            <AppRoute
              path="/micro-app2"
              name="microApp2"
              title="微应用2"
              url={['//localhost:3002/js/index.js']}
              props={{ user }}
            />
          </AppRouter>
        </Spin>
      </Layout.Content>
    </Layout>
  );
}
```

```typescript
// 子应用 src/app.tsx
import { defineAppConfig } from 'ice';
import {
  isInIcestark,
  getMountNode,
  getBasename,
  registerAppEnter,
  registerAppLeave,
} from '@ice/stark-app';
import { store as microStore } from '@ice/stark-data';

// 生命周期钩子
registerAppEnter((props) => {
  console.log('子应用启动', props);
  
  // 获取主应用传递的用户信息
  const user = microStore.get('user');
  console.log('用户信息:', user);
  
  // 获取主应用配置
  const config = microStore.get('config');
  console.log('全局配置:', config);
});

registerAppLeave(() => {
  console.log('子应用卸载');
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

