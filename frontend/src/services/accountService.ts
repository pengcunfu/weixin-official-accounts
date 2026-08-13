import { api } from './api';
import { PublicAccount, ApiResponse } from '../types';

export interface CreateAccountParams {
  account_appID: string;
  appsecret: string;
  notes?: string;
}

export interface UpdateAccountParams {
  account_appID: string;
  appsecret: string;
  notes?: string;
  authorized?: boolean;
}

export interface AccountListParams {
  page?: number;
  limit?: number;
}

export interface AccountListResponse {
  data: PublicAccount[];
  total: number;
  page: number;
  limit: number;
}

export const accountService = {
  // 获取账号列表
  getAccountList: (params: AccountListParams = { page: 1, limit: 100 }): Promise<ApiResponse<AccountListResponse>> =>
    api.get('/account/list', { params }),

  // 创建账号
  createAccount: (params: CreateAccountParams): Promise<ApiResponse<PublicAccount>> =>
    api.post('/account/create', params),

  // 更新账号
  updateAccount: (id: number, params: UpdateAccountParams): Promise<ApiResponse<PublicAccount>> =>
    api.put(`/account/${id}`, params),

  // 删除账号
  deleteAccount: (id: number): Promise<ApiResponse<any>> =>
    api.delete(`/account/${id}`),

  // 获取单个账号详情
  getAccountDetail: (id: number): Promise<ApiResponse<PublicAccount>> =>
    api.get(`/account/${id}`),

  // 检查账号授权状态
  checkAccountAuth: (id: number): Promise<ApiResponse<{ authorized: boolean; message?: string }>> =>
    api.get(`/account/${id}/auth/check`),

  // 刷新账号授权
  refreshAccountAuth: (id: number): Promise<ApiResponse<any>> =>
    api.post(`/account/${id}/auth/refresh`),
}; 