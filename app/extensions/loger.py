import logging
from .config import config_manager

# 全局标志，确保只初始化一次
_logging_initialized = False


def _init_logging():
    """内部初始化日志配置"""
    global _logging_initialized

    if _logging_initialized:
        return

    # 从配置文件读取日志配置
    log_level = config_manager.get('logging.level')
    log_format = config_manager.get('logging.format')

    # 设置日志级别和格式
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # 控制台输出
        ]
    )

    # 获取根日志记录器
    logger = logging.getLogger()

    # 可以添加文件处理器（可选）
    file_handler_config = config_manager.get('logging.file')
    if file_handler_config.get('enabled'):
        filename = file_handler_config.get('filename')
        max_bytes = file_handler_config.get('max_bytes')
        backup_count = file_handler_config.get('backup_count')

        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            filename=filename,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)

    logger.info("Logging initialized successfully")
    _logging_initialized = True


def get_logger(name=None):
    """获取日志记录器，首次调用时自动初始化日志系统"""
    # 确保日志系统已初始化
    _init_logging()
    return logging.getLogger(name) if name else logging.getLogger()
