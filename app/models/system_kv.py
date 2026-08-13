from app.extensions.database import db
from datetime import datetime


class SystemKV(db.Model):
    """通用键值存储表（替代Redis，用于Token、验证码、缓存）"""

    __tablename__ = 'system_kv'

    id = db.Column(db.Integer, primary_key=True, comment='主键')
    key = db.Column(db.String(255), unique=True, nullable=False,
                    index=True, comment='存储键')
    value = db.Column(db.Text, nullable=True, comment='存储值（JSON序列化）')
    expire_time = db.Column(db.DateTime, nullable=True,
                            comment='过期时间，None表示永不过期')
    created_time = db.Column(
        db.DateTime, default=datetime.now, comment='创建时间')
    updated_time = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f'<SystemKV {self.key}>'
