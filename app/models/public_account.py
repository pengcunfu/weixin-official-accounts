from app.extensions.database import db
from typing import Dict, Any
from .base import BaseModel


class PublicAccount(BaseModel):
    """
    公众号模型
    用于存储第三方公众号的基本信息、授权状态和收益统计等。
    支持软删除。
    """
    id = db.Column(db.Integer, primary_key=True, comment='公众号编号，主键')
    nickname = db.Column(db.String(100), nullable=True, comment='公众号昵称')
    notes = db.Column(db.String(255), nullable=True, comment='备注')
    account_appID = db.Column(
        db.String(50), unique=True, nullable=False, comment='公众号appID')
    app_secret = db.Column(db.String(100), nullable=False,
                           comment='公众号appsecret')
    access_token = db.Column(db.String(255), nullable=True, comment='访问令牌')
    refresh_token = db.Column(db.String(255), nullable=True, comment='刷新令牌')
    authorized = db.Column(db.Boolean, default=False,
                           nullable=True, comment='是否已授权')
    auth_type = db.Column(db.String(20), default='manual',
                          nullable=True, comment='授权类型：manual=手动/scan=扫码')
    total_revenue = db.Column(db.Numeric(
        10, 2), default=0, nullable=True, comment='总收益')
    yesterday_revenue = db.Column(db.Numeric(
        10, 2), default=0, nullable=True, comment='昨日收益')
    draft_count = db.Column(db.Integer, default=0,
                            nullable=True, comment='草稿箱数量')

    # 新增字段
    head_image = db.Column(db.String(500), nullable=True, comment='公众号头像URL')
    service_type = db.Column(db.Integer, default=0,
                             nullable=True, comment='公众号类型')
    verify_type = db.Column(db.Integer, default=0,
                            nullable=True, comment='认证类型')
    username = db.Column(db.String(100), nullable=True, comment='原始ID')
    principal_name = db.Column(db.String(100), nullable=True, comment='主体名称')
    alias = db.Column(db.String(100), nullable=True, comment='公众号别名')
    qrcode_url = db.Column(db.String(500), nullable=True, comment='二维码URL')

    def __repr__(self):
        return f'<PublicAccount {self.nickname}>'



    def to_dict(self) -> Dict[str, Any]:
        """将公众号实例转换为字典"""
        # 获取基类的字典
        base_dict = super().to_dict()
        
        # 添加PublicAccount特有的字段
        account_dict = {
            'nickname': self.nickname,
            'notes': self.notes,
            'account_appID': self.account_appID,
            'appsecret': self.app_secret,
            'authorized': self.authorized,
            'auth_type': self.auth_type,
            'total_revenue': float(self.total_revenue) if self.total_revenue else 0.0,
            'yesterday_revenue': float(self.yesterday_revenue) if self.yesterday_revenue else 0.0,
            'draft_count': self.draft_count,
            'headimg': self.head_image,
            'service_type': self.service_type,
            'verify_type': self.verify_type,
            'username': self.username,
            'principal_name': self.principal_name,
            'alias': self.alias,
            'qrcode_url': self.qrcode_url
        }
        
        # 合并字典
        return {**base_dict, **account_dict}
