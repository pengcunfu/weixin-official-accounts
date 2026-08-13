import { api } from './api';
import { User, ApiResponse } from '../types';

export interface UserListParams {
  page?: number;
  limit?: number;
  keyword?: string;
  status?: string;
}

export interface UserListResponse {
  data: User[];
  total: number;
  page: number;
  limit: number;
}

export interface CreateUserParams {
  nickname: string;
  username: string;
  email: string;
  phone?: string;
  password: string;
  is_main: boolean;
  bind_limit: number;
  status: 'active' | 'expired' | 'suspended';
  expire_time?: string;
}

export interface UpdateUserParams {
  nickname?: string;
  username?: string;
  email?: string;
  phone?: string;
  is_main?: boolean;
  bind_limit?: number;
  status?: 'active' | 'expired' | 'suspended';
  expire_time?: string;
}

export const userService = {
  // 获取用户列表
  getUserList: (params: UserListParams = {}): Promise<ApiResponse<UserListResponse>> =>
    api.get('/user/list', { params }),

  // 获取单个用户详情
  getUserDetail: (id: number): Promise<ApiResponse<User>> =>
    api.get(`/user/${id}`),

  // 创建用户
  createUser: (params: CreateUserParams): Promise<ApiResponse<User>> =>
    api.post('/user/create', params),

  // 更新用户
  updateUser: (id: number, params: UpdateUserParams): Promise<ApiResponse<User>> =>
    api.put(`/user/${id}`, params),

  // 删除用户
  deleteUser: (id: number): Promise<ApiResponse<any>> =>
    api.delete(`/user/${id}`),

  // 重置用户密码
  resetUserPassword: (id: number, newPassword: string): Promise<ApiResponse<any>> =>
    api.put(`/user/${id}/reset_password`, { password: newPassword }),

  // 批量删除用户
  batchDeleteUsers: (ids: number[]): Promise<ApiResponse<any>> =>
    api.delete('/user/batch', { data: { ids } }),

  // 获取用户统计信息
  getUserStats: (id: number): Promise<ApiResponse<{
    articles_count: number;
    accounts_count: number;
    login_count: number;
    last_login_time: string;
  }>> =>
    api.get(`/user/${id}/stats`),
}; 