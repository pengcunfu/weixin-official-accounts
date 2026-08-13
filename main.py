from flask_cors import CORS
from flask import Flask
from app.api import init_api
from app.extensions.database import database
from app.extensions.mail import email_service
from app.extensions.config import config_manager
from app.utils.upload_file import ensure_all_upload_dirs

# 创建Flask应用实例
app = Flask(__name__)

# 启用CORS支持 - 允许所有来源
CORS(app)

# 设置基础应用配置
app.config['SECRET_KEY'] = config_manager.get('app.secret_key')
app.config['MAX_CONTENT_LENGTH'] = config_manager.get(
    'upload.max_content_length')

# 初始化扩展
email_service.init_app(app)

# 数据库一步完成初始化
database.init_app(app)

# 确保上传目录存在
with app.app_context():
    ensure_all_upload_dirs()

# 初始化API模块
init_api(app)

# 运行应用
if __name__ == '__main__':
    # 从配置文件读取运行参数
    app.run(
        debug=config_manager.get('app.debug'),
        host=config_manager.get('app.host'),
        port=config_manager.get('app.port')
    )
