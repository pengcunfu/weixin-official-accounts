from wtforms import StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Optional, Length, ValidationError, NumberRange
from app.models.public_account import PublicAccount
from .base import BaseForm


class ArticleListForm(BaseForm):
    """文章列表查询表单"""
    page = IntegerField('页码', validators=[
        Optional(),
        NumberRange(min=1, message='页码必须大于0')
    ], default=1)

    limit = IntegerField('每页数量', validators=[
        Optional(),
        NumberRange(min=1, max=100, message='每页数量必须在1-100之间')
    ], default=10)

    title = StringField('文章标题', validators=[
        Optional(),
        Length(max=200, message='标题长度不能超过200个字符')
    ])

    category = StringField('文章分类', validators=[
        Optional(),
        Length(max=50, message='分类长度不能超过50个字符')
    ])


class CreateArticleForm(BaseForm):
    """创建文章表单"""
    title = StringField('文章标题', validators=[
        Optional(),
        Length(max=200, message='标题长度不能超过200个字符')
    ])

    category = StringField('文章分类', validators=[
        Optional(),
        Length(max=50, message='分类长度不能超过50个字符')
    ], default='默认')

    file_type = StringField('文件类型', validators=[
        Optional(),
        Length(max=20, message='文件类型长度不能超过20个字符')
    ])

    status = SelectField('文章状态', choices=[
        ('草稿', '草稿'),
        ('已发布', '已发布'),
        ('已删除', '已删除')
    ], validators=[Optional()], default='草稿')

    saved_status = SelectField('存稿状态', choices=[
        ('未存稿', '未存稿'),
        ('已存稿', '已存稿')
    ], validators=[Optional()], default='未存稿')

    public_account_nickname = StringField('公众号昵称', validators=[
        Optional(),
        Length(max=100, message='公众号昵称长度不能超过100个字符')
    ])

    author_nickname = StringField('作者昵称', validators=[
        Optional(),
        Length(max=50, message='作者昵称长度不能超过50个字符')
    ])

    uploader_phone = StringField('上传者手机号', validators=[
        Optional(),
        Length(max=20, message='手机号长度不能超过20个字符')
    ])

    # 文档相关字段（从上传API返回）
    path = StringField('文档路径', validators=[
        Optional(),
        Length(max=500, message='文档路径长度不能超过500个字符')
    ])

    original_name = StringField('原始文件名', validators=[
        Optional(),
        Length(max=255, message='原始文件名长度不能超过255个字符')
    ])

    # 封面相关字段（从上传API返回）
    cover_path = StringField('封面路径', validators=[
        Optional(),
        Length(max=500, message='封面路径长度不能超过500个字符')
    ])

    cover_original_name = StringField('封面原始文件名', validators=[
        Optional(),
        Length(max=255, message='封面原始文件名长度不能超过255个字符')
    ])


class UpdateArticleForm(BaseForm):
    """更新文章表单"""
    title = StringField('文章标题', validators=[
        Optional(),
        Length(max=200, message='标题长度不能超过200个字符')
    ])

    category = StringField('文章分类', validators=[
        Optional(),
        Length(max=50, message='分类长度不能超过50个字符')
    ])

    file_type = StringField('文件类型', validators=[
        Optional(),
        Length(max=20, message='文件类型长度不能超过20个字符')
    ])

    status = SelectField('文章状态', choices=[
        ('草稿', '草稿'),
        ('已发布', '已发布'),
        ('已删除', '已删除')
    ], validators=[Optional()])

    saved_status = SelectField('存稿状态', choices=[
        ('未存稿', '未存稿'),
        ('已存稿', '已存稿')
    ], validators=[Optional()])

    public_account_nickname = StringField('公众号昵称', validators=[
        Optional(),
        Length(max=100, message='公众号昵称长度不能超过100个字符')
    ])

    author_nickname = StringField('作者昵称', validators=[
        Optional(),
        Length(max=50, message='作者昵称长度不能超过50个字符')
    ])

    uploader_phone = StringField('上传者手机号', validators=[
        Optional(),
        Length(max=20, message='手机号长度不能超过20个字符')
    ])

    # 文档相关字段（从上传API返回）
    path = StringField('文档路径', validators=[
        Optional(),
        Length(max=500, message='文档路径长度不能超过500个字符')
    ])

    original_name = StringField('原始文件名', validators=[
        Optional(),
        Length(max=255, message='原始文件名长度不能超过255个字符')
    ])

    # 封面相关字段（从上传API返回）
    cover_path = StringField('封面路径', validators=[
        Optional(),
        Length(max=500, message='封面路径长度不能超过500个字符')
    ])

    cover_original_name = StringField('封面原始文件名', validators=[
        Optional(),
        Length(max=255, message='封面原始文件名长度不能超过255个字符')
    ])


class UpdateArticleContentForm(BaseForm):
    """更新文章内容表单"""
    title = StringField('文章标题', validators=[
        Optional(),
        Length(max=200, message='标题长度不能超过200个字符')
    ])

    content = TextAreaField('文章内容', validators=[
        DataRequired(message='文档内容不能为空'),
        Length(min=1, message='文档内容不能为空')
    ])


class SaveToAccountForm(BaseForm):
    """保存到公众号表单"""
    account_id = IntegerField('公众号ID', validators=[
        DataRequired(message='请选择公众号'),
        NumberRange(min=1, message='公众号ID无效')
    ])

    def validate_account_id(self, field):
        """验证公众号是否存在"""
        account = PublicAccount.query.filter_by(
            id=field.data,
            authorized=True,
            deleted_time=None
        ).first()
        if not account:
            raise ValidationError('公众号不存在或未授权')

        # 将公众号对象存储到表单中，供后续使用
        self.account = account
