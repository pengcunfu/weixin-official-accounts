import requests
from datetime import datetime
from typing import Dict, Any, Optional, Union
import uuid
import qrcode
import base64
from io import BytesIO

from .base import WeChatBase


class WeChatAuth(WeChatBase):
    """微信扫码授权类"""

    auth_states: Dict[str, Dict[str, Any]]

    def __init__(self,
                 app_id: Optional[str] = None,
                 app_secret: Optional[str] = None) -> None:
        super().__init__(app_id, app_secret)
        # 授权状态存储
        self.auth_states = {}

    def generate_auth_qr_code(self, redirect_uri: Optional[str] = None) -> Dict[str, str]:
        """
        生成授权二维码

        Returns:
            Dict[str, str]: 包含授权码、授权链接和二维码base64数据的字典
        """
        try:
            # 生成唯一的授权码
            auth_code = str(uuid.uuid4())

            # 默认回调地址
            if not redirect_uri:
                redirect_uri = "http://150.158.199.226/accounts/auth_callback"

            # 生成授权链接
            auth_url = (
                f"https://open.weixin.qq.com/connect/oauth2/authorize?"
                f"appid={self.app_id}&"
                f"redirect_uri={redirect_uri}&"
                f"response_type=code&"
                f"scope=snsapi_userinfo&"
                f"state={auth_code}#wechat_redirect"
            )

            # 生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=8,
                border=4,
            )
            qr.add_data(auth_url)
            qr.make(fit=True)

            # 创建二维码图片
            img = qr.make_image(fill_color="black", back_color="white")

            # 转换为base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()

            # 存储授权状态
            self.auth_states[auth_code] = {
                'status': 'waiting',
                'created_time': datetime.now(),
                'auth_url': auth_url
            }

            return {
                'auth_code': auth_code,
                'auth_url': auth_url,
                'qr_code': f"data:image/png;base64,{img_base64}"
            }

        except Exception as e:
            raise Exception(f"生成授权二维码失败: {str(e)}")

    def get_auth_status(self, auth_code: str) -> Dict[str, Union[int, str, None]]:
        """获取授权状态"""
        if not auth_code or auth_code not in self.auth_states:
            return {
                'code': 400,
                'message': '无效的授权码',
                'data': None
            }

        auth_state = self.auth_states[auth_code]
        if auth_state['status'] == 'success':
            # 清理授权状态
            del self.auth_states[auth_code]
            return {
                'code': 200,
                'message': '授权成功',
                'data': None
            }

        return {
            'code': 202,
            'message': '等待授权',
            'data': None
        }

    def validate_account_credentials(self, app_id: str, app_secret: str) -> Dict[str, Any]:
        """
        验证公众号凭证

        Args:
            app_id: 公众号AppID
            app_secret: 公众号AppSecret

        Returns:
            Dict[str, Any]: 验证结果和公众号信息
        """
        try:
            # 获取access_token
            token_url = "https://api.weixin.qq.com/cgi-bin/token"
            token_params = {
                'grant_type': 'client_credential',
                'appid': app_id,
                'secret': app_secret
            }

            token_response = requests.get(token_url, params=token_params)
            token_result = token_response.json()

            if 'access_token' not in token_result:
                return {
                    'success': False,
                    'message': f"验证失败: {token_result.get('errmsg', '获取access_token失败')}"
                }

            access_token = token_result['access_token']

            # 获取公众号基本信息
            info_url = f"https://api.weixin.qq.com/cgi-bin/account/getaccountbasicinfo?access_token={access_token}"
            info_response = requests.get(info_url)
            info_result = info_response.json()

            if 'errcode' in info_result and info_result['errcode'] != 0:
                return {
                    'success': False,
                    'message': f"获取公众号信息失败: {info_result.get('errmsg', '未知错误')}"
                }

            # 构建返回数据
            account_info = {
                'account_appID': app_id,
                'appsecret': app_secret,
                'nickname': info_result.get('nickname', ''),
                'headimg': info_result.get('headimg', ''),
                'service_type': info_result.get('service_type_info', {}).get('id', 0),
                'verify_type': info_result.get('verify_type_info', {}).get('id', 0),
                'username': info_result.get('user_name', ''),
                'principal_name': info_result.get('principal_name', ''),
                'alias': info_result.get('alias', ''),
                'qrcode_url': info_result.get('qrcode_url', '')
            }

            return {
                'success': True,
                'message': '验证成功',
                'data': account_info
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'验证失败: {str(e)}'
            }


wechat_auth: WeChatAuth = WeChatAuth()
