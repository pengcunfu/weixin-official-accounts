from flask import send_from_directory


def register_blueprints(app):
    """注册所有API蓝图"""
    from .auth import auth_bp
    from .public_account import public_account_bp
    from .article import article_bp
    from .user import user_bp
    from .profile import profile_bp
    from .upload import upload_bp
    from .dashboard import dashboard_bp

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(public_account_bp)
    app.register_blueprint(article_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(dashboard_bp)


def register_routes(app):
    """注册全局路由"""

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """静态文件服务 - 提供上传文件的访问"""
        uploads_folder = 'uploads'
        return send_from_directory(uploads_folder, filename)


def init_api(app):
    """初始化API模块"""
    register_blueprints(app)
    register_routes(app)
