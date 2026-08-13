import { api } from './api';
import { User, LoginResponse, ApiResponse } from '../types';

export interface LoginParams {
  username: string;
  password: string;
  remember?: boolean;
}

export interface RegisterParams {
  email: string;
  password: string;
  verification_code: string;
}

export interface ResetPasswordParams {
  email: string;
  verification_code: string;
  new_password: string;
}

export const authService = {
  // 登录
  login: (params: LoginParams): Promise<LoginResponse> =>
    api.post('/auth/login', params),

  // 注册
  register: (params: RegisterParams): Promise<ApiResponse<any>> =>
    api.post('/auth/register', params),

  // 发送验证码
  sendVerificationCode: (email: string, type: string = 'register'): Promise<ApiResponse<any>> =>
    api.post('/auth/send_verification_code', { email, type }),

  // 重置密码
  resetPassword: (params: ResetPasswordParams): Promise<ApiResponse<any>> =>
    api.post('/auth/reset_password', params),

  // 检查认证状态
  checkAuth: (): Promise<ApiResponse<User>> =>
    api.get('/auth/check'),

  // 退出登录
  logout: (): Promise<ApiResponse<any>> =>
    api.post('/auth/logout', {}),
}; 