import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { message } from 'antd';
import { ApiResponse } from '../types';

// 导航函数，在应用启动时设置
let navigate: ((path: string) => void) | null = null;

export const setNavigate = (navigateFunction: (path: string) => void) => {
  navigate = navigateFunction;
};

// API基础URL
const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:9009/api';

// 导出BASE_URL供外部使用
export { BASE_URL };

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加认证token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    const { data } = response;

    // 检查自定义的业务状态码
    if (data?.code !== undefined && data.code !== 200) {
      // 业务错误处理
      const errorMessage = data.message || '请求失败';

      // 特殊错误码处理
      if (data?.code == 401) {
        // 未授权，清除token并跳转到登录页
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        if (window.location.pathname !== '/login') {
          if (navigate) {
            navigate('/login');
          } else {
            // 降级方案：如果navigate未设置，使用window.location
            window.location.href = '/login';
          }
        }
        message.error('登录已过期，请重新登录');
        
        // 抛出错误，保持与原始响应格式一致
        return Promise.reject({
          response: {
            status: data.code,
            data: data
          }
        });
      }

      message.error(errorMessage);

      // 抛出错误，但保持与原始响应格式一致
      return Promise.reject({
        response: {
          status: data.code,
          data: data
        }
      });
    }

    return response;
  },
  (error) => {
    // HTTP状态码错误处理（非200）
    if (error.response) {
      const { status } = error.response;

      switch (status) {
        case 401:
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          if (window.location.pathname !== '/login') {
            if (navigate) {
              navigate('/login');
            } else {
              // 降级方案：如果navigate未设置，使用window.location
              window.location.href = '/login';
            }
          }
          message.error('网络请求未授权');
          break;
        case 403:
          message.error('网络请求被禁止');
          break;
        case 404:
          message.error('请求的接口不存在');
          break;
        case 500:
          message.error('服务器内部错误');
          break;
        default:
          message.error('网络请求失败');
      }
    } else if (error.request) {
      message.error('网络连接异常，请检查网络设置');
    } else {
      message.error('请求配置错误');
    }

    return Promise.reject(error);
  }
);

// 通用API方法
export const api = {
  // GET请求
  get: <T = any>(url: string, config?: any): Promise<ApiResponse<T>> =>
    apiClient.get(url, config).then(res => res.data),

  // POST请求
  post: <T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> =>
    apiClient.post(url, data, config).then(res => res.data),

  // PUT请求
  put: <T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> =>
    apiClient.put(url, data, config).then(res => res.data),

  // DELETE请求
  delete: <T = any>(url: string, config?: any): Promise<ApiResponse<T>> =>
    apiClient.delete(url, config).then(res => res.data),

  // 文件上传
  upload: <T = any>(url: string, formData: FormData, onProgress?: (progress: number) => void): Promise<ApiResponse<T>> =>
    apiClient.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    }).then(res => res.data),
};

export default apiClient; 
