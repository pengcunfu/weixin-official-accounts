from typing import Optional, Any
from app.extensions.config import config_manager
from .kv import KVStore


class CacheManager(KVStore):
    """缓存管理器，提供通用缓存功能"""

    def __init__(self):
        super().__init__()
        self.prefix = config_manager.get('storage.cache.prefix', 'cache:')
        self.default_expire_seconds = config_manager.get(
            'storage.cache.default_expire_seconds', 3600)

    def set_cache(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        """设置缓存"""
        cache_key = f"{self.prefix}{key}"
        expire_time = expire_seconds or self.default_expire_seconds
        return self.set(cache_key, value, expire_time)

    def get_cache(self, key: str) -> Optional[Any]:
        """获取缓存"""
        cache_key = f"{self.prefix}{key}"
        return self.get(cache_key)

    def delete_cache(self, key: str) -> bool:
        """删除缓存"""
        cache_key = f"{self.prefix}{key}"
        return self.delete(cache_key)

    def cache_exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        cache_key = f"{self.prefix}{key}"
        return self.exists(cache_key)


cache_manager = CacheManager()
