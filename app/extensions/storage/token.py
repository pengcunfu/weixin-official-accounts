from datetime import datetime
from typing import Optional, Dict
from app.extensions.config import config_manager
from .kv import KVStore


class TokenManager(KVStore):
    """Token管理器，负责登录Token的数据库存储"""

    def __init__(self):
        super().__init__()
        self.prefix = config_manager.get('storage.token.prefix', 'auth_token:')
        self.expire_seconds = config_manager.get(
            'storage.token.expire_seconds', 86400)

    def store_token(self, user_id: int, token: str, device_info: Optional[Dict] = None) -> bool:
        """存储用户Token"""
        key = self._get_token_key(user_id, token)
        token_data = {
            'user_id': user_id,
            'token': token,
            'created_time': datetime.utcnow().isoformat(),
            'device_info': device_info or {},
            'last_activity': datetime.utcnow().isoformat()
        }

        # 存储Token数据
        success = self.set(key, token_data, self.expire_seconds)

        # 同时在用户的Token列表中添加这个Token
        if success:
            self._add_user_token(user_id, token)

        return success

    def get_token_data(self, user_id: int, token: str) -> Optional[Dict]:
        """获取Token数据"""
        key = self._get_token_key(user_id, token)
        return self.get(key)

    def verify_token(self, user_id: int, token: str) -> bool:
        """验证Token是否有效"""
        token_data = self.get_token_data(user_id, token)
        return token_data is not None

    def refresh_token(self, user_id: int, token: str) -> bool:
        """刷新Token的过期时间和最后活动时间"""
        key = self._get_token_key(user_id, token)
        token_data = self.get(key)

        if token_data:
            token_data['last_activity'] = datetime.utcnow().isoformat()
            return self.set(key, token_data, self.expire_seconds)

        return False

    def revoke_token(self, user_id: int, token: str) -> bool:
        """撤销单个Token"""
        key = self._get_token_key(user_id, token)
        success = self.delete(key)

        if success:
            self._remove_user_token(user_id, token)

        return success

    def revoke_user_tokens(self, user_id: int, except_token: Optional[str] = None) -> int:
        """撤销用户的所有Token（可排除指定Token）"""
        user_tokens = self.get_user_tokens(user_id)
        revoked_count = 0

        for token in user_tokens:
            if except_token and token == except_token:
                continue

            if self.revoke_token(user_id, token):
                revoked_count += 1

        return revoked_count

    def get_user_tokens(self, user_id: int) -> list:
        """获取用户的所有有效Token"""
        user_tokens_key = self._get_user_tokens_key(user_id)
        tokens = self.get(user_tokens_key) or []

        # 验证每个Token是否还有效，移除无效的
        valid_tokens = []
        for token in tokens:
            if self.verify_token(user_id, token):
                valid_tokens.append(token)

        # 更新用户Token列表
        if len(valid_tokens) != len(tokens):
            self.set(user_tokens_key, valid_tokens, self.expire_seconds)

        return valid_tokens

    def get_user_active_sessions(self, user_id: int) -> list:
        """获取用户的活跃会话信息"""
        tokens = self.get_user_tokens(user_id)
        sessions = []

        for token in tokens:
            token_data = self.get_token_data(user_id, token)
            if token_data:
                sessions.append({
                    'token': token,
                    'created_time': token_data.get('created_time'),
                    'last_activity': token_data.get('last_activity'),
                    'device_info': token_data.get('device_info', {})
                })

        return sessions

    def _get_token_key(self, user_id: int, token: str) -> str:
        """获取Token的存储键"""
        return f"{self.prefix}user_{user_id}:token_{token}"

    def _get_user_tokens_key(self, user_id: int) -> str:
        """获取用户Token列表的存储键"""
        return f"{self.prefix}user_{user_id}:tokens"

    def _add_user_token(self, user_id: int, token: str) -> bool:
        """将Token添加到用户Token列表"""
        user_tokens_key = self._get_user_tokens_key(user_id)
        tokens = self.get(user_tokens_key) or []

        if token not in tokens:
            tokens.append(token)
            return self.set(user_tokens_key, tokens, self.expire_seconds)

        return True

    def _remove_user_token(self, user_id: int, token: str) -> bool:
        """从用户Token列表中移除Token"""
        user_tokens_key = self._get_user_tokens_key(user_id)
        tokens = self.get(user_tokens_key) or []

        if token in tokens:
            tokens.remove(token)
            if tokens:
                return self.set(user_tokens_key, tokens, self.expire_seconds)
            # 列表为空时直接删除，避免残留空记录
            return self.delete(user_tokens_key)

        return True


token_manager = TokenManager()
