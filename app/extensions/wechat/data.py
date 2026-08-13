from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from app.models.public_account import PublicAccount
from .base import WeChatBase


class WeChatData(WeChatBase):
    """微信公众号数据获取类"""

    def get_account_basic_info(self, access_token: Optional[str] = None) -> Dict[str, Any]:
        """获取公众号基本信息"""
        result = self._make_authenticated_request(
            'GET', '/cgi-bin/account/getaccountbasicinfo')
        print("成功获取公众号基本信息")
        return result

    def get_user_count(self, access_token: Optional[str] = None) -> Dict[str, int]:
        """获取用户基本信息（关注人数等）"""
        params = {'next_openid': ''}
        result = self._make_authenticated_request(
            'GET', '/cgi-bin/user/get', params=params)

        total = result.get('total', 0)
        count = result.get('count', 0)

        return {
            'total_users': total,
            'current_users': count
        }

    def get_draft_count(self, access_token: Optional[str] = None) -> int:
        """获取草稿箱文章数量"""
        try:
            data = {
                "offset": 0,
                "count": 1,  # 只获取1条来看总数
                "no_content": 1  # 不返回content字段
            }

            result = self._make_authenticated_request(
                'POST', '/cgi-bin/draft.py/batchget', data=data)

            # 返回总数
            total_count = result.get('total_count', 0)
            print(f"草稿箱文章数量: {total_count}")
            return total_count

        except Exception as e:
            print(f"获取草稿箱数量失败: {e}")
            # 如果获取失败，返回0而不是抛出异常
            return 0

    def _get_user_summary(self,
                          access_token: Optional[str] = None,
                          begin_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> Dict[str, Any]:
        """获取用户增减数据"""
        try:
            if not begin_date:
                # 默认获取最近7天的数据
                end_date = datetime.now().strftime('%Y-%m-%d')
                begin_date = (datetime.now() - timedelta(days=6)
                              ).strftime('%Y-%m-%d')

            data = {
                "begin_date": begin_date,
                "end_date": end_date
            }

            result = self._make_authenticated_request(
                'POST', '/datacube/getusersummary', data=data)
            print("成功获取用户增减数据")
            return result

        except Exception as e:
            print(f"获取用户增减数据失败: {e}")
            raise e

    def _get_article_summary(self,
                             access_token: Optional[str] = None,
                             begin_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> Dict[str, Any]:
        """获取图文群发每日数据"""
        try:
            if not begin_date:
                # 默认获取最近7天的数据
                end_date = datetime.now().strftime('%Y-%m-%d')
                begin_date = (datetime.now() - timedelta(days=6)
                              ).strftime('%Y-%m-%d')

            data = {
                "begin_date": begin_date,
                "end_date": end_date
            }

            result = self._make_authenticated_request(
                'POST', '/datacube/getarticlesummary', data=data)
            print("成功获取图文群发数据")
            return result

        except Exception as e:
            print(f"获取图文群发数据失败: {e}")
            raise e

    def get_comprehensive_info(self, access_token: Optional[str] = None) -> Dict[str, Any]:
        """获取公众号综合信息"""
        result = {
            'basic_info': {},
            'user_count': {'total_users': 0, 'current_users': 0},
            'draft_count': 0,
            'user_summary': [],
            'article_summary': [],
            'revenue': {
                'total_revenue': 0,
                'yesterday_revenue': 0
            }
        }

        # 获取基本信息
        basic_info = self.get_account_basic_info()
        result['basic_info'] = basic_info

        # 获取用户数量
        user_count = self.get_user_count()
        result['user_count'] = user_count

        # 获取草稿箱数量
        draft_count = self.get_draft_count()
        result['draft_count'] = draft_count

        # 获取用户增减数据
        user_summary = self._get_user_summary()
        result['user_summary'] = user_summary.get('list', [])

        # 获取图文数据
        article_summary = self._get_article_summary()
        result['article_summary'] = article_summary.get('list', [])

        # 计算模拟收益（基于阅读量等数据）
        result['revenue'] = self._calculate_revenue(result)

        print("成功获取公众号综合信息")
        return result

    def _calculate_revenue(self, info: Dict[str, Any]) -> Dict[str, float]:
        """计算模拟收益（基于阅读量等数据的估算）"""
        total_revenue = 0
        yesterday_revenue = 0

        # 基于图文数据计算收益（每1000阅读量 = 1元收益，这是模拟数据）
        article_data = info.get('article_summary', [])

        for item in article_data:
            # 获取阅读量
            int_page_read_count = item.get('int_page_read_count', 0)
            # 模拟收益计算：每1000阅读量0.5元
            revenue = int_page_read_count * 0.0005
            total_revenue += revenue

            # 如果是昨天的数据
            ref_date = item.get('ref_date', '')
            yesterday = (datetime.now() - timedelta(days=1)
                         ).strftime('%Y-%m-%d')
            if ref_date == yesterday:
                yesterday_revenue += revenue

        # 基于用户数据增加基础收益
        user_count = info.get('user_count', {}).get('total_users', 0)
        base_revenue = user_count * 0.001  # 每个关注用户0.001元基础收益
        total_revenue += base_revenue

        return {
            'total_revenue': round(total_revenue, 2),
            'yesterday_revenue': round(yesterday_revenue, 2)
        }

    def format_account_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """格式化公众号信息用于显示"""
        basic_info = info.get('basic_info', {})
        user_count = info.get('user_count', {})
        revenue = info.get('revenue', {})

        formatted_info = {
            'nickname': basic_info.get('nickname', '未知'),
            'head_img': basic_info.get('head_img', ''),
            'service_type': self._get_service_type_name(basic_info.get('service_type_info', {}).get('id', 0)),
            'verify_type': self._get_verify_type_name(basic_info.get('verify_type_info', {}).get('id', 0)),
            'user_name': basic_info.get('user_name', ''),
            'principal_name': basic_info.get('principal_name', ''),
            'alias': basic_info.get('alias', ''),
            'qrcode_url': basic_info.get('qrcode_url', ''),
            'total_users': user_count.get('total_users', 0),
            'draft_count': info.get('draft_count', 0),
            'total_revenue': revenue.get('total_revenue', 0),
            'yesterday_revenue': revenue.get('yesterday_revenue', 0)
        }

        return formatted_info

    def _get_service_type_name(self, service_type_id: int) -> str:
        """获取服务类型名称"""
        service_types = {
            0: '订阅号',
            1: '由历史老帐号升级后的订阅号',
            2: '服务号'
        }
        return service_types.get(service_type_id, '未知')

    def _get_verify_type_name(self, verify_type_id: int) -> str:
        """获取认证类型名称"""
        verify_types = {
            -1: '未认证',
            0: '微信认证',
            1: '新浪微博认证',
            2: '腾讯微博认证',
            3: '已资质认证通过但还未通过名称认证',
            4: '已资质认证通过、还未通过名称认证，但通过了新浪微博认证',
            5: '已资质认证通过、还未通过名称认证，但通过了腾讯微博认证'
        }
        return verify_types.get(verify_type_id, '未知')

    def sync_account_info(self, app_id: Optional[str] = None, app_secret: Optional[str] = None) -> Dict[str, Any]:
        """
        同步公众号信息

        Args:
            app_id: 公众号AppID（可选，使用初始化时的值）
            app_secret: 公众号AppSecret（可选，使用初始化时的值）

        Returns:
            Dict[str, Any]: 包含公众号信息的字典
        """
        # 使用传入的参数或初始化时的参数
        current_app_id = app_id or self.app_id
        current_app_secret = app_secret or self.app_secret

        print(f"开始同步公众号信息: {current_app_id}")

        # 临时更新凭据
        old_app_id, old_app_secret = self.app_id, self.app_secret
        self.app_id, self.app_secret = current_app_id, current_app_secret

        try:
            # 获取基本信息
            basic_info = self.get_account_basic_info()

            # 尝试获取用户数量（如果权限不足则忽略）
            user_count = {'total_users': 0, 'current_users': 0}
            try:
                user_count = self.get_user_count()
            except Exception as e:
                print(f"获取用户数量失败，使用默认值: {str(e)}")

            # 尝试获取草稿箱数量（如果权限不足则忽略）
            draft_count = 0
            try:
                draft_count = self.get_draft_count()
            except Exception as e:
                print(f"获取草稿箱数量失败，使用默认值: {str(e)}")

            # 尝试获取用户增减数据（可选）
            try:
                user_summary = self._get_user_summary()
            except Exception as e:
                print(f"获取用户增减数据失败: {str(e)}")
                user_summary = {'list': []}

            # 尝试获取图文数据（可选）
            try:
                article_summary = self._get_article_summary()
            except Exception as e:
                print(f"获取图文数据失败: {str(e)}")
                article_summary = {'list': []}

            # 计算模拟收益
            total_revenue = 0
            yesterday_revenue = 0

            # 基于图文数据计算收益
            article_data = article_summary.get('list', [])
            for item in article_data:
                int_page_read_count = item.get('int_page_read_count', 0)
                revenue = int_page_read_count * 0.0005  # 每1000阅读量0.5元
                total_revenue += revenue

                # 如果是昨天的数据
                ref_date = item.get('ref_date', '')
                yesterday = (datetime.now() - timedelta(days=1)
                             ).strftime('%Y-%m-%d')
                if ref_date == yesterday:
                    yesterday_revenue += revenue

            # 基于用户数据增加基础收益
            total_users = user_count.get('total_users', 0)
            base_revenue = total_users * 0.001  # 每个关注用户0.001元基础收益
            total_revenue += base_revenue

            # 构建返回的公众号信息字典
            service_type_id = basic_info.get(
                'service_type_info', {}).get('id', 0)
            verify_type_id = basic_info.get(
                'verify_type_info', {}).get('id', -1)

            account_info = {
                'account_appID': current_app_id,
                'app_secret': current_app_secret,
                'nickname': basic_info.get('nickname', ''),
                'head_image': basic_info.get('headimg', ''),
                'service_type': service_type_id,
                'service_type_name': self._get_service_type_name(service_type_id),
                'verify_type': verify_type_id,
                'verify_type_name': self._get_verify_type_name(verify_type_id),
                'username': basic_info.get('user_name', ''),
                'principal_name': basic_info.get('principal_name', ''),
                'alias': basic_info.get('alias', ''),
                'qrcode_url': basic_info.get('qrcode_url', ''),
                'total_users': user_count.get('total_users', 0),
                'draft_count': draft_count,
                'total_revenue': round(total_revenue, 2),
                'yesterday_revenue': round(yesterday_revenue, 2),
                'user_summary': user_summary.get('list', []),
                'article_summary': article_summary.get('list', []),
                'updated_time': datetime.now()
            }

            print(f"成功同步公众号信息: {basic_info.get('nickname', current_app_id)}")
            return account_info

        except Exception as e:
            print(f"同步公众号信息失败: {str(e)}")
            raise e
        finally:
            # 恢复原凭据
            self.app_id, self.app_secret = old_app_id, old_app_secret

    def sync_account_model(self, account: PublicAccount) -> bool:
        """
        同步PublicAccount模型实例

        Args:
            account: PublicAccount模型实例

        Returns:
            bool: 同步是否成功
        """
        try:
            # 调用新的独立函数获取公众号信息
            account_info = self.sync_account_info(
                account.account_appID, account.app_secret)

            # 更新PublicAccount模型的字段
            account.nickname = account_info.get('nickname', account.nickname)
            account.head_image = account_info.get(
                'head_image', account.head_image)
            account.service_type = account_info.get(
                'service_type', account.service_type)
            account.verify_type = account_info.get(
                'verify_type', account.verify_type)
            account.username = account_info.get('username', account.username)
            account.principal_name = account_info.get(
                'principal_name', account.principal_name)
            account.alias = account_info.get('alias', account.alias)
            account.qrcode_url = account_info.get(
                'qrcode_url', account.qrcode_url)
            account.draft_count = account_info.get(
                'draft_count', account.draft_count)
            account.total_revenue = account_info.get(
                'total_revenue', account.total_revenue)
            account.yesterday_revenue = account_info.get(
                'yesterday_revenue', account.yesterday_revenue)
            account.updated_time = account_info.get(
                'updated_time', datetime.now())

            return True

        except Exception as e:
            print(f"同步公众号信息失败: {str(e)}")
            return False


wechat_data: WeChatData = WeChatData()
