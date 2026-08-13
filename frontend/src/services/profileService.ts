import { api } from './api';
import { User, ApiResponse } from '../types';

export interface UpdateProfileParams {
  nickname?: string;
  username?: string;
  phone?: string;
  email?: string;
}

export interface ChangePasswordParams {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface UploadAvatarResponse {
  avatar_url: string;
  message: string;
}

export const profileService = {
  // 获取用户配置文件
  getUserProfile: (): Promise<ApiResponse<User>> =>
    api.get('/profile'),

  // 更新用户配置文件
  updateProfile: (params: UpdateProfileParams): Promise<ApiResponse<User>> =>
    api.put('/profile', params),

  // 修改密码
  changePassword: (params: ChangePasswordParams): Promise<ApiResponse<any>> =>
    api.put('/profile/password', params),

  // 上传头像
  uploadAvatar: (file: File, userId: number): Promise<ApiResponse<UploadAvatarResponse>> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId.toString());
    
    return api.upload('/upload/avatar', formData);
  },

  // 获取用户统计信息
  getUserStats: (): Promise<ApiResponse<{
    bind_limit: number;
    bound_accounts: number;
    login_count: number;
    articles_count: number;
    total_word_count: number;
  }>> =>
    api.get('/profile/stats'),
}; 