import re
import os
from flask import request
from typing import Type, TypeVar
from app.form.base import BaseForm

T = TypeVar('T', bound=BaseForm)


class ValidationError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def assert_id_exists(form_id, message: str = "ID is required"):
    if not form_id or not form_id.strip():
        raise ValidationError(message)


def validate_args(base_form: Type[T], **kwargs) -> T:
    form = base_form(data=request.args, **kwargs)
    if not form.validate():
        raise ValidationError(f'{form.get_first_error()}')
    return form


def validate_data(base_form: Type[T], **kwargs) -> T:
    # 检查Content-Type请求头
    content_type = request.headers.get('Content-Type', '')
    if not content_type.startswith('application/json'):
        raise ValidationError("请求头必须包含 Content-Type: application/json", 400)

    data = request.get_json()
    if not data:
        raise ValidationError("请求数据不能为空")

    # 使用表单验证
    form = base_form(data=data, **kwargs)
    if not form.validate():
        raise ValidationError(f"{form.get_first_error()}")

    return form


def validate_multipart(base_form: Type[T], **kwargs) -> T:
    """验证multipart/form-data请求"""
    # 对于multipart/form-data，直接使用Flask-WTF的表单处理
    form = base_form(**kwargs)
    if not form.validate():
        raise ValidationError(f"{form.get_first_error()}")

    return form


def validate_form(base_form: Type[T], **kwargs) -> T:
    if request.method == 'GET':
        return validate_args(base_form, **kwargs)
    else:
        # 检查Content-Type来决定使用哪种验证方法
        content_type = request.headers.get('Content-Type', '')
        if content_type.startswith('multipart/form-data'):
            return validate_multipart(base_form, **kwargs)
        else:
            return validate_data(base_form, **kwargs)


def validate_email(email):
    """验证邮箱格式是否正确"""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """验证手机号格式是否正确"""
    if not phone or not isinstance(phone, str):
        return False
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_username(username):
    """验证用户名格式是否正确"""
    if not username or not isinstance(username, str):
        return False
    username = username.strip()
    # 用户名长度3-20位，只能包含字母、数字、下划线、中文
    if len(username) < 3 or len(username) > 20:
        return False
    # 允许字母、数字、下划线、中文字符
    pattern = r'^[a-zA-Z0-9_\u4e00-\u9fff]+$'
    return bool(re.match(pattern, username))


def validate_password(password):
    """验证密码格式是否正确"""
    if not password or not isinstance(password, str):
        return False
    # 密码长度6-20位
    return 6 <= len(password) <= 20


def validate_nickname(nickname):
    """验证昵称格式是否正确"""
    if not nickname or not isinstance(nickname, str):
        return False
    # 昵称长度1-20位，不能包含特殊字符
    nickname = nickname.strip()
    if not nickname or len(nickname) > 20:
        return False
    # 不能包含HTML标签或脚本
    pattern = r'[<>"\']'
    return not re.search(pattern, nickname)


def allowed_image_file(filename):
    """检查图片文件类型是否允许上传"""
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
    return extension in allowed_extensions


def allowed_document_file(filename):
    """检查文档文件类型是否允许上传"""
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    allowed_extensions = {'pdf', 'doc', 'docx', 'txt', 'md', 'html', 'htm'}
    return extension in allowed_extensions


def validate_file_size(file, max_size_mb=5):
    """验证文件大小是否符合要求"""
    if not file:
        return False, "没有文件"

    try:
        # 获取文件大小
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置文件指针

        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return False, f"文件大小不能超过{max_size_mb}MB"

        return True, None
    except Exception as e:
        return False, f"文件大小检查失败: {str(e)}"


def validate_url(url):
    """验证URL格式是否正确"""
    if not url or not isinstance(url, str):
        return False
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))


def validate_app_id(app_id):
    """验证微信公众号AppID格式"""
    if not app_id or not isinstance(app_id, str):
        return False
    # 微信AppID格式：wx开头，18位字符
    pattern = r'^wx[a-zA-Z0-9]{16}$'
    return bool(re.match(pattern, app_id))


def validate_app_secret(app_secret):
    """验证微信公众号AppSecret格式"""
    if not app_secret or not isinstance(app_secret, str):
        return False
    # 微信AppSecret格式：32位字符
    pattern = r'^[a-zA-Z0-9]{32}$'
    return bool(re.match(pattern, app_secret))


def validate_article_title(title):
    """验证文章标题格式"""
    if not title or not isinstance(title, str):
        return False
    title = title.strip()
    if not title or len(title) > 100:
        return False
    # 不能包含HTML标签
    pattern = r'[<>]'
    return not re.search(pattern, title)


def validate_article_category(category):
    """验证文章分类格式"""
    if not category or not isinstance(category, str):
        return False
    category = category.strip()
    if not category or len(category) > 50:
        return False
    # 不能包含特殊字符
    pattern = r'[<>"\'/\\]'
    return not re.search(pattern, category)


def validate_content_length(content, min_length=1, max_length=50000):
    """验证内容长度"""
    if not content or not isinstance(content, str):
        return False, "内容不能为空"

    content_length = len(content.strip())
    if content_length < min_length:
        return False, f"内容长度不能少于{min_length}个字符"
    if content_length > max_length:
        return False, f"内容长度不能超过{max_length}个字符"

    return True, None


def sanitize_filename(filename):
    """清理文件名，移除危险字符"""
    if not filename:
        return "unnamed_file"

    # 移除路径分隔符和危险字符
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    # 限制文件名长度
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]

    return name + ext


def validate_pagination_params(page, limit, max_limit=100):
    """验证分页参数"""
    try:
        page = int(page) if page else 1
        limit = int(limit) if limit else 10

        if page < 1:
            page = 1
        if limit < 1:
            limit = 10
        if limit > max_limit:
            limit = max_limit

        return page, limit, None
    except (ValueError, TypeError):
        return 1, 10, "分页参数格式错误"


def validate_sort_params(sort_field, sort_order, allowed_fields):
    """验证排序参数"""
    if not sort_field:
        return None, None, None

    if sort_field not in allowed_fields:
        return None, None, f"不支持的排序字段: {sort_field}"

    if sort_order and sort_order.lower() not in ['asc', 'desc']:
        return None, None, "排序方向只能是 asc 或 desc"

    sort_order = sort_order.lower() if sort_order else 'desc'
    return sort_field, sort_order, None


def validate_date_range(start_date, end_date):
    """验证日期范围"""
    from datetime import datetime

    try:
        if start_date:
            start_date = datetime.fromisoformat(
                start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        if start_date and end_date and start_date > end_date:
            return None, None, "开始日期不能晚于结束日期"

        return start_date, end_date, None
    except (ValueError, AttributeError):
        return None, None, "日期格式错误"


def validate_required_fields(data, required_fields):
    """验证必填字段"""
    if not data or not isinstance(data, dict):
        return False, "无效的请求数据"

    missing_fields = []
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            missing_fields.append(field)

    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"

    return True, None


def validate_enum_value(value, allowed_values, field_name="字段"):
    """验证枚举值"""
    if value not in allowed_values:
        return False, f"{field_name}的值必须是: {', '.join(allowed_values)}"
    return True, None


def validate_id_list(id_list, field_name="ID列表"):
    """验证ID列表格式"""
    if not id_list:
        return False, f"{field_name}不能为空"

    if not isinstance(id_list, list):
        return False, f"{field_name}必须是数组格式"

    try:
        valid_ids = [int(id_val)
                     for id_val in id_list if str(id_val).isdigit()]
        if len(valid_ids) != len(id_list):
            return False, f"{field_name}包含无效的ID"
        return True, None
    except (ValueError, TypeError):
        return False, f"{field_name}格式错误"


def validate_wechat_token(token):
    """验证微信access_token格式"""
    if not token or not isinstance(token, str):
        return False
    # 微信access_token通常是一个较长的字符串
    return len(token) > 10 and len(token) < 512


def validate_json_string(json_str):
    """验证JSON字符串格式"""
    if not json_str:
        return True  # 空字符串视为有效

    try:
        import json
        json.loads(json_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_status(status, allowed_statuses):
    """验证状态值"""
    if not status:
        return False
    return status in allowed_statuses


def validate_bind_limit(limit):
    """验证绑定限制数量"""
    try:
        limit = int(limit)
        return 1 <= limit <= 100
    except (ValueError, TypeError):
        return False
