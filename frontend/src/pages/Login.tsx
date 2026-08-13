import React, { useState } from 'react';
import { Card, Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/authService';
// 使用Ant Design默认样式

interface LoginFormData {
  username: string;
  password: string;
  remember?: boolean;
}

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  // 处理登录
  const handleLogin = async (values: LoginFormData) => {
    setLoading(true);
    try {
      const response = await authService.login({
        username: values.username,
        password: values.password,
        remember: values.remember
      });

      const token = response.data?.token;
      const user = response.data?.user;
      
      if (token && user) {
        localStorage.setItem('token', token);
        message.success('登录成功');
        navigate('/dashboard');
      } else {
        message.error('登录响应数据异常');
      }
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
          <h1 style={{ fontSize: 28, fontWeight: 500, color: '#262626', margin: 0 }}>账号登录</h1>
        </div>
        
        <Form
          name="login"
          onFinish={handleLogin}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名或邮箱' }]}
          >
            <Input 
              prefix={<UserOutlined />}
              placeholder="请输入用户名或手机号"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password 
              prefix={<LockOutlined />}
              placeholder="请输入密码"
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
              立即登录
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center', marginTop: 24, color: '#8c8c8c' }}>
            <Link to="/forgot-password" style={{ color: '#1677ff', textDecoration: 'none' }}>忘记密码？</Link>
            <span style={{ margin: '0 16px', color: '#d9d9d9' }}>|</span>
            <Link to="/register" style={{ color: '#1677ff', textDecoration: 'none' }}>立即注册</Link>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default Login; 