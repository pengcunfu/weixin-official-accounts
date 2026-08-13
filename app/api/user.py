from flask import Blueprint, g
from app.decorator.auth import login_required
from app.decorator.exception import catch_exceptions
from app.models.user import User
from app.extensions.database import db
from app.extensions.storage import token_manager
from app.utils.validate import validate_form
from app.utils.model_helper import update_model_fields
from app.form.user import (
    UpdateUserForm, UpdateUserStatusForm,
    UserListForm
)
from datetime import datetime
from app.utils.json_result import success

user_bp = Blueprint('users', __name__, url_prefix='/api/user')


# RESTful API 路由
@user_bp.route('/list', methods=['GET'])
@catch_exceptions
@login_required('admin')
def get_users():
    """获取用户列表（管理员功能）"""

    # 表单验证
    form = validate_form(UserListForm)

    query = User.query.filter_by(deleted_time=None)

    if form.username.data:
        query = query.filter(User.username.like(f'%{form.username.data}%'))
    if form.status.data:
        query = query.filter(User.status == form.status.data)

    total = query.count()
    users = query.order_by(User.id.desc()).offset(
        ((form.page.data or 1) - 1) * (form.limit.data or 10)).limit(form.limit.data or 10).all()

    # 使用模型的to_dict方法
    result = [user.to_dict() for user in users]

    return success({
        'data': result,
        'total': total,
        'page': form.page.data or 1,
        'limit': form.limit.data or 10
    })


@user_bp.route('/<int:user_id>', methods=['GET'])
@catch_exceptions
@login_required
def get_user(user_id):
    """获取单个用户详情"""

    current_user = g.user
    if not current_user:
        raise ValueError('用户未登录')

    # 用户只能查看自己的信息，管理员可以查看所有用户信息
    if not current_user.is_main and current_user.id != user_id:
        raise PermissionError('权限不足')

    user = User.query.filter_by(id=user_id, deleted_time=None).first()
    if not user:
        raise ValueError('用户不存在')

    return success(user.to_dict())


@user_bp.route('/<int:user_id>', methods=['PUT'])
@catch_exceptions
@login_required('admin')
def update_user(user_id):
    """更新用户信息"""

    user = User.query.filter_by(id=user_id, deleted_time=None).first()
    if not user:
        raise ValueError('用户不存在')

    # 表单验证
    form = validate_form(UpdateUserForm, user_id=user.id)

    # 使用通用更新函数，排除特殊处理的字段
    update_model_fields(
        model=user,
        form=form,
        exclude_fields=['csrf_token', 'expire_time'],  # expire_time需要特殊处理
        auto_update_time=False  # 用户信息更新不需要自动时间戳
    )

    # 特殊处理过期时间字段
    if form.expire_time.data:
        expire_time = form.expire_time.data
        if expire_time.endswith('Z'):
            expire_time = expire_time[:-1] + '+00:00'
        new_expire_time = datetime.fromisoformat(expire_time)
        if new_expire_time != user.expire_time:
            user.expire_time = new_expire_time
    elif form.expire_time.data == '' and user.expire_time is not None:
        user.expire_time = None

    db.session.commit()

    return success(user.to_dict(), '用户信息更新成功')


@user_bp.route('/<user_ids>', methods=['DELETE'])
@catch_exceptions
@login_required('admin')
def delete_user(user_ids):
    """删除用户（直接删除）- 支持单个和批量删除"""

    current_user = g.user

    # 解析用户ID，支持单个ID或逗号分隔的多个ID
    try:
        if ',' in str(user_ids):
            # 批量删除：解析逗号分隔的ID
            id_list = [int(id.strip())
                       for id in str(user_ids).split(',') if id.strip()]
        else:
            # 单个删除
            id_list = [int(user_ids)]
    except ValueError:
        raise ValueError('用户ID格式错误')

    if not id_list:
        raise ValueError('用户ID不能为空')

    # 检查不能删除自己
    if current_user.id in id_list:
        raise ValueError('不能删除自己的账号')

    # 查找要删除的用户
    users_to_delete = User.query.filter(
        User.id.in_(id_list)
    ).all()

    if not users_to_delete:
        raise ValueError('没有找到要删除的用户')

    # 获取实际要删除的用户ID列表
    actual_user_ids = [user.id for user in users_to_delete]

    # 撤销这些用户的所有活跃token
    for user_id in actual_user_ids:
        token_manager.revoke_user_tokens(user_id)

    # 直接删除用户记录
    User.query.filter(
        User.id.in_(actual_user_ids)
    ).delete(synchronize_session=False)

    db.session.commit()

    # 根据删除的数量返回不同的消息
    if len(actual_user_ids) == 1:
        return success(message='用户删除成功')
    else:
        return success(message=f'成功删除 {len(actual_user_ids)} 个用户')


@user_bp.route('/<int:user_id>/status', methods=['PUT'])
@catch_exceptions
@login_required('admin')
def update_user_status(user_id):
    """更新用户状态"""

    user = User.query.filter_by(id=user_id, deleted_time=None).first()
    if not user:
        raise ValueError('用户不存在')

    # 表单验证
    form = validate_form(UpdateUserStatusForm)

    # 使用通用更新函数
    update_model_fields(
        model=user,
        form=form,
        exclude_fields=['csrf_token'],  # 排除CSRF令牌
        auto_update_time=False  # 用户状态更新不需要自动时间戳
    )

    db.session.commit()

    return success(user.to_dict(), '用户状态更新成功')
