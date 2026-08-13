import { User } from '../types';
import { BASE_URL } from '../services/api';

/**
 * 获取用户显示名称
 * 优先显示有效的nickname，否则显示username，最后显示默认名称
 */
export const getUserDisplayName = (user: User | null): string => {
  if (!user) return '系统管理员';
  
  // 检查nickname是否有效（不是null、不包含乱码等）
  const hasValidNickname = user.nickname && 
    user.nickname !== 'null' && 
    !user.nickname.includes('\\u') &&
    user.nickname.trim() !== '';
  
  if (hasValidNickname) {
    return user.nickname;
  }
  
  // 检查username是否有效
  if (user.username && user.username.trim() !== '') {
    return user.username;
  }
  
  // 如果都没有，根据用户类型返回默认名称
  return user.is_main ? '系统管理员' : '用户';
};

/**
 * 获取用户头像URL
 * 如果用户没有头像，返回默认头像路径
 */
export const getUserAvatarUrl = (user: User | null): string => {
  if (!user?.avatar || user.avatar.trim() === '') {
    return '/images/default-avatar.png';
  }
  
  return user.avatar;
};

/**
 * 获取用户名首字母作为头像占位符
 */
export const getUserInitial = (user: User | null): string => {
  const displayName = getUserDisplayName(user);
  return displayName.charAt(0).toUpperCase();
};

/**
 * 检查用户是否有有效头像
 */
export const hasValidAvatar = (user: User | null): boolean => {
  return !!(user?.avatar && user.avatar.trim() !== '');
};

/**
 * 处理头像URL，将相对路径转换为完整URL
 */
export const processAvatarUrl = (avatarUrl: string | null | undefined): string => {
  if (!avatarUrl || avatarUrl.trim() === '') {
    return '/images/default-avatar.png';
  }
  
  // 如果是相对路径（以/uploads/开头），则添加完整前缀
  if (avatarUrl.startsWith('/uploads/')) {
    const baseUrl = BASE_URL.replace('/api', '');
    return baseUrl + avatarUrl;
  }
  
  // 如果已经是完整URL，直接返回
  return avatarUrl;
};

/**
 * 处理用户数据，将头像相对路径转换为完整URL
 */
export const processUserData = (userData: User): User => {
  if (!userData) return userData;
  
  return {
    ...userData,
    avatar: userData.avatar ? processAvatarUrl(userData.avatar) : userData.avatar
  };
}; 