from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import bcrypt
from .loger import get_logger
from .config import config_manager

# 初始化数据库扩展对象 - 保持全局
db = SQLAlchemy()
migrate = Migrate()


class Database:
    """数据库管理类"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self._db_initialized = False
        self._app_initialized = False

    def configure_database(self, app):
        """配置数据库连接参数（支持SQLite和MySQL）"""
        db_type = config_manager.get('database.type', 'sqlite')

        if db_type == 'sqlite':
            self._configure_sqlite(app)
        elif db_type == 'mysql':
            self._configure_mysql(app)
        else:
            raise ValueError(f'不支持的数据库类型: {db_type}，仅支持 sqlite 或 mysql')

    def _configure_sqlite(self, app):
        """配置SQLite数据库连接"""
        # 环境变量优先，默认使用config.yaml中的路径
        db_path = os.environ.get('SQLITE_PATH', config_manager.get('database.path'))
        if not db_path:
            raise ValueError('SQLite数据库路径未配置，请检查config.yaml文件中的database.path')

        # 转换为绝对路径并确保目录存在
        db_path = os.path.abspath(db_path)
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        # Windows路径统一使用正斜杠，避免URI解析问题
        sqlite_uri = f"sqlite:///{db_path.replace(os.sep, '/')}"

        self.logger.info(f"数据库连接配置: type=sqlite, path={db_path}")
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config_manager.get('database.track_modifications')

        # SQLite允许跨线程访问（Flask多线程环境）
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {'check_same_thread': False}
        }

    def _configure_mysql(self, app):
        """配置MySQL数据库连接（环境变量优先）"""
        host = os.environ.get('MYSQL_HOST', config_manager.get('database.host'))
        port = int(os.environ.get('MYSQL_PORT', config_manager.get('database.port')))
        username = os.environ.get('MYSQL_USER', config_manager.get('database.username'))
        password = os.environ.get('MYSQL_PASSWORD', config_manager.get('database.password'))
        database_name = os.environ.get('MYSQL_DATABASE', config_manager.get('database.database'))
        charset = config_manager.get('database.charset', 'utf8mb4')

        self.logger.info(
            f"数据库连接配置: type=mysql, host={host}, port={port}, username={username}, database={database_name}")

        if not host or not username or not database_name:
            raise ValueError('MySQL数据库配置不完整，请检查config.yaml文件中的database配置')

        app.config[
            'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}?charset={charset}"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config_manager.get('database.track_modifications')

        # 连接池配置
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': config_manager.get('database.pool_size', 10),
            'pool_recycle': config_manager.get('database.pool_recycle', 3600),
            'pool_pre_ping': config_manager.get('database.pool_pre_ping', True),
            'pool_timeout': config_manager.get('database.pool_timeout', 30),
            'max_overflow': config_manager.get('database.max_overflow', 20),
            'connect_args': config_manager.get('database.connect_args', {})
        }

    def init_database_schema(self, app):
        """内部函数：在应用上下文中初始化数据库"""
        if self._db_initialized:
            return

        try:
            with app.app_context():
                # 导入所有模型以确保它们被注册
                from app.models.user import User
                from app.models.public_account import PublicAccount
                from app.models.article import Article
                from app.models.system_kv import SystemKV

                # 确保数据库表存在
                db.create_all()
                self.logger.info('数据库表创建/验证成功')

                # 初始化迁移
                if not os.path.exists('migrations'):
                    self.logger.info('正在初始化数据库迁移...')
                    from flask_migrate import init, migrate, upgrade
                    init()
                    migrate(message='Initial migration')
                    upgrade()
                    self.logger.info('数据库迁移初始化并应用成功')
                else:
                    self.logger.info('正在应用待处理的数据库迁移...')
                    from flask_migrate import upgrade
                    upgrade()
                    self.logger.info('数据库迁移已是最新状态')

                # 创建默认管理员账号
                self.create_default_admin()

                self._db_initialized = True

        except Exception as e:
            self.logger.error(f'数据库初始化错误: {str(e)}')
            raise

    def init_app(self, app):
        """初始化数据库扩展和配置"""
        if self._app_initialized:
            return db

        # 配置数据库连接
        self.configure_database(app)

        # 初始化Flask扩展
        db.init_app(app)
        migrate.init_app(app, db)

        # 自动执行数据库初始化
        self.init_database_schema(app)

        # 检查数据库连接
        self.check_database_connection(app)

        self._app_initialized = True
        return db

    def create_default_admin(self):
        """创建默认管理员账号"""
        try:
            from app.models.user import User

            # 获取配置中的管理员信息
            admin_username = config_manager.get('admin.username')
            admin_password = config_manager.get('admin.password')
            admin_email = config_manager.get('admin.email')
            admin_nickname = config_manager.get('admin.nickname')

            # 检查管理员账号是否已存在
            existing_admin = User.query.filter(
                (User.username == admin_username) | (User.email == admin_email)
            ).first()

            if existing_admin:
                self.logger.info(f'管理员账号已存在: {existing_admin.username}')
                return

            # 创建管理员账号
            # 密码加密
            password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            admin_user = User(
                username=admin_username,
                email=admin_email,
                password=password_hash,
                nickname=admin_nickname,
                phone='',
                is_main=True,  # 设置为主管理员
                bind_limit=999,  # 给予足够的绑定限制
                bound_accounts=0,
                status='active',
                login_count=0
            )

            db.session.add(admin_user)
            db.session.commit()

            self.logger.info(f'默认管理员账号创建成功: {admin_username}')
            self.logger.info(f'管理员登录信息 - 用户名: {admin_username}, 密码: {admin_password}')

        except Exception as e:
            self.logger.error(f'创建默认管理员账号失败: {str(e)}')
            db.session.rollback()
            raise

    def check_database_connection(self, app):
        """检查数据库连接"""
        try:
            with app.app_context():
                db.session.execute(db.text('SELECT 1'))
            self.logger.info("数据库连接建立成功")
        except Exception as e:
            self.logger.error(f"数据库连接失败: {e}")
            raise RuntimeError(f"数据库连接失败，请检查配置: {e}")

    def setup_database(self, app):
        """设置数据库 - 一步完成所有初始化"""
        return self.init_app(app)


# 创建数据库实例
database = Database()
