from flask import Blueprint, g
from app.decorator.auth import login_required
from app.decorator.exception import catch_exceptions
from app.extensions.database import db
from app.extensions.storage import token_manager
from app.utils.validate import validate_form
from app.utils.model_helper import update_model_fields
from app.form.profile import (
    UpdateProfileForm, UpdatePasswordForm
)
import bcrypt

from app.utils.json_result import success

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')


@profile_bp.route('', methods=['GET'])
@catch_exceptions
@login_required
def get_profile():
    """获取用户个人信息"""

    user = g.user

    return success({
        'id': user.id,
        'nickname': user.nickname,
        'username': user.username,
        'phone': user.phone,
        'email': user.email,
        'is_main': user.is_main,
        'bind_limit': user.bind_limit,
        'bound_accounts': user.bound_accounts,
        'register_time': user.register_time.isoformat() if user.register_time else None,
        'expire_time': user.expire_time.isoformat() if user.expire_time else None,
        'avatar': user.avatar,
        'status': user.status,
        'login_count': user.login_count
    })


@profile_bp.route('', methods=['PUT'])
@catch_exceptions
@login_required
def update_profile():
    """更新用户个人信息"""

    user = g.user

    # 表单验证
    form = validate_form(UpdateProfileForm)

    # 使用通用更新函数
    update_model_fields(
        model=user,
        form=form,
        exclude_fields=['csrf_token'],  # 排除CSRF令牌
        auto_update_time=False  # 用户信息更新不需要自动时间戳
    )

    db.session.commit()

    return success({
        'id': user.id,
        'nickname': user.nickname,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'avatar': user.avatar
    }, '个人信息更新成功')


@profile_bp.route('/password', methods=['PUT'])
@catch_exceptions
@login_required
def update_password():
    """修改密码"""

    user = g.user

    # 表单验证
    form = validate_form(UpdatePasswordForm)

    # 更新密码
    new_password_hash = bcrypt.hashpw(form.newPassword.data.encode(
        'utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.password = new_password_hash

    # 撤销除当前token外的所有活跃登录token（可选，增强安全性）
    current_token = g.get('token')

    if current_token:
        token_manager.revoke_user_tokens(user.id, except_token=current_token)

    db.session.commit()

    return success(message='密码修改成功')


@profile_bp.route('/sessions', methods=['GET'])
@catch_exceptions
@login_required('admin')
def get_active_sessions():
    """获取用户活跃的登录会话"""

    user = g.user

    # 获取当前token
    current_token = g.get('token')

    # 获取用户的活跃会话
    active_sessions = token_manager.get_user_active_sessions(user.id)

    sessions = []
    for idx, session in enumerate(active_sessions):
        is_current = (current_token == session['token'])
        sessions.append({
            'id': idx + 1,  # 使用索引作为临时ID
            'created_time': session.get('created_time'),
            'expires_at': None,  # Token没有固定过期时间
            'is_current': is_current,
            'last_activity': session.get('last_activity'),
            # 只显示token前缀，当前会话显示为current
            'token': session['token'][:8] + '...' if not is_current else 'current',
            # 用于撤销的完整token
            'revoke_token': session['token'] if not is_current else None
        })

    return success({
        'sessions': sessions,
        'total': len(sessions)
    })


@profile_bp.route('/sessions/<string:token>', methods=['DELETE'])
@catch_exceptions
@login_required('admin')
def revoke_session(token):
    """撤销指定的登录会话"""

    user = g.user
    # 验证token是否属于当前用户并撤销
    if token_manager.verify_token(user.id, token):
        success_revoke = token_manager.revoke_token(user.id, token)
        if success_revoke:
            return success(message='会话已撤销')
        else:
            raise ValueError('会话撤销失败')
    else:
        raise ValueError('会话不存在或已失效')


@profile_bp.route('/sessions', methods=['DELETE'])
@catch_exceptions
@login_required('admin')
def revoke_all_sessions():
    """撤销所有其他登录会话（保留当前会话）"""

    user = g.user

    # 获取当前token
    current_token = g.get('token')

    # 撤销除当前token外的所有活跃token
    if current_token:
        revoked_count = token_manager.revoke_user_tokens(
            user.id, except_token=current_token)
    else:
        # 如果无法获取当前token，撤销所有活跃token
        revoked_count = token_manager.revoke_user_tokens(user.id)

    return success({
        'revoked_count': revoked_count
    }, f'已撤销 {revoked_count} 个其他会话')
