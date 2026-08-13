from flask import Blueprint
from app.decorator.auth import login_required
from app.decorator.exception import catch_exceptions
from app.utils.upload_file import save_file
from app.utils.validate import validate_form
from app.form.upload import (
    ImageUploadForm, DocumentUploadForm, AvatarUploadForm,
    CoverUploadForm, FileDeleteForm
)
from app.extensions.database import db
from app.extensions.config import config_manager
import os
import time
from app.utils.json_result import success, error
from app.extensions.docx_process import docx_process
from flask import g

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')


@upload_bp.route('/image', methods=['POST'])
@catch_exceptions
@login_required
def upload_image():
    """通用图片上传接口 - 用于富文本编辑器等"""

    # 文件上传表单验证
    form = ImageUploadForm()
    if not form.validate():
        return error(form.get_first_error(), 400)

    file = form.file.data

    # 使用文件上传管理器
    relative_path, absolute_path, original_filename = save_file(
        file, 'images')

    # 构造访问URL
    image_url = f"/{relative_path}"

    return success({
        'url': image_url,
        'path': relative_path,
        'original_name': original_filename,
        'size': os.path.getsize(absolute_path)
    }, '图片上传成功')


@upload_bp.route('/document', methods=['POST'])
@catch_exceptions
@login_required
def upload_document():
    """文档上传接口 - 支持DOCX、PDF等文档格式，并自动创建文章"""
    current_user = g.get('user')

    # 文件上传表单验证
    form = DocumentUploadForm()
    if not form.validate():
        return error(form.get_first_error(), 400)

    file = form.file.data

    # 根据文件类型选择子目录
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    if file_ext in ['doc', 'docx']:
        sub_dir = 'docx'
    elif file_ext == 'pdf':
        sub_dir = 'pdf'
    else:
        sub_dir = 'documents'

    # 使用文件上传管理器
    relative_path, absolute_path, original_filename = save_file(
        file, sub_dir)

    # 解析文档并直接创建Article对象
    new_article = docx_process.parse_docx(
        file_path=absolute_path,
        current_user=current_user,
        relative_path=relative_path,
        file_ext=file_ext
    )

    # 设置公众号关联信息
    public_account_id = form.public_account_id.data
    if public_account_id:
        from app.models.public_account import PublicAccount
        public_account = PublicAccount.query.filter_by(
            id=public_account_id, 
            deleted_time=None
        ).first()
        if public_account:
            new_article.public_account_id = public_account_id
            new_article.public_account_nickname = public_account.nickname or public_account.name

    db.session.add(new_article)
    db.session.commit()

    return success({
        'path': relative_path,
        'original_name': original_filename,
        'file_type': file_ext,
        'size': os.path.getsize(absolute_path),
        'article': {
            'id': new_article.id,
            'title': new_article.title,
            'status': new_article.status
        }
    }, '文档上传并创建文章成功')


@upload_bp.route('/avatar', methods=['POST'])
@catch_exceptions
@login_required
def upload_avatar():
    """头像上传接口"""

    # 文件上传表单验证
    form = validate_form(AvatarUploadForm)

    file = form.file.data
    target_user = form.target_user

    # 生成安全的文件名
    filename = file.filename
    timestamp = str(int(time.time()))
    name, ext = os.path.splitext(filename)
    new_filename = f"avatar_{target_user.id}_{timestamp}{ext}"

    # 创建上传目录
    avatar_folder = os.path.join(config_manager.get('upload.folders.avatars'), 'avatars')
    os.makedirs(avatar_folder, exist_ok=True)

    # 删除旧头像文件（如果存在）
    if target_user.avatar and target_user.avatar.startswith('/uploads/avatars/'):
        old_file_path = os.path.join(avatar_folder, target_user.avatar[1:])
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except OSError:
                pass

    # 保存新文件
    file_path = os.path.join(avatar_folder, new_filename)
    file.save(file_path)

    # 更新用户头像URL
    avatar_url = f"/uploads/avatars/{new_filename}"
    target_user.avatar = avatar_url
    db.session.commit()

    return success({
        'avatar_url': avatar_url,
        'user_id': target_user.id,
        'size': os.path.getsize(file_path)
    }, '头像上传成功')


@upload_bp.route('/cover', methods=['POST'])
@catch_exceptions
@login_required
def upload_cover():
    """封面图片上传接口 - 用于文章封面"""

    # 文件上传表单验证
    form = CoverUploadForm()
    if not form.validate():
        return error(form.get_first_error(), 400)

    file = form.file.data

    # 使用文件上传管理器
    relative_path, absolute_path, original_filename = save_file(
        file, 'cover')

    # 构造访问URL
    cover_url = f"/{relative_path}"

    return success({
        'url': cover_url,
        'path': relative_path,
        'original_name': original_filename,
        'size': os.path.getsize(absolute_path)
    }, '封面上传成功')


@upload_bp.route('/delete', methods=['POST'])
@catch_exceptions
@login_required
def delete_file():
    """删除已上传的文件"""

    # 表单验证
    form = validate_form(FileDeleteForm)
    file_path = form.path.data

    full_path = file_path

    if os.path.exists(full_path):
        os.remove(full_path)
        return success(message='文件删除成功')
    else:
        return error('文件不存在', 404)
