import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Avatar, Button, Form, Input, message, Modal, Upload, Statistic } from 'antd';
import { UserOutlined, EditOutlined, CameraOutlined, LockOutlined, ClockCircleOutlined, TeamOutlined } from '@ant-design/icons';
import { User } from '../types';
import { profileService } from '../services/profileService';
import { getUserDisplayName, getUserAvatarUrl, hasValidAvatar, processUserData, processAvatarUrl } from '../utils/userUtils';
import dayjs from 'dayjs';

const Profile: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [passwordModalVisible, setPasswordModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    setLoading(true);
    try {
      const response = await profileService.getUserProfile();
      if (response.data) {
        // 使用工具函数处理用户数据，包括头像URL
        const processedUserData = processUserData(response.data);
        setUser(processedUserData);
      }
    } catch (error) {
      // 错误已在 api.ts 中统一处理
    } finally {
      setLoading(false);
    }
  };

  const handleEditProfile = () => {
    if (user) {
      form.setFieldsValue(user);
      setEditModalVisible(true);
    }
  };

  const handleUpdateProfile = async (values: any) => {
    try {
      await profileService.updateProfile(values);
        message.success('更新成功');
        setEditModalVisible(false);
        loadUserProfile();
    } catch (error) {
      // 错误已在 api.ts 中统一处理
    }
  };

  const handleChangePassword = async (values: any) => {
    try {
      await profileService.changePassword(values);
        message.success('密码修改成功');
        setPasswordModalVisible(false);
        passwordForm.resetFields();
    } catch (error) {
      console.log(error);
    }
  };

  const handleAvatarUpload = async (file: any) => {
    if (!user?.id) {
      message.error('用户信息不完整，无法上传头像');
      return false;
    }

    try {
      const response = await profileService.uploadAvatar(file, user.id);
        message.success('头像更新成功');
        
        // 更新本地用户头像信息，使用工具函数处理URL
        if (response.data?.avatar_url) {
          const fullAvatarUrl = processAvatarUrl(response.data.avatar_url);
          
          // 立即更新本地用户数据，避免刷新后头像丢失
          setUser(prevUser => prevUser ? {
            ...prevUser,
            avatar: fullAvatarUrl
          } : null);
        }
        
        // 重新加载用户信息以确保数据同步
        loadUserProfile();
    } catch (error) {
      // 错误已在 api.ts 中统一处理
    }
    return false; // 阻止默认上传行为
  };

  const getDaysUntilExpire = () => {
    if (!user?.expire_time) return 0;
    const expireDate = dayjs(user.expire_time);
    const now = dayjs();
    return expireDate.diff(now, 'day');
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '正常';
      case 'expired': return '已过期';
      case 'suspended': return '已暂停';
      default: return '未知';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#52c41a';
      case 'expired': return '#faad14';
      case 'suspended': return '#ff4d4f';
      default: return '#d9d9d9';
    }
  };

  if (!user) {
    return <div>加载中...</div>;
  }

  return (
    <div>
      <Row gutter={[24, 24]}>
        {/* 用户基本信息 */}
        <Col xs={24} lg={8}>
          <Card title="账号信息" loading={loading}>
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <Upload
                showUploadList={false}
                beforeUpload={handleAvatarUpload}
                accept="image/*"
              >
                <div style={{ position: 'relative', display: 'inline-block' }}>
                  <Avatar
                    size={120}
                    src={getUserAvatarUrl(user)}
                    icon={!hasValidAvatar(user) ? <UserOutlined /> : undefined}
                    style={{ cursor: 'pointer' }}
                  />
                  <div style={{
                    position: 'absolute',
                    bottom: 0,
                    right: 0,
                    background: '#1890ff',
                    borderRadius: '50%',
                    width: 32,
                    height: 32,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer'
                  }}>
                    <CameraOutlined style={{ color: 'white', fontSize: 16 }} />
                  </div>
                </div>
              </Upload>
              <h3 style={{ marginTop: 16, marginBottom: 8 }}>
                {getUserDisplayName(user)}
              </h3>
              <p style={{ color: '#666', margin: 0 }}>
                {user.is_main ? '主账号' : '普通账号'}
              </p>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Row>
                <Col span={8}>用户名:</Col>
                <Col span={16}>{user.username || '-'}</Col>
              </Row>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Row>
                <Col span={8}>手机号:</Col>
                <Col span={16}>{user.phone || '-'}</Col>
              </Row>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Row>
                <Col span={8}>邮箱:</Col>
                <Col span={16}>{user.email || '-'}</Col>
              </Row>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Row>
                <Col span={8}>状态:</Col>
                <Col span={16}>
                  <span style={{ color: getStatusColor(user.status) }}>
                    {getStatusText(user.status)}
                  </span>
                </Col>
              </Row>
            </div>

            <div style={{ marginBottom: 24 }}>
              <Row>
                <Col span={8}>密码:</Col>
                <Col span={16}>••••••••</Col>
              </Row>
            </div>

            <Button
              type="primary"
              icon={<EditOutlined />}
              onClick={handleEditProfile}
              block
              style={{ marginBottom: 12 }}
            >
              编辑资料
            </Button>

            <Button
              icon={<LockOutlined />}
              onClick={() => setPasswordModalVisible(true)}
              block
            >
              修改密码
            </Button>
          </Card>
        </Col>

        {/* 账号统计 */}
        <Col xs={24} lg={16}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12}>
              <Card>
                <Statistic
                  title="绑定限制"
                  value={user.bind_limit}
                  prefix={<TeamOutlined />}
                  suffix="个"
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>

            <Col xs={24} sm={12}>
              <Card>
                <Statistic
                  title="已绑定数量"
                  value={user.bound_accounts}
                  prefix={<TeamOutlined />}
                  suffix="个"
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>

            <Col xs={24} sm={12}>
              <Card>
                <Statistic
                  title="登录次数"
                  value={user.login_count}
                  prefix={<UserOutlined />}
                  suffix="次"
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>

            <Col xs={24} sm={12}>
              <Card>
                <Statistic
                  title="剩余天数"
                  value={getDaysUntilExpire()}
                  prefix={<ClockCircleOutlined />}
                  suffix="天"
                  valueStyle={{
                    color: getDaysUntilExpire() > 30 ? '#52c41a' : getDaysUntilExpire() > 7 ? '#faad14' : '#ff4d4f'
                  }}
                />
              </Card>
            </Col>
          </Row>

          <Card title="账号详情" style={{ marginTop: 16 }}>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12}>
                <div style={{ marginBottom: 16 }}>
                  <strong>注册时间:</strong>
                  <br />
                  {user.register_time ? dayjs(user.register_time).format('YYYY-MM-DD HH:mm:ss') : '-'}
                </div>
              </Col>
              <Col xs={24} sm={12}>
                <div style={{ marginBottom: 16 }}>
                  <strong>过期时间:</strong>
                  <br />
                  {user.expire_time ? dayjs(user.expire_time).format('YYYY-MM-DD HH:mm:ss') : '-'}
                </div>
              </Col>
            </Row>

            {getDaysUntilExpire() <= 30 && (
              <div style={{
                background: getDaysUntilExpire() <= 7 ? '#fff2f0' : '#fffbe6',
                border: `1px solid ${getDaysUntilExpire() <= 7 ? '#ffccc7' : '#ffe58f'}`,
                borderRadius: 4,
                padding: 16,
                marginTop: 16
              }}>
                <p style={{ margin: 0, color: getDaysUntilExpire() <= 7 ? '#cf1322' : '#d46b08' }}>
                  <ClockCircleOutlined /> 您的账号将在 {getDaysUntilExpire()} 天后过期，请及时续费。
                </p>
                <Button
                  type="primary"
                  danger={getDaysUntilExpire() <= 7}
                  style={{ marginTop: 12 }}
                >
                  立即续费
                </Button>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* 编辑资料模态框 */}
      <Modal
        title="编辑资料"
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleUpdateProfile}
        >
          <Form.Item
            name="nickname"
            label="昵称"
            rules={[{ required: true, message: '请输入昵称' }]}
          >
            <Input placeholder="请输入昵称" />
          </Form.Item>

          <Form.Item
            name="username"
            label="用户名"
          >
            <Input placeholder="请输入用户名" />
          </Form.Item>

          <Form.Item
            name="phone"
            label="手机号"
          >
            <Input placeholder="请输入手机号" />
          </Form.Item>

          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="请输入邮箱地址" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" style={{ marginRight: 8 }}>
              保存
            </Button>
            <Button onClick={() => setEditModalVisible(false)}>
              取消
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* 修改密码模态框 */}
      <Modal
        title="修改密码"
        open={passwordModalVisible}
        onCancel={() => setPasswordModalVisible(false)}
        footer={null}
        width={500}
      >
        <Form
          form={passwordForm}
          layout="vertical"
          onFinish={handleChangePassword}
        >
          <Form.Item
            name="currentPassword"
            label="当前密码"
            rules={[{ required: true, message: '请输入当前密码' }]}
          >
            <Input.Password placeholder="请输入当前密码" />
          </Form.Item>

          <Form.Item
            name="newPassword"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码长度至少6位' }
            ]}
          >
            <Input.Password placeholder="请输入新密码" />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            label="确认新密码"
            dependencies={['newPassword']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('newPassword') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password placeholder="请再次输入新密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" style={{ marginRight: 8 }}>
              修改密码
            </Button>
            <Button onClick={() => setPasswordModalVisible(false)}>
              取消
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Profile; 