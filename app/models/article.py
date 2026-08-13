from app.extensions.database import db
import json
from typing import Dict, Any, List, Union
from .base import BaseModel
import re
from app.utils.upload_file import add_domain_prefix

class Article(BaseModel):
    """
    文章模型
    用于存储上传的文章及其元数据、归属、状态等信息。
    """
    id = db.Column(db.Integer, primary_key=True, comment='文章编号，主键')
    title = db.Column(db.String(255), nullable=False, comment='文章标题')
    category = db.Column(db.String(50), default='默认', comment='文章分类')
    file_type = db.Column(db.String(20), default='docx', comment='文件类型')
    file_path = db.Column(db.String(255), comment='文件存储路径')
    cover_path = db.Column(db.String(255), comment='封面图片路径')
    status = db.Column(db.String(50), default='草稿', comment='文章状态：发布/草稿等')
    saved_status = db.Column(
        db.String(50), default='已保存', comment='是否存稿：已保存/未保存')
    public_account_nickname = db.Column(db.String(100), comment='存稿公众号昵称')
    author_nickname = db.Column(db.String(100), comment='添加账号昵称')
    likes = db.Column(db.Integer, default=0, comment='点赞数/宁数')
    uploader_phone = db.Column(db.String(20), comment='添加账号手机号')
    word_count = db.Column(db.Integer, default=0, comment='文章字数')
    author_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', name='fk_article_author'), comment='作者ID')
    public_account_id = db.Column(db.Integer, db.ForeignKey(
        'public_account.id', name='fk_article_public_account'), comment='关联公众号ID')
    draft_media_id = db.Column(db.String(100), comment='草稿箱media_id')
    saved_time = db.Column(db.DateTime, comment='存稿时间')
    content_html = db.Column(db.Text, comment='HTML格式内容')
    images_info = db.Column(db.Text, comment='图片信息JSON')

    def __repr__(self):
        return f'<Article {self.title}>'



    def set_images_info(self, images_data: Union[List[Dict[str, Any]], Dict[str, Any], None]) -> None:
        """
        设置图片信息，自动转换为JSON字符串存储
        
        Args:
            images_data: 图片信息列表或字典，None表示清空
        """
        self._set_json_field('images_info', images_data)

    def get_images_info(self) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        """
        获取图片信息，自动从JSON字符串解析
        
        Returns:
            解析后的图片信息列表或字典，解析失败返回None
        """
        return self._get_json_field('images_info')

    def _process_images_info(self):
        """处理images_info JSON中的图片路径，只返回filename和url"""
        images_data = self.get_images_info()
        if not images_data:
            return json.dumps([])

        try:

            if isinstance(images_data, list):
                simplified_images = []
                for image in images_data:
                    if isinstance(image, dict):
                        # 只保留filename和url（从local_path生成）
                        simplified_image = {
                            'filename': image.get('filename', ''),
                            'url': add_domain_prefix(image.get('local_path', '')) if image.get('local_path') else ''
                        }
                        simplified_images.append(simplified_image)
                return json.dumps(simplified_images)

            return json.dumps([])
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，返回空数组
            return json.dumps([])

    def _process_content_html(self):
        """处理content_html中的图片src路径，添加域名前缀"""
        if not self.content_html:
            return self.content_html

        def replace_src(match):
            src = match.group(1)
            # 只处理相对路径，跳过已经是完整URL的
            if not src.startswith('http'):
                return f'src="{add_domain_prefix(src)}"'
            return match.group(0)

        # 替换HTML中的图片src属性
        return re.sub(r'src="([^"]*)"', replace_src, self.content_html)

    def to_dict(self) -> Dict[str, Any]:
        """将文章实例转换为字典

        Returns:
            dict: 包含文章所有字段的字典，文件路径会自动添加域名前缀
        """
        from app.utils.upload_file import add_domain_prefix

        # 获取基类的字典
        base_dict = super().to_dict()
        
        # 添加Article特有的字段
        article_dict = {
            'title': self.title,
            'category': self.category,
            'file_type': self.file_type,
            'file_path': add_domain_prefix(self.file_path),
            'cover_path': add_domain_prefix(self.cover_path),
            'status': self.status,
            'saved_status': self.saved_status,
            'public_account_nickname': self.public_account_nickname,
            'author_nickname': self.author_nickname,
            'likes': self.likes,
            'uploader_phone': self.uploader_phone,
            'public_account_id': self.public_account_id,
            'word_count': self.word_count,
            'draft_media_id': self.draft_media_id,
            'saved_time': self._format_datetime(self.saved_time),
            'content_html': self._process_content_html(),
            'images_info': self._process_images_info()
        }
        
        # 合并字典
        return {**base_dict, **article_dict}


