from wtforms import StringField, BooleanField, IntegerField, SelectField, PasswordField
from wtforms.validators import Email, Length, Optional, ValidationError, Regexp, NumberRange
from app.models.user import User
from datetime import datetime
from .base import BaseForm


class UpdateUserForm(BaseForm):
    """更新用户表单验证"""
    username = StringField('用户名', validators=[
        Optional(),
        Length(min=3, max=20, message='用户名长度必须在3-20位之间'),
        Regexp(r'^[a-zA-Z0-9_]+$', message='用户名只能包含字母、数字、下划线')
    ])

    email = StringField('邮箱', validators=[
        Optional(),
        Email(message='邮箱格式不正确')
    ])

    nickname = StringField('昵称', validators=[
        Optional(),
        Length(max=20, message='昵称长度不能超过20个字符')
    ])

    phone = StringField('手机号', validators=[
        Optional(),
        Regexp(r'^1[3-9]\d{9}$', message='手机号格式不正确')
    ])

    password = PasswordField('密码', validators=[
        Optional(),
        Length(min=6, max=20, message='密码长度必须在6-20位之间')
    ])

    avatar = StringField('头像', validators=[Optional()])

    status = SelectField('状态', choices=[
        ('active', '活跃'),
        ('inactive', '非活跃'),
        ('suspended', '暂停'),
        ('已删除', '已删除')
    ], validators=[Optional()])

    can_post = BooleanField('发布权限', validators=[Optional()])
    is_main = BooleanField('是否为管理员', validators=[Optional()])
    bind_limit = IntegerField('绑定限制', validators=[Optional()])
    expire_time = StringField('过期时间', validators=[Optional()])

    def __init__(self, user_id=None, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.user_id = user_id

    def validate_username(self, field):
        """验证用户名唯一性（排除当前用户）"""
        if field.data:
            user = User.query.filter_by(username=field.data, deleted_time=None).filter(
                User.id != self.user_id
            ).first()
            if user:
                raise ValidationError('用户名已存在')

    def validate_email(self, field):
        """验证邮箱唯一性（排除当前用户）"""
        if field.data:
            user = User.query.filter_by(email=field.data, deleted_time=None).filter(
                User.id != self.user_id
            ).first()
            if user:
                raise ValidationError('邮箱已存在')

    def validate_phone(self, field):
        """验证手机号唯一性（排除当前用户）"""
        if field.data:
            user = User.query.filter_by(phone=field.data, deleted_time=None).filter(
                User.id != self.user_id
            ).first()
            if user:
                raise ValidationError('手机号已被使用')

    def validate_expire_time(self, field):
        """验证过期时间格式"""
        if field.data:
            try:
                expire_time = field.data
                if expire_time.endswith('Z'):
                    expire_time = expire_time[:-1] + '+00:00'
                datetime.fromisoformat(expire_time)
            except ValueError:
                raise ValidationError('过期时间格式不正确')


class UpdateUserStatusForm(BaseForm):
    """更新用户状态表单验证"""
    status = SelectField('状态', choices=[
        ('active', '活跃'),
        ('inactive', '非活跃'),
        ('suspended', '暂停'),
        ('已删除', '已删除')
    ], validators=[Optional()])

    can_post = BooleanField('发布权限', validators=[Optional()])


class UserListForm(BaseForm):
    """用户列表查询表单验证"""
    page = IntegerField('页码', validators=[
        Optional(),
        NumberRange(min=1, message='页码必须大于0')
    ], default=1)

    limit = IntegerField('每页数量', validators=[
        Optional(),
        NumberRange(min=1, max=100, message='每页数量必须在1-100之间')
    ], default=10)

    username = StringField('用户名', validators=[Optional()])
    status = StringField('状态', validators=[Optional()])
