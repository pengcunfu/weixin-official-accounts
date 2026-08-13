// 用户相关类型
export interface User {
  id: number;
  nickname: string;
  username?: string;
  phone?: string;
  email?: string;
  is_main: boolean;
  bind_limit: number;
  bound_accounts: number;
  register_time: string;
  expire_time: string;
  avatar?: string;
  status: 'active' | 'expired' | 'suspended';
  login_count: number;
}

// 图片信息类型
export interface ImageInfo {
  filename: string;
  url: string;
}

// 文章相关类型
export interface Article {
  id: number;
  title: string;
  content: string;
  html_content?: string;
  content_html?: string; // 兼容字段
  category?: string;
  author?: string;
  author_nickname?: string;
  cover_url?: string;
  cover_path?: string;
  status: '草稿' | '已发布' | '已删除';
  word_count: number;
  file_path?: string;
  file_type?: string; // 文件类型
  created_time: string;
  updated_time: string;
  published_time?: string;
  images_info?: string; // 图片信息JSON字符串
  public_account_nickname?: string; // 公众号昵称
  public_account_id?: number; // 关联的公众号ID
  saved_status?: '已存稿' | '未存稿' | '存稿中'; // 保存状态
}

// 公众号相关类型
export interface PublicAccount {
  id: number;
  name: string;
  nickname?: string; // 公众号昵称，用于显示
  app_id: string;
  account_appID?: string; // 兼容字段
  app_secret: string;
  access_token?: string;
  token_expires_at?: string;
  status: 'active' | 'inactive' | 'error';
  authorized?: boolean; // 是否已授权
  last_sync_time?: string;
  created_time: string;
  updated_time: string;
  deleted_time?: string; // 删除时间，用于软删除
}

// API响应基础类型
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data?: T;
  count?: number;
}

// 登录响应类型
export interface LoginResponse {
  code: number;
  message: string;
  data?: {
    token: string;
    user: User;
  };
}

// 分页参数类型
export interface PaginationParams {
  page: number;
  limit: number;
  title?: string;
}

// 上传文件结果类型
export interface UploadResult {
  filename: string;
  title?: string;
  author?: string;
  word_count?: number;
  images_count?: number;
  status: 'success' | 'warning' | 'error';
  message?: string;
}

// 菜单项类型
export interface MenuItem {
  key: string;
  icon?: React.ReactNode;
  label: string;
  path?: string;
  children?: MenuItem[];
}

// 路由守卫相关
export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  isLoading: boolean;
} 