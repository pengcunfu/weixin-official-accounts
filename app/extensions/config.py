import os
import yaml
from typing import Any, Dict

from dotenv import load_dotenv

# 项目根目录（app/extensions/config.py 向上两级）
_BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 敏感配置项 -> 环境变量名映射，值统一从 .env / 环境变量读取
ENV_CONFIG_MAP: Dict[str, str] = {
    'app.secret_key': 'APP_SECRET_KEY',
    'wechat.direct.app_id': 'WECHAT_APP_ID',
    'wechat.direct.app_secret': 'WECHAT_APP_SECRET',
    'wechat.component.component_appid': 'WECHAT_COMPONENT_APP_ID',
    'wechat.component.component_appsecret': 'WECHAT_COMPONENT_APP_SECRET',
    'wechat.component.token': 'WECHAT_COMPONENT_TOKEN',
    'wechat.component.encoding_aes_key': 'WECHAT_COMPONENT_ENCODING_AES_KEY',
    'jwt.secret': 'JWT_SECRET',
    'mail.username': 'MAIL_USERNAME',
    'mail.password': 'MAIL_PASSWORD',
    'admin.username': 'ADMIN_USERNAME',
    'admin.password': 'ADMIN_PASSWORD',
    'admin.email': 'ADMIN_EMAIL',
}


class ConfigManager:
    """配置管理器"""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._load_config()

    def _load_config(self):
        """加载配置文件，敏感配置由 .env / 环境变量覆盖"""
        # 加载项目根目录下的 .env（已存在的环境变量优先，不会被覆盖）
        load_dotenv(os.path.join(_BASE_DIR, '.env'), override=False)

        config_path = 'config.yaml'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            raise FileNotFoundError(f'配置文件 {config_path} 不存在')

        # 用环境变量覆盖敏感配置
        self._apply_env_overrides()

    def _apply_env_overrides(self):
        """用环境变量覆盖敏感配置项"""
        for config_key, env_name in ENV_CONFIG_MAP.items():
            env_value = os.environ.get(env_name)
            if env_value is not None:
                self.set(config_key, env_value)

    def reload_config(self):
        """重新加载配置"""
        self._load_config()

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的键路径"""
        keys = key.split('.')
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            if default is not None:
                return default
            raise KeyError(f'配置项 "{key}" 不存在')

    def set(self, key: str, value: Any):
        """设置配置值，支持点号分隔的键路径"""
        keys = key.split('.')
        config = self._config

        # 遍历到最后一个键的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # 设置最后一个键的值
        config[keys[-1]] = value

    def save_config(self, config_path: str = 'config.yaml'):
        """保存配置到文件"""
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False,
                      allow_unicode=True, indent=2)


# 创建全局配置管理器实例
config_manager = ConfigManager()
