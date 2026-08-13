from wtforms import StringField
from wtforms.validators import DataRequired, Optional, Length, ValidationError, Email
from app.models.user import User
from app.utils.validate import validate_email, validate_phone
from flask import g
import bcrypt
from .base import BaseForm


class UpdateProfileForm(BaseForm):
    """更新个人信息表单"""
    nickname = StringField('昵称', validators=[
        Optional(),
        Length(min=1, max=20, message='昵称长度必须在1-20个字符之间')
    ])

    username = StringField('用户名', validators=[
        Optional(),
        Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
    ])

    email = StringField('邮箱', validators=[
        Optional(),
        Email(message='请输入正确的邮箱格式')
    ])

    phone = StringField('手机号', validators=[
        Optional(),
        Length(min=11, max=11, message='手机号必须是11位')
    ])

    avatar = StringField('头像URL', validators=[Optional()])

    def validate_nickname(self, field):
        """验证昵称"""
        if field.data:
            nickname = field.data.strip()
            if not nickname:
                raise ValidationError('昵称不能为空')

    def validate_username(self, field):
        """验证用户名唯一性"""
        if field.data:
            username = field.data.strip()
            if not username:
                return

            # 检查用户名是否已被其他用户使用
            current_user = g.user
            existing_user = User.query.filter(
                User.username == username,
                User.id != current_user.id,
                User.deleted_time == None
            ).first()
            if existing_user:
                raise ValidationError('用户名已被使用')

    def validate_email(self, field):
        """验证邮箱格式和唯一性"""
        if field.data:
            email = field.data.strip()
            if not email:
                return

            if not validate_email(email):
                raise ValidationError('请输入正确的邮箱格式')

            # 检查邮箱是否已被其他用户使用
            current_user = g.user
            existing_user = User.query.filter(
                User.email == email,
                User.id != current_user.id,
                User.deleted_time == None
            ).first()
            if existing_user:
                raise ValidationError('邮箱已被使用')

    def validate_phone(self, field):
        """验证手机号格式"""
        if field.data:
            phone = field.data.strip()
            if not phone:
                return

            if not validate_phone(phone):
                raise ValidationError('请输入正确的手机号格式')


class UpdatePasswordForm(BaseForm):
    """修改密码表单"""
    currentPassword = StringField('当前密码', validators=[
        DataRequired(message='当前密码不能为空')
    ])

    newPassword = StringField('新密码', validators=[
        DataRequired(message='新密码不能为空'),
        Length(min=6, max=16, message='新密码长度必须在6-16位之间')
    ])

    confirmPassword = StringField('确认新密码', validators=[
        Optional()
    ])

    def __init__(self, *args, **kwargs):
        super(UpdatePasswordForm, self).__init__(*args, **kwargs)
        self.current_user = g.user

    def validate_currentPassword(self, field):
        """验证当前密码"""
        if not self.current_user:
            raise ValidationError('用户不存在')

        current_password = field.data
        if not bcrypt.checkpw(current_password.encode('utf-8'), self.current_user.password.encode('utf-8')):
            raise ValidationError('当前密码错误')

    def validate_newPassword(self, field):
        """验证新密码"""
        if not self.current_user:
            return

        new_password = field.data

        # 验证新密码不能与当前密码相同
        if bcrypt.checkpw(new_password.encode('utf-8'), self.current_user.password.encode('utf-8')):
            raise ValidationError('新密码不能与当前密码相同')

    def validate_confirmPassword(self, field):
        """验证确认密码"""
        if field.data and self.newPassword.data:
            if field.data != self.newPassword.data:
                raise ValidationError('两次输入的新密码不一致')
