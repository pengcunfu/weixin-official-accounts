import requests
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from app.models.public_account import PublicAccount
from app.extensions.config import config_manager
from .base import WeChatBase


class WeChatDraft(WeChatBase):
    """微信草稿箱管理类"""

    host_image_path: Optional[str]
    docker_image_path: Optional[str]
    access_token: str

    def __init__(self, app_id: str, app_secret: str) -> None:
        super().__init__(app_id, app_secret)
        # 文件路径配置
        self.host_image_path = config_manager.get('wechat.host_image_path')
        self.docker_image_path = config_manager.get('wechat.docker_image_path')
        
        # 初始化时获取access_token
        self.access_token = self.get_access_token()

    def _upload_material(self, material_type: str, file_data: bytes, file_name: str) -> Dict[str, Any]:
        """上传多媒体素材"""
        files = {'media': (file_name, file_data, 'image/jpeg')}
        params = {'type': material_type}

        result = self._make_authenticated_request('POST', '/cgi-bin/material/add_material',
                                                  params=params, files=files)

        # 将http替换为https
        if 'url' in result:
            result['url'] = result['url'].replace("http://", "https://")

        print(f"素材上传成功: {file_name}")
        return result

    def _upload_image(self, image_url: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """上传图片"""
        if image_url.startswith("http"):
            # 从URL下载图片
            response = requests.get(image_url)
            if not response.ok:
                raise Exception(
                    f"Failed to download image from URL: {image_url}")

            # 从URL获取文件名
            parsed_url = urlparse(image_url.split("?")[0])
            file_name_from_url = os.path.basename(parsed_url.path)
            ext = os.path.splitext(file_name_from_url)[1]
            image_name = file_name or (
                f"{file_name_from_url}.jpg" if not ext else file_name_from_url)

            file_data = response.content

        else:
            # 从本地路径读取图片
            local_image_path = image_url
            if self.host_image_path:
                local_image_path = image_url.replace(
                    self.host_image_path, self.docker_image_path)

            file_name_from_local = os.path.basename(local_image_path)
            ext = os.path.splitext(file_name_from_local)[1]
            image_name = file_name or (
                f"{file_name_from_local}.jpg" if not ext else file_name_from_local)

            with open(local_image_path, 'rb') as f:
                file_data = f.read()

        return self._upload_material('image', file_data, image_name)

    def _upload_images(self, content: str) -> Tuple[str, str]:
        """上传内容中的所有图片并返回更新后的HTML和第一张图片的media_id"""
        if '<img' not in content:
            return content, ""

        soup = BeautifulSoup(content, 'html.parser')
        images = soup.find_all('img')

        media_ids = []

        for img in images:
            src = img.get('src')
            if src:
                if not src.startswith('https://mmbiz.qpic.cn'):
                    # 上传图片并更新src
                    resp = self._upload_image(src)
                    img['src'] = resp['url']
                    media_ids.append(resp['media_id'])
                else:
                    media_ids.append(src)

        first_image_id = media_ids[0] if media_ids else ""
        updated_html = str(soup)

        print(f"成功处理 {len(images)} 张图片")
        return updated_html, first_image_id

    def _publish_to_draft(self, title: str, content: str, cover: str = "") -> Dict[str, Any]:
        """发布文章到草稿箱"""
        print("开始发布文章到草稿箱...")

        # 处理内容中的图片
        html, first_image_id = self._upload_images(content)

        # 处理封面图片
        thumb_media_id = ""
        if cover:
            # 如果指定了封面图片
            resp = self._upload_image(cover, "cover.jpg")
            thumb_media_id = resp['media_id']
        else:
            # 使用第一张图片作为封面
            if first_image_id:
                if first_image_id.startswith("https://mmbiz.qpic.cn"):
                    resp = self._upload_image(first_image_id, "cover.jpg")
                    thumb_media_id = resp['media_id']
                else:
                    thumb_media_id = first_image_id

        if not thumb_media_id:
            raise Exception("你必须指定一张封面图或者在正文中至少出现一张图片。")

        # 构建文章数据
        article_data = {
            "articles": [{
                "title": title,
                "content": html,
                "thumb_media_id": thumb_media_id,
            }]
        }

        # 发布到草稿箱
        result = self._make_authenticated_request(
            'POST', '/cgi-bin/draft.py/add', data=article_data)

        if 'media_id' in result:
            print(f"文章成功发布到草稿箱，media_id: {result['media_id']}")
            return result
        else:
            raise Exception(f"上传到公众号草稿失败: {result}")

    def save_to_account(self, article: Any, public_account: PublicAccount) -> Tuple[bool, str]:
        """
        将Article模型保存到指定的公众号草稿箱

        Args:
            article: Article模型实例
            public_account: PublicAccount模型实例

        Returns:
            Tuple[bool, str]: (成功状态, 消息)
        """
        # 准备文章内容
        content = article.content_html or ""
        if not content and article.file_path:
            # 如果没有HTML内容，尝试从文件解析
            file_path = article.file_path
            if os.path.exists(file_path):
                # 这里可以重新解析文档获取内容，但为了简化先抛出异常
                raise Exception("文章内容为空，需要先解析文档")

        if not content:
            raise Exception("文章内容为空")

        # 准备封面图片路径
        cover_path = ""
        if article.cover_path:
            cover_path = article.cover_path
            if not os.path.exists(cover_path):
                cover_path = ""

        # 调用发布到草稿箱方法
        result = self._publish_to_draft(
            title=article.title,
            content=content,
            cover=cover_path
        )

        # 更新文章状态
        article.saved_status = '已存稿'
        article.public_account_nickname = public_account.nickname or public_account.name
        article.draft_media_id = result.get('media_id')
        article.saved_time = datetime.now()

        print(f"文章成功保存到公众号: {article.title} -> {public_account.nickname}")

        return True, "success"
