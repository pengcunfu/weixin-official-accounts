import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, Space, Card, message, Modal, Form, Input, Select, Tag, Avatar, DatePicker } from 'antd';
import { EditOutlined, DeleteOutlined, UserOutlined, SearchOutlined } from '@ant-design/icons';
import { User } from '../types';
import { userService } from '../services/userService';
import { getUserAvatarUrl, hasValidAvatar, processUserData } from '../utils/userUtils';
import dayjs from 'dayjs';

const { Option } = Select;
const { Search } = Input;

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [total, setTotal] = useState(0);
  const [searchParams, setSearchParams] = useState({
    nickname: '',
    username: '',
    email: '',
    status: '',
  });
  const [form] = Form.useForm();

  const loadUsers = useCallback(async () => {
    setLoading(true);
    try {
      const response = await userService.getUserList();
      if (response.data) {
        // 处理用户数据，包括头像URL
        let processedUsers = (response.data.data || []).map((user: User) => processUserData(user));
        
        // 前端搜索过滤
        if (searchParams.nickname) {
          processedUsers = processedUsers.filter(user => 
            user.nickname?.toLowerCase().includes(searchParams.nickname.toLowerCase())
          );
        }
        if (searchParams.username) {
          processedUsers = processedUsers.filter(user => 
            user.username?.toLowerCase().includes(searchParams.username.toLowerCase())
          );
        }
        if (searchParams.email) {
          processedUsers = processedUsers.filter(user => 
            user.email?.toLowerCase().includes(searchParams.email.toLowerCase())
          );
        }
        if (searchParams.status) {
          processedUsers = processedUsers.filter(user => user.status === searchParams.status);
        }
        
        setUsers(processedUsers);
        setTotal(processedUsers.length);
      }
    } catch (error) {
      // 错误已在 api.ts 中统一处理
    } finally {
      setLoading(false);
    }
  }, [searchParams]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleSearch = (field: string, value: string) => {
    setSearchParams(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleStatusFilter = (value: string) => {
    setSearchParams(prev => ({
      ...prev,
      status: value,
    }));
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    form.setFieldsValue({
      ...user,
      expire_time: user.expire_time ? dayjs(user.expire_time) : null,
    });
    setModalVisible(true);
  };

  const handleDelete = (user: User) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除用户 "${user.nickname}" 吗？`,
      onOk: async () => {
        try {
          await userService.deleteUser(user.id);
            message.success('删除成功');
            loadUsers();
        } catch (error) {
          // 错误已在 api.ts 中统一处理
        }
      },
    });
  };

  const handleSubmit = async (values: any) => {
    if (!editingUser) {
      message.error('用户信息错误');
      return;
    }
    
    try {
      const submitData = {
        ...values,
        expire_time: values.expire_time ? values.expire_time.format('YYYY-MM-DD HH:mm:ss') : null,
      };
      
      await userService.updateUser(editingUser.id, submitData);
        message.success('更新成功');
        setModalVisible(false);
        loadUsers();
    } catch (error) {
      // 错误已在 api.ts 中统一处理
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'expired': return 'warning';
      case 'suspended': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '正常';
      case 'expired': return '已过期';
      case 'suspended': return '已暂停';
      default: return '未知';
    }
  };

  const columns = [
    {
      title: '头像',
      dataIndex: 'avatar',
      key: 'avatar',
      width: 80,
      render: (avatar: string, record: User) => (
        <Avatar 
          src={getUserAvatarUrl(record)} 
          icon={!hasValidAvatar(record) ? <UserOutlined /> : undefined}
          size="default"
        />
      ),
    },
    {
      title: '昵称',
      dataIndex: 'nickname',
      key: 'nickname',
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '手机号',
      dataIndex: 'phone',
      key: 'phone',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '账号类型',
      dataIndex: 'is_main',
      key: 'is_main',
      render: (isMain: boolean) => (
        <Tag color={isMain ? 'gold' : 'blue'}>
          {isMain ? '主账号' : '普通账号'}
        </Tag>
      ),
    },
    {
      title: '绑定限制',
      dataIndex: 'bind_limit',
      key: 'bind_limit',
    },
    {
      title: '已绑定数量',
      dataIndex: 'bound_accounts',
      key: 'bound_accounts',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '过期时间',
      dataIndex: 'expire_time',
      key: 'expire_time',
      render: (time: string) => time ? dayjs(time).format('YYYY-MM-DD') : '-',
    },
    {
      title: '登录次数',
      dataIndex: 'login_count',
      key: 'login_count',
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (record: User) => (
        <Space>
          <Button 
            type="primary" 
            size="small" 
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button 
            danger 
            size="small" 
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card>
        {/* 搜索栏 */}
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Search
              placeholder="搜索昵称"
              allowClear
              style={{ width: 200 }}
              onSearch={(value) => handleSearch('nickname', value)}
              enterButton={<SearchOutlined />}
            />
            <Search
              placeholder="搜索用户名"
              allowClear
              style={{ width: 200 }}
              onSearch={(value) => handleSearch('username', value)}
              enterButton={<SearchOutlined />}
            />
            <Search
              placeholder="搜索邮箱"
              allowClear
              style={{ width: 200 }}
              onSearch={(value) => handleSearch('email', value)}
              enterButton={<SearchOutlined />}
            />
            <Select
              placeholder="选择状态"
              style={{ width: 120 }}
              allowClear
              onChange={handleStatusFilter}
            >
              <Option value="active">正常</Option>
              <Option value="expired">已过期</Option>
              <Option value="suspended">已暂停</Option>
            </Select>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            total: total,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      <Modal
        title="编辑用户"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="nickname"
            label="昵称"
            rules={[{ required: true, message: '请输入昵称' }]}
          >
            <Input placeholder="请输入用户昵称" />
          </Form.Item>

          <Form.Item
            name="username"
            label="用户名"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input placeholder="请输入用户名" />
          </Form.Item>

          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="请输入邮箱地址" />
          </Form.Item>

          <Form.Item
            name="phone"
            label="手机号"
          >
            <Input placeholder="请输入手机号" />
          </Form.Item>

          <Form.Item
            name="is_main"
            label="账号类型"
            rules={[{ required: true, message: '请选择账号类型' }]}
          >
            <Select placeholder="请选择账号类型">
              <Option value={true}>主账号</Option>
              <Option value={false}>普通账号</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="bind_limit"
            label="绑定限制"
            rules={[{ required: true, message: '请输入绑定限制数量' }]}
          >
            <Input type="number" placeholder="最大绑定公众号数量" />
          </Form.Item>

          <Form.Item
            name="status"
            label="状态"
            rules={[{ required: true, message: '请选择用户状态' }]}
          >
            <Select placeholder="请选择用户状态">
              <Option value="active">正常</Option>
              <Option value="expired">已过期</Option>
              <Option value="suspended">已暂停</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="expire_time"
            label="过期时间"
          >
            <DatePicker 
              style={{ width: '100%' }}
              placeholder="请选择过期时间"
              showTime
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                更新
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserList; 