from flask import current_app
from functools import wraps
import traceback
from datetime import datetime
import jwt
from sqlalchemy.exc import IntegrityError, OperationalError
import pymysql.err
from app.utils.json_result import error
from app.extensions.loger import get_logger
from app.utils.validate import ValidationError


def catch_exceptions(f):
    """
    通用异常捕获装饰器
    专门用于API接口的异常处理，返回统一格式的JSON响应
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger = get_logger(__name__)

        try:
            return f(*args, **kwargs)

        # JWT相关异常
        except jwt.ExpiredSignatureError:
            logger.warning(f"Token expired in {f.__name__}")
            return error('Token已过期，请重新登录', 401)

        except jwt.InvalidTokenError:
            logger.warning(f"Invalid token in {f.__name__}")
            return error('Token无效，请重新登录', 401)

        # 数据库完整性约束异常
        except IntegrityError as e:
            logger.warning(
                f"Database integrity error in {f.__name__}: {str(e)}")
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)

            # MySQL: Duplicate entry / SQLite: UNIQUE constraint failed
            if 'Duplicate entry' in error_msg or 'UNIQUE constraint failed' in error_msg:
                if 'email' in error_msg:
                    message = '该邮箱已被注册'
                elif 'username' in error_msg:
                    message = '该用户名已被使用'
                elif 'phone' in error_msg:
                    message = '该手机号已被注册'
                else:
                    message = '数据重复，请检查输入'
            elif 'FOREIGN KEY constraint failed' in error_msg or 'Cannot add or update a child row' in error_msg:
                message = '数据关联错误，请检查输入'
            else:
                message = '数据验证失败，请检查输入'

            return error(message, 400)

        # 数据库操作异常（兼容MySQL和SQLite）
        except OperationalError as e:
            logger.error(
                f"Database operational error in {f.__name__}: {str(e)}")

            # MySQL特有错误码（SQLite错误码不同，走通用提示）
            if isinstance(e.orig, pymysql.err.OperationalError) and e.orig.args[0] == 1062:  # Duplicate entry
                return error('数据重复，请检查输入', 400)
            elif isinstance(e.orig, pymysql.err.OperationalError) and e.orig.args[0] == 1452:  # Foreign key constraint
                return error('数据关联错误，请检查输入', 400)
            else:
                return error('数据库操作失败，请稍后重试', 500)

        # 表单验证异常
        except ValidationError as e:
            logger.warning(f"Validation error in {f.__name__}: {str(e)}")
            return error(e.message, e.status_code)

        # 值错误异常（通常是参数验证失败）
        except ValueError as e:
            logger.warning(f"Value error in {f.__name__}: {str(e)}")
            return error(f'参数错误: {str(e)}', 400)

        # 键错误异常（缺少必要参数）
        except KeyError as e:
            logger.warning(f"Key error in {f.__name__}: {str(e)}")
            return error(f'缺少必要参数: {str(e)}', 400)

        # 权限错误异常
        except PermissionError as e:
            logger.warning(f"Permission error in {f.__name__}: {str(e)}")
            return error(f'权限不足: {str(e)}', 403)

        # 文件不存在异常
        except FileNotFoundError as e:
            logger.warning(f"File not found in {f.__name__}: {str(e)}")
            return error('文件不存在', 404)

        # 文件系统异常
        except OSError as e:
            logger.error(f"File system error in {f.__name__}: {str(e)}")
            return error('文件系统错误', 500)

        # 其他未知异常
        except Exception as e:
            error_traceback = traceback.format_exc()
            error_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')

            # 记录详细错误日志
            logger.error(
                f"Exception in {f.__name__} [ID: {error_id}]: {str(e)}\n{error_traceback}"
            )

            # 根据应用配置决定是否暴露详细错误信息
            if current_app.config.get('DEBUG', False):
                message = f'系统错误: {str(e)} [错误ID: {error_id}]'
            else:
                message = f'系统内部错误，请稍后重试 [错误ID: {error_id}]'

            return error(message, 500)

    return decorated_function
