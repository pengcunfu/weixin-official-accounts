from flask import Blueprint, request, g
from app.models.user import User
from app.extensions.database import db
import bcrypt
import jwt
from datetime import datetime, timedelta
from app.extensions.config import config_manager
from app.extensions.mail import email_service
from app.utils.validate import validate_form
from app.form.auth import (
    LoginForm, RegisterForm, SendVerificationCodeForm, ResetPasswordForm
)
from app.decorator.exception import catch_exceptions
from app.extensions.storage import token_manager, verification_code_manager
from app.utils.json_result import success, error
from app.decorator.auth import login_required
from app.extensions.loger import get_logger

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 获取日志记录器
logger = get_logger(__name__)


# RESTful API 路由
@auth_bp.route('/login', methods=['POST'])
@catch_exceptions
def login():
    """用户登录"""

    # 表单验证
    form = validate_form(LoginForm)

    # 查找用户（支持邮箱、用户名登录）
    user = User.find_by_login(form.username.data)

    if not user:
        logger.warning(f"登录失败: 用户不存在 - {form.username.data}")
        return error('用户不存在', 401)

    # 验证密码
    if not bcrypt.checkpw(form.password.data.encode('utf-8'), user.password.encode('utf-8')):
        logger.warning(f"登录失败: 密码错误 - 用户ID={user.id}, 用户名={form.username.data}")
        return error('密码错误', 401)

    # 生成JWT token (记住我功能延长过期时间)
    jwt_expire_hours = config_manager.get('jwt.expire_hours', 24)
    expire_hours = jwt_expire_hours * 7 if form.remember.data else jwt_expire_hours
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=expire_hours)
    }
    jwt_secret = config_manager.get('jwt.secret', 'your_secret_key')
    jwt_algorithm = config_manager.get('jwt.algorithm', 'HS256')
    token = jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)

    # 获取设备信息
    device_info = {
        'user_agent': request.headers.get('User-Agent', ''),
        'ip': request.remote_addr,
        'remember': form.remember.data
    }

    # 保存token到数据库
    store_success = token_manager.store_token(
        user.id,
        token,
        device_info
    )

    # 更新登录次数
    user.login_count = (user.login_count or 0) + 1
    db.session.commit()

    logger.info(
        f"用户登录成功: ID={user.id}, 用户名={user.username}, IP={request.remote_addr}, 存储={store_success}")

    return success({
        'token': token,
        'user': {
            'id': user.id,
            'nickname': user.nickname,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'is_main': user.is_main,
            'bind_limit': user.bind_limit,
            'bound_accounts': user.bound_accounts,
            'status': user.status,
            'avatar': user.avatar,
            'register_time': user.register_time.isoformat() if user.register_time else None,
            'expire_time': user.expire_time.isoformat() if user.expire_time else None,
            'login_count': user.login_count
        }
    }, '登录成功')


@auth_bp.route('/register', methods=['POST'])
@catch_exceptions
def register():
    """用户注册"""

    # 表单验证
    form = validate_form(RegisterForm)

    # 验证验证码
    verify_success, verify_message = verification_code_manager.verify_code(
        form.email.data, form.verification_code.data, 'register'
    )

    if not verify_success:
        logger.warning(f"注册失败: 验证码验证失败 - {form.email.data}, 错误={verify_message}")
        return error(verify_message, 400)

    # 密码加密
    hashed = bcrypt.hashpw(
        form.password.data.encode('utf-8'), bcrypt.gensalt())

    # 创建用户（只需要邮箱和密码）
    user = User(
        email=form.email.data,
        password=hashed.decode('utf-8'),
        nickname=form.email.data.split('@')[0],  # 默认昵称为邮箱前缀
        register_time=datetime.utcnow(),
        status='active'
    )
    db.session.add(user)
    db.session.commit()

    logger.info(f"用户注册成功: ID={user.id}, 邮箱={user.email}, 昵称={user.nickname}")

    return success({
        'user': {
            'id': user.id,
            'email': user.email,
            'nickname': user.nickname
        }
    }, '注册成功')


@auth_bp.route('/check', methods=['GET'])
@catch_exceptions
@login_required
def check_auth():
    """检查登录状态"""
    user = g.user
    logger.debug(f"身份验证检查通过: 用户ID={user.id}, 用户名={user.username}")
    return success({
        'user': {
            'id': user.id,
            'nickname': user.nickname,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'is_main': user.is_main,
            'bind_limit': user.bind_limit,
            'bound_accounts': user.bound_accounts,
            'status': user.status,
            'avatar': user.avatar,
            'register_time': user.register_time.isoformat() if user.register_time else None,
            'expire_time': user.expire_time.isoformat() if user.expire_time else None,
            'login_count': user.login_count
        }
    })


@auth_bp.route('/logout', methods=['POST'])
@catch_exceptions
@login_required
def logout():
    """用户登出"""

    # 由于有@login_required装饰器，g.user和g.token都已确保存在
    user = g.user
    token = g.token

    # 撤销当前token
    token_manager.revoke_token(user.id, token)
    logger.info(f"用户登出成功: ID={user.id}, 用户名={user.username}")

    return success(message='登出成功')


@auth_bp.route('/send_verification_code', methods=['POST'])
@catch_exceptions
def send_verification_code():
    """发送邮箱验证码"""

    # 表单验证
    form = validate_form(SendVerificationCodeForm)

    email = form.email.data
    code_type = form.type.data

    # 检查是否频繁发送验证码
    if verification_code_manager.is_code_sent_recently(email, code_type, interval=60):
        ttl = verification_code_manager.get_code_ttl(email, code_type)
        logger.warning(f"验证码发送过于频繁: {email}, 类型={code_type}, TTL={ttl}秒")
        return error(f'验证码发送过于频繁，请{ttl}秒后再试', 429)

    # 发送验证码（email_service内部已经处理了验证码存储）
    result = email_service.send_verification_code(email, code_type)

    if result['success']:
        logger.info(f"验证码发送成功: {email}, 类型={code_type}")
        return success(message='验证码已发送到您的邮箱，请查收')
    else:
        logger.error(f"验证码发送失败: {email}, 类型={code_type}, 错误={result['message']}")
        return error(result['message'], 500)


@auth_bp.route('/reset_password', methods=['POST'])
@catch_exceptions
def reset_password():
    """重置密码"""

    # 表单验证
    form = validate_form(ResetPasswordForm)
    user = form.user  # 从表单验证中获取用户对象

    # 验证验证码
    verify_success, verify_message = verification_code_manager.verify_code(
        form.email.data, form.verification_code.data, 'reset_password'
    )
    if not verify_success:
        logger.warning(f"密码重置失败: 验证码验证失败 - {form.email.data}, 错误={verify_message}")
        return error(verify_message, 400)

    # 更新密码
    hashed = bcrypt.hashpw(
        form.new_password.data.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed.decode('utf-8')

    # 撤销所有活跃的登录token
    token_manager.revoke_user_tokens(user.id)

    db.session.commit()

    logger.info(f"密码重置成功: 用户ID={user.id}, 邮箱={user.email}")
    return success(message='密码重置成功，请重新登录')


@auth_bp.route('/refresh_token', methods=['POST'])
@catch_exceptions
@login_required
def refresh_token():
    """刷新Token"""

    user = g.user

    # 生成新的JWT token
    jwt_expire_hours = config_manager.get('jwt.expire_hours', 24)
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=jwt_expire_hours)
    }
    jwt_secret = config_manager.get('jwt.secret', 'your_secret_key')
    jwt_algorithm = config_manager.get('jwt.algorithm', 'HS256')
    new_token = jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)

    # 撤销旧token并保存新token到数据库
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        old_token = auth[7:]
        token_manager.revoke_token(user.id, old_token)

    # 保存新token到数据库
    device_info = {
        'user_agent': request.headers.get('User-Agent', ''),
        'ip': request.remote_addr,
        'refresh': True
    }
    token_manager.store_token(user.id, new_token, device_info)

    db.session.commit()

    logger.info(f"Token刷新成功: 用户ID={user.id}, 用户名={user.username}, IP={request.remote_addr}")

    return success({
        'token': new_token,
        'user': {
            'id': user.id,
            'nickname': user.nickname,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'is_main': user.is_main,
            'bind_limit': user.bind_limit,
            'bound_accounts': user.bound_accounts,
            'status': user.status,
            'avatar': user.avatar,
            'register_time': user.register_time.isoformat() if user.register_time else None,
            'expire_time': user.expire_time.isoformat() if user.expire_time else None,
            'login_count': user.login_count
        }
    }, 'Token刷新成功')
