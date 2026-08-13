import React, { lazy, Suspense, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { ConfigProvider, Spin, message } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import 'dayjs/locale/zh-cn';
import { setNavigate } from './services/api';

// 页面组件（路由级懒加载，减少首屏包体积）
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const ForgotPassword = lazy(() => import('./pages/ForgotPassword'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const ArticleList = lazy(() => import('./pages/ArticleList'));
const ArticleUpload = lazy(() => import('./pages/ArticleUpload'));
const ArticleEdit = lazy(() => import('./pages/ArticleEdit'));
const ArticlePreview = lazy(() => import('./pages/ArticlePreview'));
const AccountList = lazy(() => import('./pages/AccountList'));
const UserList = lazy(() => import('./pages/UserList'));
const Profile = lazy(() => import('./pages/Profile'));
import AppLayout from './components/Layout';

// Ant Design已包含所有必要样式

// 配置全局message
message.config({
  top: 100,
  duration: 3,
  maxCount: 3,
});

// 页面加载占位
function PageLoading() {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '60vh'
    }}>
      <Spin size="large" />
    </div>
  );
}

// 内部App组件，用于获取navigate
function AppContent() {
  const navigate = useNavigate();

  useEffect(() => {
    // 将navigate函数传递给api模块
    setNavigate(navigate);
  }, [navigate]);

  return (
    <Suspense fallback={<PageLoading />}>
      <Routes>
        {/* 认证相关页面 */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />

        {/* 主应用路由 */}
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />

          {/* 文章管理 */}
          <Route path="articles" element={<ArticleList />} />
          <Route path="articles/upload" element={<ArticleUpload />} />
          <Route path="articles/edit/:id" element={<ArticleEdit />} />
          <Route path="articles/preview/:id" element={<ArticlePreview />} />

          {/* 账号管理 */}
          <Route path="accounts" element={<AccountList />} />

          {/* 用户管理 */}
          <Route path="users" element={<UserList />} />

          {/* 个人中心 */}
          <Route path="profile" element={<Profile />} />
        </Route>

        {/* 404重定向 */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Suspense>
  );
}

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <AppContent />
      </Router>
    </ConfigProvider>
  );
}

export default App;
