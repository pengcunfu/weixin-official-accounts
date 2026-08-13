from flask import g, request
from functools import wraps
import jwt
from app.models.user import User
from app.extensions.config import config_manager
from app.extensions.storage import token_manager
from app.utils.json_result import error


# JWT登录校验装饰器
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 从请求头获取token
            auth = request.headers.get('Authorization', '')
            token = None

            if auth.startswith('Bearer '):
                token = auth[7:]

            if token is None:
                return error('请先登录', 401)

            try:
                # 验证JWT token
                jwt_secret = config_manager.get('jwt.secret', 'your_secret_key')
                jwt_algorithm = config_manager.get('jwt.algorithm', 'HS256')
                payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
                user_id = payload['user_id']

                # 从数据库检查token是否有效
                if token_manager.verify_token(user_id, token):
                    # 刷新token的活动时间
                    token_manager.refresh_token(user_id, token)

                    # 获取用户信息
                    user = User.query.get(user_id)
                    if user and user.deleted_time is None and user.status == 'active':
                        g.user = user
                        g.token = token  # 将token也传递给g对象

                        # 权限检查
                        if role == 'admin':
                            if not user.is_main:
                                return error('权限不足，需要管理员权限', 403)

                        return f(*args, **kwargs)
                    else:
                        return error('用户不存在或已被禁用', 401)
                else:
                    return error('Token已失效，请重新登录', 401)

            except jwt.ExpiredSignatureError:
                return error('Token已过期，请重新登录', 401)
            except jwt.InvalidTokenError:
                return error('Token无效，请重新登录', 401)

        return decorated_function

    # 支持不带参数的调用
    if callable(role):
        func = role
        role = None
        return decorator(func)

    return decorator
