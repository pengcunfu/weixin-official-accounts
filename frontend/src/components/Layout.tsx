import React, { useEffect, useState } from 'react';
import { Layout, Menu, Breadcrumb, Dropdown, Avatar, Space } from 'antd';
import {
  HomeOutlined,
  FileTextOutlined,
  TeamOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../services/authService';
import { profileService } from '../services/profileService';
import { User } from '../types';
import { getUserDisplayName, getUserAvatarUrl, getUserInitial, hasValidAvatar, processUserData } from '../utils/userUtils';
import type { MenuProps } from 'antd';

const { Header, Sider, Content } = Layout;

interface MenuItem {
  key: string;
  icon: React.ReactNode;
  label: string;
  path: string;
}

const AppLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState<User | null>(null);
  const [collapsed, setCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);

  // 菜单项定义
  const menuItems: MenuItem[] = [
    {
      key: 'dashboard',
      icon: <HomeOutlined />,
      label: '首页',
      path: '/dashboard'
    },
    {
      key: 'accounts',
      icon: <UserOutlined />,
      label: '公众号管理',
      path: '/accounts'
    },
    {
      key: 'articles',
      icon: <FileTextOutlined />,
      label: '文章管理',
      path: '/articles'
    },
    {
      key: 'users',
      icon: <TeamOutlined />,
      label: '用户管理',
      path: '/users'
    },
    {
      key: 'profile',
      icon: <SettingOutlined />,
      label: '个人设置',
      path: '/profile'
    }
  ];

  // 页面标题映射
  const pageTitles: Record<string, string> = {
    '/dashboard': '仪表盘',
    '/accounts': '公众号管理',
    '/articles': '文章管理',
    '/articles/upload': '文章上传',
    '/articles/edit': '编辑文章',
    '/users': '用户管理',
    '/profile': '个人设置'
  };

  // 获取当前页面标题
  const getCurrentPageTitle = () => {
    const path = location.pathname;
    if (path.startsWith('/articles/edit/')) {
      return '编辑文章';
    }
    return pageTitles[path] || '未知页面';
  };

  // 生成面包屑
  const getBreadcrumbItems = () => {
    const path = location.pathname;
    const items = [
      { title: '首页' }
    ];

    if (path !== '/dashboard') {
      const currentTitle = getCurrentPageTitle();
      items.push({ title: currentTitle });
    }

    return items;
  };

  // 检查用户认证状态
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        // 先检查auth状态，然后获取完整的profile信息
        const authResponse = await authService.checkAuth();
        if (authResponse && authResponse.data) {
          // 获取完整的用户资料信息
          const profileResponse = await profileService.getUserProfile();
          if (profileResponse.code === 200 && profileResponse.data) {
            // 使用工具函数处理用户数据，包括头像URL
            setUser(processUserData(profileResponse.data));
          } else {
            setUser(processUserData(authResponse.data));
          }
        } else {
          localStorage.removeItem('token');
          navigate('/login');
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        localStorage.removeItem('token');
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [navigate]);

  // 处理菜单点击
  const handleMenuClick = (e: { key: string }) => {
    const item = menuItems.find(item => item.key === e.key);
    if (item) {
      navigate(item.path);
    }
  };

  // 处理退出登录
  const handleLogout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('退出登录失败:', error);
    } finally {
      localStorage.removeItem('token');
      navigate('/login');
    }
  };

  // 用户下拉菜单
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      label: '个人设置',
      icon: <UserOutlined />,
      onClick: () => navigate('/profile')
    },
    {
      type: 'divider'
    },
    {
      key: 'logout',
      label: '退出登录',
      icon: <LogoutOutlined />,
      onClick: handleLogout
    }
  ];

  // 获取当前选中的菜单项
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.startsWith('/articles')) return 'articles';
    if (path === '/dashboard') return 'dashboard';
    if (path === '/accounts') return 'accounts';
    if (path === '/users') return 'users';
    if (path === '/profile') return 'profile';
    return 'dashboard';
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh'
      }}>
        <div>加载中...</div>
      </div>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed} 
        theme="dark"
        collapsedWidth={80}
        width={200} 
        style={{ 
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          height: '100vh',
          zIndex: 200,
          transition: 'all 0.3s ease-in-out'
        }}
      >
        <div style={{
          height: 48,
          padding: '8px 16px',
          background: 'rgba(255, 255, 255, 0.1)',
          margin: '12px 16px',
          borderRadius: 4,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: 16,
          fontWeight: 500,
          letterSpacing: '1px',
          transition: 'all 0.3s ease-in-out',
          overflow: 'hidden',
          position: 'relative'
        }}>
          <div style={{
            transition: 'transform 0.3s ease-in-out, opacity 0.3s ease-in-out',
            transform: collapsed ? 'scale(0.9)' : 'scale(1)',
            opacity: collapsed ? 0.8 : 1,
            whiteSpace: 'nowrap'
          }}>
            {!collapsed && '公众号发文助手'}
            {collapsed && '发文助手'}
          </div>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[getSelectedKey()]}
          onClick={handleMenuClick}
          style={{ 
            height: 'calc(100vh - 72px - 80px)', // 减去标题高度(48px+24px边距)和版权信息高度
            borderRight: 0,
            overflow: 'auto'
          }}
          items={menuItems.map(item => ({
            key: item.key,
            icon: item.icon,
            label: item.label
          }))}
        />
        
        {/* 版权信息 */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          padding: '16px 12px',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          background: 'rgba(0, 0, 0, 0.2)',
          transition: 'all 0.3s ease',
          overflow: 'hidden'
        }}>
          <div style={{
            transition: 'transform 0.3s ease, opacity 0.3s ease',
            transform: collapsed ? 'translateY(-5px)' : 'translateY(0)',
            opacity: collapsed ? 0.8 : 1
          }}>
            {!collapsed && (
              <div style={{
                color: 'rgba(255, 255, 255, 0.65)',
                fontSize: 12,
                lineHeight: 1.5,
                textAlign: 'center',
                transition: 'opacity 0.3s ease 0.1s',
                opacity: collapsed ? 0 : 1
              }}>
                <div style={{ 
                  marginBottom: 4,
                  transition: 'transform 0.3s ease'
                }}>
                  © 2025 公众号发文助手
                </div>
                <div style={{
                  transition: 'transform 0.3s ease 0.1s'
                }}>
                  <a 
                    href="https://beian.miit.gov.cn" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style={{ 
                      color: 'rgba(255, 255, 255, 0.65)', 
                      textDecoration: 'none',
                      transition: 'color 0.3s ease'
                    }}
                  >
                    京ICP备12345678号
                  </a>
                </div>
              </div>
            )}
            {collapsed && (
              <div style={{
                color: 'rgba(255, 255, 255, 0.65)',
                fontSize: 10,
                textAlign: 'center',
                lineHeight: 1.2,
                transition: 'opacity 0.3s ease 0.1s',
                opacity: collapsed ? 1 : 0
              }}>
                <div style={{
                  transition: 'transform 0.3s ease',
                  transform: collapsed ? 'scale(1)' : 'scale(0.8)'
                }}>©</div>
                <div style={{
                  transition: 'transform 0.3s ease 0.1s',
                  transform: collapsed ? 'scale(1)' : 'scale(0.8)'
                }}>2025</div>
              </div>
            )}
          </div>
        </div>
      </Sider>
      <Layout style={{ 
        marginLeft: collapsed ? 80 : 200,
        transition: 'margin-left 0.2s ease'
      }}>
        <Header style={{ padding: 0, background: '#fff' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            width: '100%'
          }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div
                style={{
                  fontSize: 18,
                  lineHeight: '64px',
                  padding: '0 24px',
                  cursor: 'pointer',
                  transition: 'color 0.3s'
                }}
                onClick={() => setCollapsed(!collapsed)}
              >
                {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              </div>
              <div style={{ margin: '16px 0' }}>
                <Breadcrumb items={getBreadcrumbItems()} />
              </div>
            </div>
            
            <div style={{ paddingRight: 24 }}>
              <Dropdown 
                menu={{ items: userMenuItems }} 
                placement="bottomRight"
                trigger={['click']}
              >
                <Space style={{
                  display: 'flex',
                  alignItems: 'center',
                  cursor: 'pointer'
                }}>
                  <Avatar 
                    style={{ marginRight: 8 }}
                    src={getUserAvatarUrl(user)}
                    icon={!hasValidAvatar(user) ? <UserOutlined /> : undefined}
                  >
                    {!hasValidAvatar(user) && getUserInitial(user)}
                  </Avatar>
                  <span>{getUserDisplayName(user)}</span>
                </Space>
              </Dropdown>
            </div>
          </div>
        </Header>
        <Content
          style={{
            padding: '16px',
            minHeight: 280,
            background: '#fff'
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout; 
