import requests
from typing import Dict, Any, Optional
import logging
import time
import json
from app.extensions.config import config_manager


class WeChatBase:
    """微信API基础类，提供通用功能"""

    app_id: Optional[str]
    app_secret: Optional[str]
    base_url: str
    open_url: str
    access_token: Optional[str]
    token_expires: int

    def __init__(self, app_id: Optional[str] = None,
                 app_secret: Optional[str] = None) -> None:
        """
        初始化微信API基础配置

        Args:
            app_id: 微信公众号AppID
            app_secret: 微信公众号AppSecret
        """
        self.app_id = app_id or config_manager.get('wechat.direct.app_id')
        self.app_secret = app_secret or config_manager.get(
            'wechat.direct.app_secret')
        self.base_url = "https://api.weixin.qq.com"
        self.open_url = "https://open.weixin.qq.com"

        # Token管理
        self.access_token = None
        self.token_expires = 0

        if not self.app_id or not self.app_secret:
            logging.warning("微信公众号的APP_ID和APP_SECRET未设置")

    def get_access_token(self) -> str:
        """
        获取access_token（带缓存）

        Returns:
            str: access_token

        Raises:
            Exception: 获取失败时抛出异常
        """
        now = int(time.time())
        if self.access_token and now < self.token_expires:
            return self.access_token

        url = f"{self.base_url}/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.app_id,
            'secret': self.app_secret
        }

        result = self._make_request('GET', url, params=params)

        if 'access_token' in result:
            self.access_token = result['access_token']
            self.token_expires = now + \
                                 result.get('expires_in', 7200) - 300  # 提前5分钟过期
            print(f"成功获取access_token: {self.app_id}")
            return self.access_token
        else:
            raise Exception(
                f"获取access_token失败: {result.get('errmsg', '未知错误')}")

    def _make_request(self, method: str, url: str,
                      params: Optional[Dict[str, Any]] = None,
                      data: Optional[Dict[str, Any]] = None,
                      files: Optional[Dict[str, Any]] = None,
                      **kwargs: Any) -> Dict[str, Any]:
        """
        统一的API请求处理

        Args:
            method: 请求方法 GET/POST
            url: 请求URL
            params: URL参数
            data: 请求数据
            files: 文件数据
            **kwargs: 其他请求参数

        Returns:
            Dict[str, Any]: 响应结果

        Raises:
            Exception: 请求失败时抛出异常
        """
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, **kwargs)
            elif method.upper() == 'POST':
                if files:
                    response = requests.post(
                        url, params=params, files=files, **kwargs)
                elif data:
                    headers = kwargs.get('headers', {})
                    if 'Content-Type' not in headers:
                        headers['Content-Type'] = 'application/json'
                        kwargs['headers'] = headers
                    response = requests.post(url, params=params,
                                             data=json.dumps(data, ensure_ascii=False), **kwargs)
                else:
                    response = requests.post(url, params=params, **kwargs)
            else:
                raise Exception(f"不支持的请求方法: {method}")

            if not response.ok:
                raise Exception(
                    f"HTTP请求失败: {response.status_code} {response.text}")

            result = response.json()
            return self._handle_api_response(result)

        except requests.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"响应解析失败: {str(e)}")

    def _handle_api_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        统一的API响应处理

        Args:
            result: API响应结果

        Returns:
            Dict[str, Any]: 处理后的结果

        Raises:
            Exception: API返回错误时抛出异常
        """
        if 'errcode' in result and result['errcode'] != 0:
            error_msg = result.get('errmsg', '未知错误')
            error_code = result.get('errcode')

            # 特殊错误码处理
            if error_code == 40013:
                raise Exception("无效的AppID，请检查权限")
            elif error_code == 40001:
                raise Exception("无效的access_token，请重新获取")
            elif error_code == 40014:
                raise Exception("无效的access_token类型")
            else:
                raise Exception(f"API错误 [{error_code}]: {error_msg}")

        return result

    def _make_authenticated_request(self,
                                    method: str,
                                    endpoint: str,
                                    use_token_param: bool = True,
                                    **kwargs: Any) -> Dict[str, Any]:
        """
        需要access_token的请求

        Args:
            method: 请求方法
            endpoint: API端点（相对于base_url）
            use_token_param: 是否将token作为URL参数
            **kwargs: 其他请求参数

        Returns:
            Dict[str, Any]: 响应结果
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}{endpoint}"

        if use_token_param:
            params = kwargs.get('params', {})
            params['access_token'] = access_token
            kwargs['params'] = params

        return self._make_request(method, url, **kwargs)

# ========== 全局实例 ==========
