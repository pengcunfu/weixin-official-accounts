# 公众号发文助手 - 前端

微信公众号文章管理系统的前端应用，基于 React + TypeScript + Ant Design 构建。

## 📝 项目简介

公众号发文助手是一个专为微信公众号内容管理设计的现代化Web应用。前端提供了直观易用的界面，支持文章编辑、公众号管理、用户管理等核心功能。

## ✨ 主要功能

### 🔐 用户认证
- 用户注册、登录、密码重置
- 邮箱验证码验证
- JWT令牌认证
- 个人资料管理和头像上传

### 📄 文章管理
- 文档上传（支持.docx格式）
- 富文本编辑器
- 文章分类管理
- 批量操作（删除、保存到公众号）
- 文章状态追踪（草稿、已发布、已存稿）

### 📱 公众号管理
- 公众号账号配置（AppID、AppSecret）
- 授权状态管理
- 账号信息维护

### 👥 用户管理
- 用户列表查看
- 用户信息编辑
- 账号状态管理
- 绑定限制设置

### 📊 仪表盘
- 数据统计概览
- 快捷操作入口

## 🛠 技术栈

- **框架**: React 19
- **语言**: TypeScript
- **UI组件**: Ant Design 6.x
- **路由**: React Router v7
- **HTTP客户端**: Axios
- **日期处理**: Day.js
- **构建工具**: Vite
- **包管理**: npm

## 📁 项目结构

```
frontend/
├── index.html          # 应用入口 HTML
├── vite.config.ts      # Vite 构建配置
└── src/
├── components/           # 公共组件
│   └── Layout.tsx       # 主布局组件
├── pages/               # 页面组件
│   ├── Dashboard.tsx    # 仪表盘
│   ├── Login.tsx        # 登录页
│   ├── Register.tsx     # 注册页
│   ├── ForgotPassword.tsx # 忘记密码
│   ├── Profile.tsx      # 个人设置
│   ├── AccountList.tsx  # 公众号列表
│   ├── ArticleList.tsx  # 文章列表
│   ├── ArticleEdit.tsx  # 文章编辑
│   ├── ArticleUpload.tsx # 文章上传
│   └── UserList.tsx     # 用户管理
├── services/            # API服务层
│   ├── api.ts          # API基础配置
│   ├── authService.ts  # 认证服务
│   ├── accountService.ts # 公众号服务
│   ├── articleService.ts # 文章服务
│   ├── uploadService.ts # 上传服务
│   ├── profileService.ts # 用户资料服务
│   └── userService.ts  # 用户管理服务
├── types/               # TypeScript类型定义
│   └── index.ts        # 全局类型
├── utils/               # 工具函数
│   └── userUtils.ts    # 用户相关工具
├── App.tsx             # 根组件
├── index.tsx           # 应用入口
└── index.css           # 全局样式
```

## 🏗 架构特点

### 服务层设计
- 统一的API服务封装
- 类型安全的接口调用
- 错误处理和响应拦截
- 自动的JWT令牌管理

### 组件设计
- 函数式组件 + Hooks
- TypeScript严格类型检查
- Ant Design组件库
- 响应式布局设计

### 状态管理
- React useState/useEffect
- 本地存储管理
- 用户认证状态维护

## 🚀 快速开始

### 环境要求
- Node.js >= 20.19.0
- npm >= 10.0.0

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动

### 构建生产版本
```bash
npm run build
```

构建产物输出到 `dist/` 目录

### 类型检查
```bash
npm run typecheck
```

## 🔧 环境配置

### API地址配置
在 `src/services/api.ts` 中配置后端API地址：

```typescript
const API_BASE_URL = 'http://localhost:8000/api'
```

### 开发环境变量
可以创建 `.env.local` 文件配置环境变量：

```env
VITE_API_URL=http://localhost:8000/api
```

## 📋 API服务说明

### authService
- `login()` - 用户登录
- `register()` - 用户注册
- `sendVerificationCode()` - 发送验证码
- `resetPassword()` - 重置密码
- `checkAuth()` - 检查认证状态
- `logout()` - 退出登录

### articleService
- `getArticleList()` - 获取文章列表
- `getArticleDetail()` - 获取文章详情
- `createArticle()` - 创建文章
- `updateArticle()` - 更新文章
- `deleteArticle()` - 删除文章
- `saveToAccount()` - 保存到公众号

### accountService
- `getAccountList()` - 获取公众号列表
- `createAccount()` - 创建公众号
- `updateAccount()` - 更新公众号
- `deleteAccount()` - 删除公众号

## 🎨 UI/UX特性

- **响应式设计**: 支持桌面端和移动端
- **主题定制**: 基于Ant Design主题系统
- **交互反馈**: 完善的loading、消息提示
- **无障碍支持**: 符合Web无障碍标准
- **暗色模式**: 支持明暗主题切换（可扩展）

## 🔒 安全特性

- JWT令牌认证
- 自动令牌刷新
- 路由权限守卫
- XSS防护
- CSRF防护

## 📱 浏览器支持

- Chrome >= 88
- Firefox >= 85
- Safari >= 14
- Edge >= 88

## 🤝 开发规范

### 代码风格
- 使用TypeScript严格模式
- 函数式组件优先
- 统一的命名规范
- ESLint代码检查

### 组件规范
- 单一职责原则
- Props类型定义
- 错误边界处理
- 性能优化

### API调用规范
- 统一使用service层
- 错误处理
- Loading状态管理
- 类型安全

## 📄 许可证

Copyright © 2025 公众号发文助手. All rights reserved.

## 🔗 相关链接

- [后端API文档](../backend/README.md)
- [部署文档](../../docs/deployment.md)
- [Ant Design 文档](https://ant.design/)
- [React 文档](https://reactjs.org/)

## 📞 技术支持

如有问题，请联系开发团队或提交Issue。
