from wtforms import StringField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, ValidationError, NumberRange
from app.models.public_account import PublicAccount
from .base import BaseForm


class AccountListForm(BaseForm):
    """公众号列表查询表单"""
    page = IntegerField('页码', validators=[
        Optional(),
        NumberRange(min=1, message='页码必须大于0')
    ], default=1)

    limit = IntegerField('每页数量', validators=[
        Optional(),
        NumberRange(min=1, max=100, message='每页数量必须在1-100之间')
    ], default=10)

    nickname = StringField('公众号昵称', validators=[
        Optional(),
        Length(max=100, message='昵称长度不能超过100个字符')
    ])


class CreateAccountForm(BaseForm):
    """创建公众号表单"""
    account_appID = StringField('AppID', validators=[
        DataRequired(message='AppID不能为空'),
        Length(min=18, max=18, message='AppID必须是18位')
    ])

    appsecret = StringField('AppSecret', validators=[
        DataRequired(message='AppSecret不能为空'),
        Length(min=32, max=32, message='AppSecret必须是32位')
    ])

    notes = StringField('备注', validators=[
        Optional(),
        Length(max=500, message='备注长度不能超过500个字符')
    ])

    def validate_account_appID(self, field):
        """验证AppID格式和唯一性"""
        app_id = field.data.strip()

        # 验证格式
        if not app_id.startswith('wx'):
            raise ValidationError('AppID必须以wx开头')

        if not app_id[2:].replace('_', '').replace('-', '').isalnum():
            raise ValidationError('AppID格式不正确')

        # 验证唯一性
        existing = PublicAccount.query.filter_by(
            account_appID=app_id,
            deleted_time=None
        ).first()
        if existing:
            raise ValidationError(f'AppID "{app_id}" 已存在')

    def validate_appsecret(self, field):
        """验证AppSecret格式"""
        app_secret = field.data.strip()
        if not app_secret.replace('_', '').replace('-', '').isalnum():
            raise ValidationError('AppSecret格式不正确')


class UpdateAccountForm(BaseForm):
    """更新公众号表单"""
    account_appID = StringField('AppID', validators=[
        Optional(),
        Length(min=18, max=18, message='AppID必须是18位')
    ])

    appsecret = StringField('AppSecret', validators=[
        Optional(),
        Length(min=32, max=32, message='AppSecret必须是32位')
    ])

    notes = StringField('备注', validators=[
        Optional(),
        Length(max=500, message='备注长度不能超过500个字符')
    ])

    authorized = BooleanField('授权状态', validators=[Optional()])

    def __init__(self, account_id=None, *args, **kwargs):
        super(UpdateAccountForm, self).__init__(*args, **kwargs)
        self.account_id = account_id

    def validate_account_appID(self, field):
        """验证AppID格式和唯一性"""
        if not field.data:
            return

        app_id = field.data.strip()

        # 验证格式
        if not app_id.startswith('wx'):
            raise ValidationError('AppID必须以wx开头')

        if not app_id[2:].replace('_', '').replace('-', '').isalnum():
            raise ValidationError('AppID格式不正确')

        # 验证唯一性（排除当前账号）
        existing = PublicAccount.query.filter(
            PublicAccount.account_appID == app_id,
            PublicAccount.id != self.account_id,
            PublicAccount.deleted_time == None
        ).first()
        if existing:
            raise ValidationError(f'AppID "{app_id}" 已被其他账号使用')

    def validate_appsecret(self, field):
        """验证AppSecret格式"""
        if not field.data:
            return

        app_secret = field.data.strip()
        if not app_secret.replace('_', '').replace('-', '').isalnum():
            raise ValidationError('AppSecret格式不正确')


class AuthStatusForm(BaseForm):
    """检查授权状态表单"""
    auth_code = StringField('授权码', validators=[
        DataRequired(message='缺少授权码参数'),
        Length(min=1, max=200, message='授权码长度不正确')
    ])


class ValidateCredentialsForm(BaseForm):
    """验证账号凭证表单"""
    account_appID = StringField('AppID', validators=[
        DataRequired(message='AppID不能为空'),
        Length(min=18, max=18, message='AppID必须是18位')
    ])

    appsecret = StringField('AppSecret', validators=[
        DataRequired(message='AppSecret不能为空'),
        Length(min=32, max=32, message='AppSecret必须是32位')
    ])

    def validate_account_appID(self, field):
        """验证AppID格式"""
        app_id = field.data.strip()

        # 验证格式
        if not app_id.startswith('wx'):
            raise ValidationError('AppID必须以wx开头')

        if not app_id[2:].replace('_', '').replace('-', '').isalnum():
            raise ValidationError('AppID格式不正确')

    def validate_appsecret(self, field):
        """验证AppSecret格式"""
        app_secret = field.data.strip()
        if not app_secret.replace('_', '').replace('-', '').isalnum():
            raise ValidationError('AppSecret格式不正确')
