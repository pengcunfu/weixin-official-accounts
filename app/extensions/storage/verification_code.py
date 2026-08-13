from datetime import datetime
from typing import Optional, Dict
from app.extensions.config import config_manager
from .kv import KVStore


class VerificationCodeManager(KVStore):
    """验证码管理器，负责验证码的数据库存储"""

    def __init__(self):
        super().__init__()
        self.prefix = config_manager.get(
            'storage.verification_code.prefix', 'verify_code:')
        # 不同类型验证码的过期时间配置
        self.expire_configs = {
            'register': config_manager.get('storage.verification_code.register_expire_seconds', 600),
            'reset_password': config_manager.get('storage.verification_code.reset_password_expire_seconds', 600),
            'login': config_manager.get('storage.verification_code.login_expire_seconds', 300),
            'default': config_manager.get('storage.verification_code.expire_seconds', 300)
        }

    def store_code(self, email: str, code: str, code_type: str = 'login') -> bool:
        """存储验证码"""
        key = self._get_code_key(email, code_type)
        code_data = {
            'code': code,
            'email': email,
            'type': code_type,
            'created_time': datetime.utcnow().isoformat(),
            'attempts': 0
        }

        # 根据验证码类型设置过期时间
        expire_seconds = self.expire_configs.get(
            code_type, self.expire_configs['default'])

        return self.set(key, code_data, expire_seconds)

    def verify_code(self, email: str, code: str, code_type: str = 'login') -> tuple[bool, str]:
        """验证验证码"""
        key = self._get_code_key(email, code_type)
        code_data = self.get(key)

        if not code_data:
            return False, '验证码不存在或已过期'

        # 增加尝试次数
        code_data['attempts'] = code_data.get('attempts', 0) + 1

        # 检查尝试次数限制
        max_attempts = config_manager.get(
            'storage.verification_code.max_attempts', 5)
        if code_data['attempts'] > max_attempts:
            self.delete(key)
            return False, '验证码尝试次数过多，请重新获取'

        # 验证验证码
        if code_data['code'] != code:
            # 更新尝试次数
            remaining_ttl = self.ttl(key)
            if remaining_ttl > 0:
                self.set(key, code_data, remaining_ttl)
            return False, f'验证码错误，还可尝试{max_attempts - code_data["attempts"]}次'

        # 验证成功，删除验证码
        self.delete(key)
        return True, '验证成功'

    def is_code_sent_recently(self, email: str, code_type: str = 'login', interval: int = 60) -> bool:
        """检查是否最近已发送验证码（防止频繁发送）"""
        key = self._get_code_key(email, code_type)
        code_data = self.get(key)

        if not code_data:
            return False

        created_time = datetime.fromisoformat(code_data['created_time'])
        time_diff = (datetime.utcnow() - created_time).total_seconds()

        return time_diff < interval

    def get_code_ttl(self, email: str, code_type: str = 'login') -> int:
        """获取验证码剩余有效时间"""
        key = self._get_code_key(email, code_type)
        return self.ttl(key)

    def get_code_info(self, email: str, code_type: str = 'login') -> Optional[Dict]:
        """获取验证码详细信息（不包含验证码本身）"""
        key = self._get_code_key(email, code_type)
        code_data = self.get(key)

        if not code_data:
            return None

        # 移除敏感信息（验证码）
        info = code_data.copy()
        info.pop('code', None)
        info['ttl'] = self.ttl(key)
        return info

    def delete_code(self, email: str, code_type: str = 'login') -> bool:
        """删除验证码"""
        key = self._get_code_key(email, code_type)
        return self.delete(key)

    def _get_code_key(self, email: str, code_type: str) -> str:
        """获取验证码的存储键"""
        return f"{self.prefix}{code_type}:{email}"


verification_code_manager = VerificationCodeManager()
