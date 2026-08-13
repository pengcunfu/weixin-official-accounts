import { api } from './api';
import { ApiResponse } from '../types';

export interface UploadDocumentResponse {
  path: string;
  original_name: string;
  file_type: string;
  size: number;
  article?: {
    id: number;
    title: string;
    status: string;
  };
}

export interface UploadImageResponse {
  url: string;
  path: string;
  filename: string;
  size: number;
}

export const uploadService = {
  // 上传文档文件
  uploadDocument: (file: File, publicAccountId: number): Promise<ApiResponse<UploadDocumentResponse>> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('public_account_id', publicAccountId.toString());
    
    return api.post('/upload/document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // 上传图片文件
  uploadImage: (file: File): Promise<ApiResponse<UploadImageResponse>> => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // 批量上传图片
  uploadImages: (files: File[]): Promise<ApiResponse<UploadImageResponse[]>> => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    return api.post('/upload/images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // 删除上传的文件
  deleteUploadedFile: (path: string): Promise<ApiResponse<any>> =>
    api.delete('/upload/file', { data: { path } }),
}; 