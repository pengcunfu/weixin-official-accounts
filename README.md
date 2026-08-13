# 公众号发文助手

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.5+-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

现代化的微信公众号内容管理系统，采用前后端分离架构，支持多账号管理、文章编辑、内容发布等功能。

## 项目简介

公众号发文助手是一个专为微信公众号内容管理设计的现代化 Web 应用。系统采用 React + TypeScript 前端和 Flask + SQLAlchemy 后端的分离式架构，后端提供高性能的 RESTful API 服务，支持用户认证、文章管理、公众号集成等核心功能，并通过 Docker 实现一键部署。

## 功能特性

### 用户认证与管理
- 用户注册、登录、密码重置、退出登录
- 邮箱验证码验证、Token 刷新
- JWT 令牌认证与会话管理
- 个人资料管理和头像上传
- 用户权限与账号状态管理

### 文章管理系统
- Word 文档上传解析（.docx 格式）
- 富文本内容处理与在线编辑
- 文章分类管理
- 批量操作（删除、保存到公众号）
- 文章状态追踪（草稿、已发布、已存稿）
- 图片提取和存储

### 微信公众号管理
- 多公众号账号配置（AppID、AppSecret）
- 扫码授权与授权状态管理
- 微信 API 集成与素材管理
- 文章发布到公众号草稿箱
- 账号信息维护与同步

### 用户管理
- 用户列表查看和编辑
- 账号状态管理
- 绑定限制设置
- 角色权限控制

### 文件管理
- 文件上传处理（图片、文档、封面、头像）
- 图片压缩优化
- 文件类型与大小校验
- 静态资源服务

### 仪表盘统计
- 数据统计概览
- 收益图表与使用情况分析
- 系统状态与健康检查

### 现代化 UI/UX
- 响应式设计，支持移动端
- 基于 Ant Design 的美观界面
- 完善的交互反馈
- 暗色模式支持（可扩展）

## 系统架构

### 项目结构

```
wechat-official-accounts/
├── app/                    # Flask 后端应用
│   ├── api/                # API 路由模块（auth/article/account/upload/user/profile/dashboard）
│   ├── decorator/          # 认证与异常处理装饰器
│   ├── extensions/         # 扩展模块（数据库、KV存储、微信、邮件、配置、文档处理）
│   ├── form/               # 表单验证
│   ├── models/             # 数据模型
│   └── utils/              # 工具函数
├── docker/                 # Docker 编排与镜像
│   ├── docker-compose.yml  # 服务编排
│   ├── backend.Dockerfile  # 后端镜像
│   └── frontend.Dockerfile # 前端镜像
├── frontend/               # React 前端应用
│   ├── src/                # 组件、页面、服务、类型、工具
│   ├── public/             # 静态资源
│   ├── nginx.conf          # Nginx 配置
│   └── package.json        # 前端依赖
├── config.yaml             # 后端配置文件
├── main.py                 # 后端应用入口
├── requirements.txt        # 后端依赖
└── README.md               # 项目说明
```

### 架构特点

- **分层架构**：API 层、业务逻辑层、数据访问层分离
- **模块化设计**：功能模块独立，便于维护和扩展
- **数据库设计**：SQLAlchemy ORM，规范的表结构，支持软删除、索引优化和版本迁移
- **安全机制**：JWT 认证、bcrypt 密码散列、CORS 控制、ORM 防注入

## 技术栈

### 前端技术
- **框架**：React 18 + TypeScript
- **UI 组件**：Ant Design 5.x
- **路由**：React Router v6
- **HTTP 客户端**：Axios
- **日期处理**：Day.js
- **图表**：Recharts
- **构建工具**：Create React App

### 后端技术
- **框架**：Flask 2.x
- **数据库**：SQLAlchemy ORM + Flask-Migrate
- **存储**：SQLite（数据 + KV 存储，替代 Redis）
- **认证**：JWT (PyJWT)
- **文档处理**：python-docx
- **邮件服务**：Flask-Mail
- **配置管理**：PyYAML
- **日志**：Python logging
- **WSGI 服务器**：Gunicorn

### 基础设施
- **容器化**：Docker + Docker Compose
- **Web 服务器**：Nginx
- **数据库**：SQLite（默认）/ MySQL

## 快速开始

### 环境要求

- Node.js >= 16.0.0
- Python >= 3.8
- 现代浏览器

### 使用 Docker Compose 部署（推荐）

```bash
cd docker
docker-compose up -d
```

服务启动后：

- 前端：http://localhost
- 后端 API：http://localhost:9009/api
- 数据持久化：`/root/data/uploads`（上传文件）、`/root/data/sqlite`（SQLite 数据库）

### 本地开发环境

#### 后端启动

```bash
# 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 数据库：默认使用 SQLite（instance/wechat.db），无需额外安装数据库
# 如需切换 MySQL，编辑 config.yaml 中的 database 配置

# 启动服务（默认 http://localhost:9009）
python main.py
```

#### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（默认 http://localhost:3000）
npm start
```

前端 API 地址在 `frontend/src/services/api.ts` 中配置，默认指向 `http://127.0.0.1:9009/api`，也可通过环境变量 `REACT_APP_API_URL` 覆盖。

### 数据库初始化

应用首次启动时会自动创建数据表、初始化迁移并生成默认管理员账号（用户名 `admin`，密码 `123456`，可在 `config.yaml` 中修改）。

如需手动执行迁移：

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 配置说明

### 后端配置（config.yaml）

```yaml
# 应用基础配置
app:
  debug: true
  secret_key: "your-secret-key"
  host: "0.0.0.0"
  port: 9009

# 数据库配置
database:
  type: "sqlite"              # sqlite 或 mysql
  path: "instance/wechat.db"  # SQLite 数据库文件路径

# 文件上传配置
upload:
  max_content_length: 16777216  # 16MB
  allowed_extensions: ["docx"]
  allowed_image_extensions: ["png", "jpg", "jpeg", "gif"]

# 存储配置（基于SQLite的KV存储，替代Redis）
storage:
  token:
    prefix: "auth_token:"
    expire_seconds: 86400
  verification_code:
    prefix: "verify_code:"
    expire_seconds: 300
    max_attempts: 5
  cache:
    prefix: "cache:"
    default_expire_seconds: 3600

# 邮件配置
mail:
  server: "smtp.qq.com"
  port: 587
  username: "your-email@example.com"
  password: "your-password"

# 微信配置
wechat:
  direct:
    app_id: "wx1234567890"
    app_secret: "your_app_secret"

# JWT 配置
jwt:
  secret: "your_secret_key"
  algorithm: "HS256"
  expire_hours: 24

# 默认管理员
admin:
  username: "admin"
  password: "123456"
  email: "admin@example.com"
```

敏感配置（微信 AppID/AppSecret、JWT Secret、SMTP 密码、默认管理员密码等）不写入 config.yaml，统一存放在项目根目录的 `.env` 文件中，该文件已被 `.gitignore` 忽略，不会提交到仓库。克隆或部署项目后，请先复制 `.env.example` 为 `.env` 并填写真实值：

```bash
cp .env.example .env
```

### 前端配置

在 `frontend/src/services/api.ts` 中配置 API 地址：

```typescript
const BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:9009/api'
```

## API 接口文档

### 认证接口（/api/auth）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /login | 用户登录（支持邮箱或用户名） |
| POST | /register | 用户注册（邮箱 + 验证码） |
| POST | /send_verification_code | 发送邮箱验证码 |
| POST | /reset_password | 重置密码 |
| POST | /refresh_token | 刷新 Token |
| POST | /logout | 退出登录 |
| GET | /check | 检查登录状态 |

登录示例：

```json
{
  "username": "admin",
  "password": "123456",
  "remember": false
}
```

### 文章接口（/api/article）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /list | 获取文章列表（支持分页和标题搜索） |
| GET | /&lt;id&gt; | 获取文章详情 |
| POST | /create | 创建文章 |
| PUT | /&lt;id&gt; | 更新文章 |
| DELETE | /&lt;ids&gt; | 批量删除文章 |
| GET | /&lt;id&gt;/content | 获取文章内容 |
| PUT | /&lt;id&gt;/content | 更新文章内容 |
| POST | /&lt;id&gt;/save_to_account | 保存文章到公众号 |
| GET | /accounts | 获取可选公众号列表 |

### 公众号接口（/api/account）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /list | 获取公众号列表 |
| POST | /create | 创建公众号配置 |
| GET | /&lt;id&gt; | 获取公众号详情 |
| PUT | /&lt;id&gt; | 更新公众号 |
| DELETE | /&lt;ids&gt; | 批量删除公众号 |
| POST | /&lt;ids&gt;/sync | 同步公众号数据 |
| GET | /auth/qr_code | 生成扫码授权二维码 |
| GET | /auth/status | 查询授权状态 |
| POST | /validate | 校验公众号配置 |
| POST | /info | 获取公众号信息 |
| POST | /draft/test | 测试草稿发布 |
| GET | /access_token | 获取 access_token |

创建公众号示例：

```json
{
  "account_appID": "wx1234567890",
  "appsecret": "app_secret_key",
  "notes": "备注信息"
}
```

### 上传接口（/api/upload）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /image | 上传图片 |
| POST | /document | 上传 Word 文档 |
| POST | /avatar | 上传头像 |
| POST | /cover | 上传封面 |
| POST | /delete | 删除文件 |

上传使用 `multipart/form-data`，字段名为 `file`。

### 用户管理接口（/api/user）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /list | 获取用户列表 |
| GET | /&lt;id&gt; | 获取用户详情 |
| PUT | /&lt;id&gt; | 编辑用户 |
| DELETE | /&lt;ids&gt; | 批量删除用户 |
| PUT | /&lt;id&gt;/status | 修改账号状态 |

### 个人资料接口（/api/profile）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 获取当前用户资料 |
| PUT | / | 更新个人资料 |
| PUT | /password | 修改密码 |
| GET | /sessions | 获取登录会话列表 |
| DELETE | /sessions/&lt;token&gt; | 注销指定会话 |
| DELETE | /sessions | 注销全部会话 |

### 仪表盘接口（/api/dashboard）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /stats | 获取主要统计数据 |
| GET | /revenue-chart | 获取总收益图表数据 |
| GET | /daily-revenue-chart | 获取日收益趋势 |
| GET | /activities | 获取最近活动 |
| GET | /system-status | 获取系统状态 |
| GET | /system-info | 获取详细系统信息 |
| GET | /system-health | 系统健康检查 |
| GET | /detailed-stats | 获取详细统计数据 |

除认证接口外，其余接口均需在请求头携带 Token：

```text
Authorization: Bearer <token>
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权访问 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |

## 安全特性

- **JWT 认证**：无状态令牌认证机制，支持过期处理和 Token 刷新
- **密码加密**：bcrypt 密码散列存储
- **CORS 配置**：跨域请求安全控制
- **文件验证**：上传文件类型和大小限制
- **XSS 防护**：前端输入过滤和转义
- **SQL 注入防护**：ORM 参数化查询
- **CSRF 保护**：敏感操作防护

## 性能优化

### 数据库优化
- 索引优化
- 查询优化
- 连接池配置（MySQL）
- 慢查询监控

### 缓存策略
- 数据库 KV 缓存热点数据
- 查询结果缓存
- 会话缓存
- 验证码缓存

### 文件处理
- 异步文件处理
- 图片压缩
- 文件类型验证
- 存储路径优化

## 日志管理

日志采用分级记录，支持文件轮转，配置见 `config.yaml` 的 `logging` 部分：

```yaml
logging:
  level: "INFO"
  file:
    enabled: false
    filename: "logs/app.log"
    max_bytes: 10485760
    backup_count: 5
```

## 开发工具

- **格式化**：Black、isort
- **静态检查**：Flake8、mypy
- **测试**：pytest、pytest-cov

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 代码格式化
black app/
isort app/

# 静态检查
flake8 app/
mypy app/
```

## 部署指南

### Docker 部署

```bash
cd docker

# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 生产模式启动后端

```bash
gunicorn -w 4 -b 0.0.0.0:9009 main:app
```

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:9009;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态资源
    location /static/ {
        alias /path/to/backend/static/;
        expires 30d;
    }
}
```

## 测试

### 后端测试

```bash
python -m pytest tests/
python -m pytest --cov=app tests/
```

### 前端测试

```bash
cd frontend
npm test
```

## 相关文档

- [前端文档](frontend/README.md)
- [Flask 文档](https://flask.palletsprojects.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)

## 贡献指南

1. Fork 项目
2. 创建功能分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 开启 Pull Request

## 许可证

Copyright © 2025 公众号发文助手. All rights reserved.

## 联系方式

- 项目主页：[GitHub Repository](https://github.com/your-username/wechat-official-accounts)
- 邮箱：your-email@example.com
- 技术支持：如有问题，请提交 Issue

## 致谢

感谢所有贡献者和使用者的支持！

如果这个项目对你有帮助，请给它一个 Star！

## 更新日志

### v2.0.0 (2025-01-21)

- 全新架构：前后端分离设计
- React + TypeScript 前端
- Flask + SQLAlchemy 后端重构
- 全新的现代化 UI 界面
- 完整的响应式设计
- 增强的安全机制
- Docker 容器化部署
- 完善的 API 文档

### v1.0.0

- 初始版本发布
- 基础文章管理功能
- 用户认证系统
- 微信公众号集成
