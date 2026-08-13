from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional, Length, ValidationError, Email
from app.models.user import User
from app.utils.validate import validate_email, validate_password
from .base import BaseForm


class LoginForm(BaseForm):
    """用户登录表单"""
    username = StringField('用户名/邮箱', validators=[
        DataRequired(message='用户名和密码不能为空'),
        Length(min=1, max=100, message='用户名长度不正确')
    ])

    password = StringField('密码', validators=[
        DataRequired(message='用户名和密码不能为空'),
        Length(min=1, max=100, message='密码长度不正确')
    ])

    remember = BooleanField('记住我', validators=[Optional()], default=False)


class RegisterForm(BaseForm):
    """用户注册表单"""
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱、验证码和密码均为必填'),
        Email(message='请输入正确的邮箱格式')
    ])

    verification_code = StringField('验证码', validators=[
        DataRequired(message='邮箱、验证码和密码均为必填'),
        Length(min=4, max=10, message='验证码格式不正确')
    ])

    password = StringField('密码', validators=[
        DataRequired(message='邮箱、验证码和密码均为必填'),
        Length(min=6, max=20, message='密码长度必须在6-20位之间')
    ])

    def validate_email(self, field):
        """验证邮箱格式和唯一性"""
        email = field.data.strip()

        if not validate_email(email):
            raise ValidationError('请输入正确的邮箱格式')

        # 检查邮箱是否已注册
        existing_user = User.query.filter_by(email=email, deleted_time=None).first()
        if existing_user:
            raise ValidationError('邮箱已注册')

    def validate_password(self, field):
        """验证密码格式"""
        password = field.data
        if not validate_password(password):
            raise ValidationError('密码长度必须在6-20位之间')


class SendVerificationCodeForm(BaseForm):
    """发送验证码表单"""
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱地址不能为空'),
        Email(message='请输入正确的邮箱格式')
    ])

    type = SelectField('验证码类型', choices=[
        ('register', '注册'),
        ('reset_password', '重置密码')
    ], validators=[
        DataRequired(message='验证码类型不能为空')
    ], default='register')

    def validate_email(self, field):
        """根据类型验证邮箱"""
        email = field.data.strip()

        if not validate_email(email):
            raise ValidationError('请输入正确的邮箱格式')

        code_type = self.type.data

        # 如果是注册验证码，检查邮箱是否已注册
        if code_type == 'register':
            existing_user = User.query.filter_by(email=email, deleted_time=None).first()
            if existing_user:
                raise ValidationError('该邮箱已注册，请直接登录')

        # 如果是密码重置验证码，检查邮箱是否已注册
        elif code_type == 'reset_password':
            existing_user = User.query.filter_by(email=email, deleted_time=None).first()
            if not existing_user:
                raise ValidationError('该邮箱未注册，请先注册账号')


class ResetPasswordForm(BaseForm):
    """重置密码表单"""
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱、验证码和新密码均为必填'),
        Email(message='请输入正确的邮箱格式')
    ])

    verification_code = StringField('验证码', validators=[
        DataRequired(message='邮箱、验证码和新密码均为必填'),
        Length(min=4, max=10, message='验证码格式不正确')
    ])

    new_password = StringField('新密码', validators=[
        DataRequired(message='邮箱、验证码和新密码均为必填'),
        Length(min=6, max=20, message='密码长度必须在6-20位之间')
    ])

    def validate_email(self, field):
        """验证邮箱格式和存在性"""
        email = field.data.strip()

        if not validate_email(email):
            raise ValidationError('请输入正确的邮箱格式')

        # 查找用户
        user = User.query.filter_by(email=email, deleted_time=None).first()
        if not user:
            raise ValidationError('该邮箱未注册')

        # 将用户对象存储到表单中，供后续使用
        self.user = user

    def validate_new_password(self, field):
        """验证新密码格式"""
        password = field.data
        if not validate_password(password):
            raise ValidationError('密码长度必须在6-20位之间')
