import os
import uuid
from datetime import datetime
from app.extensions.config import config_manager
from flask import request


def allowed_file(filename):
    """检查文件类型是否允许上传"""
    if not filename:
        return False
    from app.extensions.config import config_manager
    allowed_extensions = config_manager.get('upload.allowed_extensions')
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


def allowed_image(filename):
    """检查图片类型是否允许上传"""
    if not filename:
        return False
    from app.extensions.config import config_manager
    allowed_image_extensions = config_manager.get(
        'upload.allowed_image_extensions')
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_image_extensions


def validate_file_extension(filename, allowed_extensions):
    """验证文件扩展名"""
    if not filename:
        return False, "文件名为空"

    if '.' not in filename:
        return False, "文件没有扩展名"

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return False, f"不支持的文件类型，仅支持：{', '.join(allowed_extensions)}"

    return True, ""


def generate_secure_filename(original_filename, use_uuid=True):
    """生成安全的文件名"""
    if not original_filename:
        raise ValueError("原始文件名不能为空")

    filename = original_filename
    if '.' not in filename:
        raise ValueError("文件没有扩展名")

    name, ext = filename.rsplit('.', 1)
    ext = ext.lower()

    if use_uuid:
        unique_name = f"{uuid.uuid4().hex}.{ext}"
    else:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_name = f"{timestamp}_{filename}"

    return unique_name, ext


def ensure_upload_dir(sub_dir='', base_upload_dir=None):
    """确保上传目录存在"""
    if base_upload_dir is None:
        base_dir = '/uploads'
    else:
        base_dir = base_upload_dir
    upload_path = os.path.join(base_dir, sub_dir)
    os.makedirs(upload_path, exist_ok=True)
    return upload_path


def ensure_all_upload_dirs():
    """确保所有上传目录存在"""
    from app.extensions.config import config_manager

    folders = [
        config_manager.get('upload.folders.docx'),
        config_manager.get('upload.folders.cover'),
        config_manager.get('upload.folders.avatars')
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)


def save_file(file, sub_dir='', use_uuid=True, base_upload_dir=None):
    """
    保存上传的文件

    Args:
        file: 上传的文件对象
        sub_dir: 子目录（如 'docx', 'images', 'cover'）
        use_uuid: 是否使用UUID生成文件名
        base_upload_dir: 基础上传目录，默认使用Flask的static_folder + uploads

    Returns:
        tuple: (相对路径, 绝对路径, 原始文件名)
    """
    if not file or not file.filename:
        raise ValueError("没有选择文件")

    # 确保目录存在
    upload_dir = ensure_upload_dir(sub_dir, base_upload_dir)

    # 生成安全文件名
    unique_filename, ext = generate_secure_filename(file.filename, use_uuid)

    # 保存文件
    absolute_path = os.path.join(upload_dir, unique_filename)
    file.save(absolute_path)

    # 返回相对路径
    relative_path = os.path.join(
        'uploads', sub_dir, unique_filename).replace('\\', '/')

    return relative_path, absolute_path, file.filename


def delete_file(file_path):
    """删除文件"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"删除文件失败: {str(e)}")
    return False


def get_file_info(file_path):
    """获取文件信息"""
    try:
        if not os.path.exists(file_path):
            return None

        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'exists': True
        }
    except Exception:
        return None


def add_domain_prefix(file_path):
    """
    为文件路径添加域名前缀
    """
    if not file_path:
        return None

    # 如果已经是完整URL，直接返回
    if file_path.startswith('http'):
        return file_path

    domain = config_manager.get('app.domain')

    # 如果配置存在且不为空，使用配置的域名
    if domain:
        domain = domain.rstrip('/')
    else:
        # 如果配置为空，从请求中自动提取域名
        domain = request.url_root.rstrip('/')

    # 移除路径开头的斜杠（如果有的话）
    if file_path.startswith('/'):
        file_path = file_path[1:]

    return f"{domain}/{file_path}"
