from app.extensions.database import db
from datetime import datetime
from typing import Dict, Any, Optional
from .base import BaseModel


class User(BaseModel):
    """用户模型

    用于存储系统用户的基本信息，包括账号状态、权限和统计数据等。
    支持软删除功能，删除用户时不会真正从数据库中删除记录。
    支持邮箱注册登录。
    """

    id = db.Column(db.Integer, primary_key=True, comment='用户ID，主键')
    email = db.Column(db.String(120), unique=True,
                      nullable=False, comment='邮箱地址，唯一且必填，主要登录方式')
    username = db.Column(db.String(80), unique=True,
                         nullable=True, comment='用户名，唯一但可选')
    phone = db.Column(db.String(11), unique=True,
                      nullable=True, comment='手机号，唯一但可选，11位数字')
    password = db.Column(db.String(120), nullable=False, comment='密码，加密存储')
    avatar = db.Column(db.String(255), nullable=True, comment='用户头像URL')
    nickname = db.Column(db.String(80), nullable=True, comment='用户昵称')
    login_account = db.Column(db.String(80), nullable=True, comment='登录账号')
    is_main = db.Column(db.Boolean, default=False, comment='是否主账号')
    bind_limit = db.Column(db.Integer, default=5, comment='可绑定公众号数量限制')
    register_time = db.Column(
        db.DateTime, default=db.func.now(), comment='注册时间')
    expire_time = db.Column(db.DateTime, nullable=True, comment='账号到期时间')
    status = db.Column(db.String(50), default='正常', comment='账号状态：正常/禁用/锁定等')
    can_post = db.Column(db.Boolean, default=True,
                         comment='是否允许发布文章：True-允许，False-禁止')
    bound_accounts = db.Column(db.Integer, default=0, comment='已绑定的公众号数量')
    uploaded_articles = db.Column(db.Integer, default=0, comment='已上传的文章数量')
    login_count = db.Column(db.Integer, default=0, comment='登录次数统计')
    # 注意：User模型使用不同的时间字段名，但BaseModel已经提供了标准的时间字段

    def __repr__(self):
        """返回用户的字符串表示"""
        return f'<User {self.email}>'

    def soft_delete(self) -> None:
        """软删除用户

        将用户标记为已删除，而不是真正从数据库中删除记录。
        设置 deleted_time 为当前时间。
        """
        self.deleted_time = datetime.now()
        self.deleted_time = datetime.now()  # 同时设置BaseModel的字段
        self.status = '已删除'
        db.session.commit()

    @classmethod
    def get_active(cls):
        """获取所有未删除的用户

        Returns:
            Query: 返回未删除用户的查询对象
        """
        return cls.query.filter_by(deleted_time=None)

    @property
    def is_deleted(self) -> bool:
        """判断用户是否已被删除

        Returns:
            bool: 如果用户已被删除返回 True，否则返回 False
        """
        return self.deleted_time is not None or self.deleted_time is not None

    @property
    def password_mask(self):
        """返回掩码后的密码，用于显示"""
        return '********'

    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """根据邮箱查找用户"""
        return cls.query.filter_by(email=email, deleted_time=None).first()

    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """根据用户名查找用户"""
        return cls.query.filter_by(username=username, deleted_time=None).first()

    @classmethod
    def find_by_login(cls, login_identifier: str) -> Optional['User']:
        """根据登录标识查找用户（邮箱或用户名）"""
        user = cls.find_by_email(login_identifier)
        if not user and login_identifier:
            user = cls.find_by_username(login_identifier)
        return user

    def to_dict(self) -> Dict[str, Any]:
        """将用户实例转换为字典

        Returns:
            dict: 包含用户信息的字典
        """
        # 获取基类的字典
        base_dict = super().to_dict()
        
        # 添加User特有的字段
        user_dict = {
            'email': self.email,
            'username': self.username,
            'phone': self.phone,
            'avatar': self.avatar,
            'nickname': self.nickname,
            'login_account': self.login_account,
            'is_main': self.is_main,
            'bind_limit': self.bind_limit,
            'register_time': self._format_datetime(self.register_time),
            'expire_time': self._format_datetime(self.expire_time),
            'status': self.status,
            'can_post': self.can_post,
            'bound_accounts': self.bound_accounts,
            'uploaded_articles': self.uploaded_articles,
            'login_count': self.login_count,
            'created_time': self._format_datetime(self.created_time),
            'updated_time': self._format_datetime(self.updated_time),
            'deleted_time': self._format_datetime(self.deleted_time)
        }
        
        # 合并字典，User特有字段优先
        return {**base_dict, **user_dict}
