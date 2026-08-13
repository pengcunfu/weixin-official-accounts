from flask_mail import Mail, Message
import random
import string
from flask import render_template_string
from .loger import get_logger
from .config import config_manager

# 保持全局Mail对象
mail = Mail()


class EmailService:
    """邮件服务类"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self._app_initialized = False

    def configure_mail(self, app):
        """配置邮件参数"""
        # 邮件配置
        app.config['MAIL_SERVER'] = config_manager.get('mail.server')
        app.config['MAIL_PORT'] = config_manager.get('mail.port')
        app.config['MAIL_USE_TLS'] = config_manager.get('mail.use_tls')
        app.config['MAIL_USE_SSL'] = config_manager.get('mail.use_ssl')
        app.config['MAIL_USERNAME'] = config_manager.get('mail.username')
        app.config['MAIL_PASSWORD'] = config_manager.get('mail.password')
        app.config['MAIL_DEFAULT_SENDER'] = config_manager.get('mail.default_sender')
        app.config['MAIL_MAX_EMAILS'] = config_manager.get('mail.max_emails')

    def init_app(self, app):
        """初始化邮件扩展"""
        if self._app_initialized:
            return mail

        # 配置邮件参数
        self.configure_mail(app)

        # 初始化邮件扩展
        mail.init_app(app)

        self._app_initialized = True
        self.logger.info(
            f"邮件服务初始化成功: 服务器={config_manager.get('mail.server')}, 端口={config_manager.get('mail.port')}")
        return mail

    def get_mail_instance(self):
        """获取邮件实例"""
        return mail

    def generate_verification_code(self):
        """生成6位数字验证码"""
        return ''.join(random.choices(string.digits, k=6))

    def send_verification_code(self, email, code_type='register'):
        """发送验证码邮件"""
        try:
            # 导入验证码管理器
            from app.extensions.storage import verification_code_manager

            # 检查是否最近已发送验证码（防止频繁发送）
            if verification_code_manager.is_code_sent_recently(email, code_type, interval=60):
                return {'success': False, 'message': '验证码发送过于频繁，请稍后再试'}

            # 生成验证码
            code = self.generate_verification_code()

            # 存储验证码到数据库
            success = verification_code_manager.store_code(email, code, code_type)

            if not success:
                return {'success': False, 'message': '验证码存储失败，请稍后重试'}

            # 发送邮件
            email_success = self._send_email(email, code, code_type)

            if email_success:
                self.logger.info(f"验证码发送成功: {email}, 类型={code_type}")
                return {'success': True, 'message': '验证码发送成功', 'code': code}
            else:
                # 发送失败，删除验证码记录
                verification_code_manager.delete_code(email, code_type)
                self.logger.error(f"邮件发送失败: {email}, 类型={code_type}")
                return {'success': False, 'message': '邮件发送失败，请稍后重试'}

        except Exception as e:
            self.logger.error(f'发送验证码失败: {str(e)}')
            return {'success': False, 'message': '系统错误，请稍后重试'}

    def _send_email(self, email, code, code_type):
        """发送邮件"""
        try:
            # 根据类型确定邮件主题和内容
            if code_type == 'register':
                subject = '【公众号发文助手】注册验证码'
                template = self._get_register_template(code)
            elif code_type == 'reset_password':
                subject = '【公众号发文助手】密码重置验证码'
                template = self._get_reset_password_template(code)
            else:
                subject = '【公众号发文助手】验证码'
                template = self._get_default_template(code)

            # 创建邮件消息
            msg = Message(
                subject=subject,
                recipients=[email],
                html=template,
                sender=config_manager.get('mail.default_sender')
            )

            # 发送邮件
            mail.send(msg)
            return True

        except Exception as e:
            self.logger.error(f'邮件发送异常: {str(e)}')
            return False

    def _get_register_template(self, code):
        """获取注册验证码邮件模板"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>注册验证码</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
                .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }
                .code-box { background: white; border: 2px dashed #007bff; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }
                .code { font-size: 32px; font-weight: bold; color: #007bff; letter-spacing: 5px; }
                .footer { text-align: center; margin-top: 20px; color: #6c757d; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h2>欢迎注册公众号发文助手！</h2>
                    <p>您正在注册公众号发文助手账户，您的验证码是：</p>
                    <div class="code-box">
                        <div class="code">{{ code }}</div>
                    </div>
                    <p><strong>温馨提示：</strong></p>
                    <ul>
                        <li>验证码有效期为10分钟，请及时使用</li>
                        <li>为了您的账户安全，请勿将验证码泄露给他人</li>
                        <li>如果您没有进行此操作，请忽略此邮件</li>
                    </ul>
                    <div class="footer">
                        <p>此邮件由系统自动发送，请勿回复</p>
                        <p>© 2025 公众号发文助手. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return render_template_string(template, code=code)

    def _get_reset_password_template(self, code):
        """获取密码重置验证码邮件模板"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>密码重置验证码</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
                .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }
                .code-box { background: white; border: 2px dashed #dc3545; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }
                .code { font-size: 32px; font-weight: bold; color: #dc3545; letter-spacing: 5px; }
                .footer { text-align: center; margin-top: 20px; color: #6c757d; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h2>密码重置验证</h2>
                    <p>您正在重置公众号发文助手账户密码，您的验证码是：</p>
                    <div class="code-box">
                        <div class="code">{{ code }}</div>
                    </div>
                    <p><strong>安全提醒：</strong></p>
                    <ul>
                        <li>验证码有效期为10分钟，请及时使用</li>
                        <li>为了您的账户安全，请勿将验证码泄露给他人</li>
                        <li>如果您没有进行此操作，请立即联系客服</li>
                    </ul>
                    <div class="footer">
                        <p>此邮件由系统自动发送，请勿回复</p>
                        <p>© 2025 公众号发文助手. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return render_template_string(template, code=code)

    def _get_default_template(self, code):
        """获取默认验证码邮件模板"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>验证码</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
                .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }
                .code-box { background: white; border: 2px dashed #28a745; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }
                .code { font-size: 32px; font-weight: bold; color: #28a745; letter-spacing: 5px; }
                .footer { text-align: center; margin-top: 20px; color: #6c757d; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h2>身份验证</h2>
                    <p>您的验证码是：</p>
                    <div class="code-box">
                        <div class="code">{{ code }}</div>
                    </div>
                    <p><strong>温馨提示：</strong></p>
                    <ul>
                        <li>验证码有效期为10分钟，请及时使用</li>
                        <li>为了您的账户安全，请勿将验证码泄露给他人</li>
                        <li>如果您没有进行此操作，请忽略此邮件</li>
                    </ul>
                    <div class="footer">
                        <p>此邮件由系统自动发送，请勿回复</p>
                        <p>© 2025 公众号发文助手. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return render_template_string(template, code=code)

    def verify_code(self, email, code, code_type='register'):
        """验证验证码"""
        try:
            # 导入验证码管理器
            from app.extensions.storage import verification_code_manager

            # 使用验证码管理器验证验证码
            is_valid, message = verification_code_manager.verify_code(email, code, code_type)

            return {'success': is_valid, 'message': message}

        except Exception as e:
            self.logger.error(f'验证码验证失败: {str(e)}')
            return {'success': False, 'message': '系统错误，请稍后重试'}

    def get_code_ttl(self, email, code_type='register'):
        """获取验证码剩余有效时间"""
        try:
            from app.extensions.storage import verification_code_manager
            ttl = verification_code_manager.get_code_ttl(email, code_type)
            return {'success': True, 'ttl': ttl}
        except Exception as e:
            self.logger.error(f'获取验证码TTL失败: {str(e)}')
            return {'success': False, 'message': '系统错误'}

    def get_code_status(self, email, code_type='register'):
        """获取验证码状态信息"""
        try:
            from app.extensions.storage import verification_code_manager
            info = verification_code_manager.get_code_info(email, code_type)

            if not info:
                return {'success': False, 'message': '未找到验证码'}

            return {
                'success': True,
                'data': {
                    'email': info['email'],
                    'type': info['type'],
                    'created_time': info['created_time'],
                    'attempts': info['attempts'],
                    'ttl': info['ttl']
                }
            }
        except Exception as e:
            self.logger.error(f'获取验证码状态失败: {str(e)}')
            return {'success': False, 'message': '系统错误'}

    def cancel_verification_code(self, email, code_type='register'):
        """取消验证码（删除验证码）"""
        try:
            from app.extensions.storage import verification_code_manager
            success = verification_code_manager.delete_code(email, code_type)

            if success:
                return {'success': True, 'message': '验证码已取消'}
            else:
                return {'success': False, 'message': '验证码取消失败'}

        except Exception as e:
            self.logger.error(f'取消验证码失败: {str(e)}')
            return {'success': False, 'message': '系统错误'}


# 创建邮件服务实例
email_service = EmailService()
