from wtforms import StringField, IntegerField, FileField
from wtforms.validators import DataRequired, Optional, ValidationError, NumberRange
from app.utils.validate import allowed_image_file, allowed_document_file, validate_file_size
from app.models.user import User
from flask import g
from .base import BaseForm


class FileTypeValidator:
    """文件类型验证器"""

    def __init__(self, allowed_types, message=None):
        self.allowed_types = allowed_types
        self.message = message

    def __call__(self, form, field):
        if field.data and hasattr(field.data, 'filename'):
            if field.data.filename:
                if self.allowed_types == 'image':
                    if not allowed_image_file(field.data.filename):
                        raise ValidationError(self.message or '不支持的图片格式，支持：png、jpg、jpeg、gif、webp、svg')
                elif self.allowed_types == 'document':
                    if not allowed_document_file(field.data.filename):
                        raise ValidationError(self.message or '不支持的文档格式，支持：pdf、doc、docx、txt、md、html、htm')


class FileSizeValidator:
    """文件大小验证器"""

    def __init__(self, max_size_mb=5, message=None):
        self.max_size_mb = max_size_mb
        self.message = message

    def __call__(self, form, field):
        if field.data and hasattr(field.data, 'read'):
            valid, error_msg = validate_file_size(field.data, max_size_mb=self.max_size_mb)
            if not valid:
                raise ValidationError(self.message or error_msg)


class ImageUploadForm(BaseForm):
    """图片上传表单验证"""
    file = FileField('图片文件', validators=[
        DataRequired(message='请选择要上传的图片文件'),
        FileTypeValidator('image'),
        FileSizeValidator(max_size_mb=5)
    ])

    max_size = IntegerField('最大文件大小(MB)', validators=[
        Optional(),
        NumberRange(min=1, max=50, message='文件大小限制必须在1-50MB之间')
    ], default=5)

    def validate_file(self, field):
        """动态文件大小验证"""
        if field.data and self.max_size.data:
            valid, error_msg = validate_file_size(field.data, max_size_mb=self.max_size.data)
            if not valid:
                raise ValidationError(error_msg)


class DocumentUploadForm(BaseForm):
    """文档上传表单验证"""
    file = FileField('文档文件', validators=[
        DataRequired(message='请选择要上传的文档文件'),
        FileTypeValidator('document'),
        FileSizeValidator(max_size_mb=20)
    ])

    public_account_id = IntegerField('公众号ID', validators=[
        DataRequired(message='请选择公众号')
    ])

    max_size = IntegerField('最大文件大小(MB)', validators=[
        Optional(),
        NumberRange(min=1, max=100, message='文件大小限制必须在1-100MB之间')
    ], default=20)

    def validate_file(self, field):
        """动态文件大小验证"""
        if field.data and self.max_size.data:
            valid, error_msg = validate_file_size(field.data, max_size_mb=self.max_size.data)
            if not valid:
                raise ValidationError(error_msg)

    def validate_public_account_id(self, field):
        """验证公众号是否存在且用户有权限"""
        if field.data:
            from app.models.public_account import PublicAccount
            account = PublicAccount.query.filter_by(
                id=field.data, 
                deleted_time=None
            ).first()
            if not account:
                raise ValidationError('所选公众号不存在')


class AvatarUploadForm(BaseForm):
    """头像上传表单验证"""
    file = FileField('头像文件', validators=[
        DataRequired(message='请选择要上传的头像文件'),
        FileTypeValidator('image', message='不支持的图片格式，支持：png、jpg、jpeg、gif、webp'),
        FileSizeValidator(max_size_mb=2, message='头像文件大小不能超过2MB')
    ])

    user_id = IntegerField('用户ID', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(AvatarUploadForm, self).__init__(*args, **kwargs)
        self.target_user = None

    def validate_user_id(self, field):
        """验证用户权限"""
        if field.data:
            # 管理员为其他用户上传头像
            if not g.user or not g.user.is_main:
                raise ValidationError('权限不足')

            target_user = User.query.filter_by(id=field.data, deleted_time=None).first()
            if not target_user:
                raise ValidationError('用户不存在')

            self.target_user = target_user
        else:
            # 用户为自己上传头像
            self.target_user = g.user


class CoverUploadForm(BaseForm):
    """封面上传表单验证"""
    file = FileField('封面文件', validators=[
        DataRequired(message='请选择要上传的封面文件'),
        FileTypeValidator('image', message='不支持的图片格式，支持：png、jpg、jpeg、gif、webp'),
        FileSizeValidator(max_size_mb=10, message='封面文件大小不能超过10MB')
    ])


class FileDeleteForm(BaseForm):
    """文件删除表单验证"""
    path = StringField('文件路径', validators=[
        DataRequired(message='文件路径不能为空')
    ])

    def validate_path(self, field):
        """验证文件路径安全性"""
        if field.data:
            # 安全检查：确保文件路径在uploads目录下
            if not field.data.startswith('uploads/'):
                raise ValidationError('无效的文件路径')

            # 防止路径遍历攻击
            if '..' in field.data or field.data.startswith('/'):
                raise ValidationError('无效的文件路径')
