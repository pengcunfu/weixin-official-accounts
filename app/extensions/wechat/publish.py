"""微信公众号「发布」模块。

通过微信 freepublish 接口，将已存到草稿箱的图文（draft media_id）发布为
公众号正式图文页。相比群发（mass/sendall），订阅号、服务号均可使用。

流程：
1. submit    -> freepublish/submit     传入草稿 media_id，返回 publish_id
2. 轮询      -> freepublish/get        依据 publish_status 判断是否成功，成功取文章 url
"""
import time
from datetime import datetime
from typing import Any, Dict, Tuple

from .base import WeChatBase


class WeChatPublish(WeChatBase):
    """公众号草稿发布（freepublish）管理类"""

    def submit(self, media_id: str) -> str:
        """提交发布申请

        Args:
            media_id: 草稿箱中的图文 media_id

        Returns:
            str: publish_id

        Raises:
            Exception: 调用失败时抛出
        """
        data = {'media_id': media_id}
        result = self._make_authenticated_request(
            'POST', '/cgi-bin/freepublish/submit', data=data)

        if 'publish_id' not in result:
            raise Exception(f"提交发布失败: {result}")

        return result['publish_id']

    def get_status(self, publish_id: str) -> Dict[str, Any]:
        """查询发布状态

        publish_status 语义：
            0  发布成功
            1  发布中
            2  原文件审核失败
            3  发布后被删除
        """
        data = {'publish_id': publish_id}
        return self._make_authenticated_request(
            'POST', '/cgi-bin/freepublish/get', data=data)

    def extract_article_url(self, result: Dict[str, Any]) -> str:
        """从发布成功结果中提取文章链接"""
        try:
            item = result['article_detail']['item'][0]
            return item.get('url', '')
        except (KeyError, IndexError, TypeError):
            return ''

    def wait_for_result(self, publish_id: str,
                        max_wait: int = 60, interval: int = 5) -> Dict[str, Any]:
        """轮询发布结果直至成功或超时

        Args:
            publish_id: 提交发布返回的 publish_id
            max_wait: 最大等待秒数
            interval: 每次轮询间隔秒数

        Returns:
            Dict[str, Any]: 带有文章 url 的发布成功结果

        Raises:
            Exception: 审核失败或超时未成功时抛出
        """
        deadline = time.time() + max_wait
        while time.time() < deadline:
            result = self.get_status(publish_id)
            status = result.get('publish_status', -1)

            if status == 0:
                url = self.extract_article_url(result)
                if not url:
                    raise Exception(f"发布成功但未获取到文章链接: {result}")
                return {'url': url, 'publish_id': publish_id}

            if status == 2:
                raise Exception(f"微信返回原文件审核失败，无法发布: {result}")

            if status == 3:
                raise Exception(f"发布后已被删除，请检查公众号后台: {result}")

            # status == 1（发布中）或其他未知状态，继续轮询
            time.sleep(interval)

        raise Exception(f"等待发布结果超时（{max_wait}s），publish_id: {publish_id}")

    def publish_to_account(self, article: Any,
                           public_account: Any) -> Tuple[bool, Any]:
        """将已存稿的文章发布到指定的公众号

        Args:
            article: Article 模型实例（需已存稿，含 draft_media_id）
            public_account: PublicAccount 模型实例

        Returns:
            Tuple[bool, Any]: (成功状态, 含 url/publish_id 的dict 或 错误消息)
        """
        if not article.draft_media_id:
            raise Exception("文章尚未存稿到公众号草稿箱，请先执行『存稿』操作")

        print(f"开始发布文章到公众号: {article.title} -> {public_account.nickname}")

        publish_id = self.submit(article.draft_media_id)
        result = self.wait_for_result(publish_id)

        # 回写文章状态
        article.status = '已发布'
        article.publish_id = publish_id
        article.publish_url = result.get('url')
        article.publish_time = datetime.now()

        print(f"文章发布成功: {article.title} -> {article.publish_url}")

        return True, result