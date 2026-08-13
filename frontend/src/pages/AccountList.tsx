import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, Space, Card, message, Modal, Form, Input, Switch, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CheckCircleOutlined, CloseCircleOutlined, SearchOutlined } from '@ant-design/icons';
import { PublicAccount } from '../types';
import { accountService } from '../services/accountService';

const { Search } = Input;

const AccountList: React.FC = () => {
  const [accounts, setAccounts] = useState<PublicAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingAccount, setEditingAccount] = useState<PublicAccount | null>(null);
  const [total, setTotal] = useState(0);
  const [allAccounts, setAllAccounts] = useState<PublicAccount[]>([]);
  const [searchParams, setSearchParams] = useState({
    nickname: '',
    account_appID: '',
  });
  const [form] = Form.useForm();

  const loadAccounts = useCallback(async () => {
    setLoading(true);
    try {
      const response = await accountService.getAccountList({ page: 1, limit: 100 });
      const accountsData = response.data?.data || [];
      setAllAccounts(accountsData);
      
      // 前端搜索过滤
      let filteredAccounts = accountsData;
      if (searchParams.nickname) {
        filteredAccounts = filteredAccounts.filter(account => 
          account.nickname?.toLowerCase().includes(searchParams.nickname.toLowerCase())
        );
      }
      if (searchParams.account_appID) {
        filteredAccounts = filteredAccounts.filter(account => 
          account.account_appID?.toLowerCase().includes(searchParams.account_appID.toLowerCase())
        );
      }

      
      setAccounts(filteredAccounts);
      setTotal(filteredAccounts.length);
    } catch (error) {
      // 错误已在 api.ts 中统一处理
    } finally {
      setLoading(false);
    }
  }, [searchParams]);

  useEffect(() => {
    loadAccounts();
  }, [loadAccounts]);

  const handleSearch = (field: string, value: string) => {
    setSearchParams(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleAdd = () => {
    setEditingAccount(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (account: PublicAccount) => {
    setEditingAccount(account);
    form.setFieldsValue(account);
    setModalVisible(true);
  };

  const handleDelete = (account: PublicAccount) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除账号 "${account.nickname || account.account_appID}" 吗？`,
      onOk: async () => {
        try {
          await accountService.deleteAccount(account.id);
            message.success('删除成功');
            loadAccounts();
        } catch (error) {
          // 错误已在 api.ts 中统一处理
        }
      },
    });
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingAccount) {
        // 更新账号
        await accountService.updateAccount(editingAccount.id, {
          account_appID: values.account_appID,
          appsecret: values.appsecret,
          notes: values.notes || '',
          authorized: values.authorized
        });
      } else {
        // 创建账号
        await accountService.createAccount({
          account_appID: values.account_appID,
          appsecret: values.appsecret,
          notes: values.notes || ''
        });
      }
      
        message.success(editingAccount ? '更新成功' : '添加成功');
        setModalVisible(false);
        loadAccounts();
    } catch (error) {
      // 错误已在 api.ts 中统一处理
    }
  };

  const columns = [
    {
      title: '账号昵称',
      dataIndex: 'nickname',
      key: 'nickname',
    },
    {
      title: 'AppID',
      dataIndex: 'account_appID',
      key: 'account_appID',
      width: 200,
      ellipsis: true,
      render: (text: string) => (
        <code style={{ background: '#f5f5f5', padding: '2px 6px', borderRadius: '4px' }}>
          {text}
        </code>
      ),
    },
    {
      title: '备注',
      dataIndex: 'notes',
      key: 'notes',
      width: 150,
      ellipsis: true,
    },
    {
      title: '授权状态',
      dataIndex: 'authorized',
      key: 'authorized',
      render: (authorized: boolean) => (
        <Tag color={authorized ? 'success' : 'error'} icon={authorized ? <CheckCircleOutlined /> : <CloseCircleOutlined />}>
          {authorized ? '已授权' : '未授权'}
        </Tag>
      ),
    },
    {
      title: '状态',
      key: 'status',
      render: (record: PublicAccount) => (
        <Tag color={record.deleted_time ? 'error' : 'success'}>
          {record.deleted_time ? '已删除' : '正常'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (record: PublicAccount) => (
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
        {/* 搜索栏和操作按钮 */}
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Search
              placeholder="搜索账号昵称"
              allowClear
              style={{ width: 200 }}
              onSearch={(value) => handleSearch('nickname', value)}
              enterButton={<SearchOutlined />}
            />
            <Search
              placeholder="搜索AppID"
              allowClear
              style={{ width: 200 }}
              onSearch={(value) => handleSearch('account_appID', value)}
              enterButton={<SearchOutlined />}
            />
          </Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            添加账号
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={accounts}
          rowKey="id"
          loading={loading}
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
        title={editingAccount ? '编辑账号' : '添加账号'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >


          <Form.Item
            name="account_appID"
            label="AppID"
            rules={[{ required: true, message: '请输入AppID' }]}
          >
            <Input placeholder="请输入微信公众号AppID" />
          </Form.Item>

          <Form.Item
            name="appsecret"
            label="AppSecret"
            rules={[{ required: true, message: '请输入AppSecret' }]}
          >
            <Input.Password placeholder="请输入微信公众号AppSecret" />
          </Form.Item>

          <Form.Item
            name="notes"
            label="备注"
          >
            <Input.TextArea rows={3} placeholder="请输入备注信息" />
          </Form.Item>

          {editingAccount && (
            <Form.Item
              name="authorized"
              label="授权状态"
              valuePropName="checked"
            >
              <Switch checkedChildren="已授权" unCheckedChildren="未授权" />
            </Form.Item>
          )}

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingAccount ? '更新' : '添加'}
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

export default AccountList; 