import { api } from './api';
import { ApiResponse } from '../types';

export interface DashboardStats {
  username: string;
  isMainAccount: boolean;
  authorizedAccounts: number;
  totalAccounts: number;
  loginCount: number;
  childAccountCount: number;
  accountRevenue: number;
  dailyAccountRevenue: number;
}

export interface ChartData {
  name: string;
  value: number;
  revenue?: number;
}

export interface ActivityItem {
  id: string;
  type: 'article' | 'account' | 'user' | 'revenue';
  title: string;
  time: string;
  status: 'success' | 'warning' | 'info';
}

export interface SystemStatus {
  server_status: {
    percent: number;
    status: string;
    color: string;
  };
  memory_usage: {
    percent: number;
    status: string;
  };
  cpu_usage: {
    percent: number;
    status: string;
  };
  disk_space: {
    percent: number;
    status: string;
  };
  overall_status: {
    message: string;
    type: string;
  };
}

export interface TrendInfo {
  type: 'increase' | 'decrease' | 'stable';
  percent?: number;
  text: string;
}

export interface DetailedStats {
  weekly_articles: {
    value: number;
    suffix: string;
    trend: TrendInfo;
  };
  monthly_views: {
    value: number;
    suffix: string;
    trend: TrendInfo;
  };
  active_accounts: {
    value: number;
    suffix: string;
    total: number;
    text: string;
  };
  daily_revenue: {
    value: number;
    suffix: string;
    precision: number;
    trend: TrendInfo;
  };
}

// 简单的带 TTL 的内存缓存，避免短时间内重复请求首页数据
const CACHE_TTL_MS = 30_000;
const cache = new Map<string, { data: unknown; expiresAt: number }>();

async function cachedGet<T>(key: string, fetcher: () => Promise<ApiResponse<T>>): Promise<ApiResponse<T>> {
  const now = Date.now();
  const hit = cache.get(key);
  if (hit && hit.expiresAt > now) {
    return hit.data as ApiResponse<T>;
  }
  const response = await fetcher();
  cache.set(key, { data: response, expiresAt: now + CACHE_TTL_MS });
  return response;
}

/** 清空首页数据缓存（如登出/数据变更时使用） */
export function clearDashboardCache(): void {
  cache.clear();
}

export const dashboardService = {
  // 获取Dashboard主要统计数据
  getDashboardStats: (): Promise<ApiResponse<DashboardStats>> =>
    cachedGet('/dashboard/stats', () => api.get('/dashboard/stats')),

  // 获取总收益图表数据
  getRevenueChart: (): Promise<ApiResponse<ChartData[]>> =>
    cachedGet('/dashboard/revenue-chart', () => api.get('/dashboard/revenue-chart')),

  // 获取日收益趋势图表数据
  getDailyRevenueChart: (): Promise<ApiResponse<ChartData[]>> =>
    cachedGet('/dashboard/daily-revenue-chart', () => api.get('/dashboard/daily-revenue-chart')),

  // 获取最近活动数据
  getRecentActivities: (): Promise<ApiResponse<ActivityItem[]>> =>
    cachedGet('/dashboard/activities', () => api.get('/dashboard/activities')),

  // 获取系统状态数据
  getSystemStatus: (): Promise<ApiResponse<SystemStatus>> =>
    cachedGet('/dashboard/system-status', () => api.get('/dashboard/system-status')),

  // 获取详细统计数据
  getDetailedStats: (): Promise<ApiResponse<DetailedStats>> =>
    cachedGet('/dashboard/detailed-stats', () => api.get('/dashboard/detailed-stats')),
};
