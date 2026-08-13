import { api } from './api';
import { Article, ApiResponse, PaginationParams } from '../types';

export interface CreateArticleParams {
  title: string;
  category: string;
  file_type: string;
  file_path?: string;
  status?: string;
  saved_status?: string;
  author_nickname?: string;
  uploader_phone?: string;
  content?: string;
  content_html?: string;
}

export interface UpdateArticleParams {
  title?: string;
  category?: string;
  author_nickname?: string;
  content?: string;
  content_html?: string;
  status?: string;
  saved_status?: string;
}

export interface ArticleListResponse {
  data: Article[];
  total: number;
  page: number;
  limit: number;
}

// SaveToAccountParams 接口已移除，因为后端不再需要 account_id 参数

export const articleService = {
  // 获取文章列表
  getArticleList: (params: PaginationParams): Promise<ApiResponse<ArticleListResponse>> =>
    api.get('/article/list', { params }),

  // 获取单个文章详情
  getArticleDetail: (id: number): Promise<ApiResponse<Article>> =>
    api.get(`/article/${id}`),

  // 创建文章
  createArticle: (params: CreateArticleParams): Promise<ApiResponse<Article>> =>
    api.post('/article/create', params),

  // 更新文章
  updateArticle: (id: number, params: UpdateArticleParams): Promise<ApiResponse<Article>> =>
    api.put(`/article/${id}`, params),

  // 删除文章（单个）
  deleteArticle: (id: number): Promise<ApiResponse<any>> =>
    api.delete(`/article/${id}`),

  // 批量删除文章
  batchDeleteArticles: (ids: string): Promise<ApiResponse<any>> =>
    api.delete(`/article/${ids}`),

  // 保存文章到微信公众号（单个）
  saveToAccount: (id: number): Promise<ApiResponse<any>> =>
    api.post(`/article/${id}/save_to_account`),

  // 批量保存文章到微信公众号（已移除，请使用 saveToAccount 单独保存每篇文章）

  // 发布文章
  publishArticle: (id: number): Promise<ApiResponse<Article>> =>
    api.put(`/article/${id}`, { status: '已发布' }),

  // 获取文章预览
  getArticlePreview: (id: number): Promise<ApiResponse<any>> =>
    api.get(`/article/${id}/preview`),
}; 