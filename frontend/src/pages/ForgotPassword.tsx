import React, { useState } from 'react';
import { Card, Form, Input, Button, message } from 'antd';
import { MailOutlined, LockOutlined, SafetyOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
// 使用Ant Design默认样式

interface ForgotPasswordFormData {
  email: string;
  verification_code: string;
  new_password: string;
  confirm_password: string;
}

const ForgotPassword: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [form] = Form.useForm();

  // 发送验证码
  const handleSendCode = async () => {
    try {
      const email = form.getFieldValue('email');
      if (!email) {
        message.error('请先输入邮箱地址');
        return;
      }

      // 验证邮箱格式
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        message.error('请输入正确的邮箱格式');
        return;
      }

      setSendingCode(true);
      
      // 开始倒计时
      setCountdown(60);
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      await authService.sendVerificationCode(email, 'reset_password');
      message.success('验证码已发送到您的邮箱');
    } catch (error: any) {
      // 错误已在 api.ts 中统一处理
      // 如果发送失败，清除倒计时
      setCountdown(0);
    } finally {
      setSendingCode(false);
    }
  };

  // 处理重置密码
  const handleResetPassword = async (values: ForgotPasswordFormData) => {
    if (values.new_password !== values.confirm_password) {
      message.error('两次输入的密码不一致');
      return;
    }

    setLoading(true);
    try {
      // 根据后端API接口调整参数
      const resetData = {
        email: values.email,
        verification_code: values.verification_code,
        new_password: values.new_password
      };
      
      await authService.resetPassword(resetData);
      message.success('密码重置成功，请使用新密码登录');
      navigate('/login');
    } catch (error: any) {
      // 错误已在 api.ts 中统一处理
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      background: '#f0f2f5',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <h1 style={{ fontSize: 28, fontWeight: 500, color: '#262626', margin: 0 }}>重置密码</h1>
        </div>
        
        <Form
          form={form}
          name="forgot-password"
          onFinish={handleResetPassword}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入正确的邮箱格式' }
            ]}
          >
            <Input 
              prefix={<MailOutlined />}
              size="large"
              placeholder="请输入邮箱"
            />
          </Form.Item>

          <Form.Item
            name="verification_code"
            rules={[{ required: true, message: '请输入验证码' }]}
          >
            <div style={{ display: 'flex', gap: 8 }}>
              <Input 
                prefix={<SafetyOutlined />}
                size="large"
                placeholder="请输入验证码"
                style={{ flex: 1 }}
              />
              <Button
                onClick={handleSendCode}
                loading={sendingCode}
                disabled={countdown > 0}
                style={{ minWidth: 120 }}
                size="large"
              >
                {countdown > 0 ? `${countdown}s` : '获取验证码'}
              </Button>
            </div>
          </Form.Item>

          <Form.Item
            name="new_password"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码至少6个字符' }
            ]}
          >
            <Input.Password 
              prefix={<LockOutlined />}
              placeholder="请输入新密码"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="confirm_password"
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password 
              prefix={<LockOutlined />}
              placeholder="请再次输入新密码"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
            >
              重置密码
            </Button>
          </Form.Item>

          <Form.Item>
            <Button
              type="default"
              block
              onClick={() => navigate('/login')}
              size="large"
            >
              返回登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default ForgotPassword; 