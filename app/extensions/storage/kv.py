import json
from datetime import datetime, timedelta
from typing import Any, Optional

from app.extensions.database import db
from app.models.system_kv import SystemKV


class KVStore:
    """基于SQLite的通用键值存储（替代Redis）"""

    def set(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        """设置键值，可选过期时间（秒），返回是否成功"""
        try:
            serialized = json.dumps(value, ensure_ascii=False, default=str)
            expire_time = None
            if expire_seconds:
                expire_time = datetime.now() + timedelta(seconds=expire_seconds)

            record = SystemKV.query.filter_by(key=key).first()
            if record:
                record.value = serialized
                record.expire_time = expire_time
                record.updated_time = datetime.now()
            else:
                record = SystemKV(
                    key=key, value=serialized, expire_time=expire_time)
                db.session.add(record)

            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    def get(self, key: str) -> Optional[Any]:
        """获取键值，不存在或已过期返回None"""
        record = SystemKV.query.filter_by(key=key).first()
        if not record:
            return None

        if record.expire_time and record.expire_time <= datetime.now():
            db.session.delete(record)
            db.session.commit()
            return None

        try:
            return json.loads(record.value) if record.value is not None else None
        except (json.JSONDecodeError, TypeError):
            return record.value

    def delete(self, key: str) -> bool:
        """删除键值，不存在返回False"""
        record = SystemKV.query.filter_by(key=key).first()
        if not record:
            return False

        db.session.delete(record)
        db.session.commit()
        return True

    def exists(self, key: str) -> bool:
        """检查键是否存在且未过期"""
        record = SystemKV.query.filter_by(key=key).first()
        if not record:
            return False

        if record.expire_time and record.expire_time <= datetime.now():
            db.session.delete(record)
            db.session.commit()
            return False

        return True

    def expire(self, key: str, seconds: int) -> bool:
        """设置键的过期时间（秒），不存在返回False"""
        record = SystemKV.query.filter_by(key=key).first()
        if not record:
            return False

        record.expire_time = datetime.now() + timedelta(seconds=seconds)
        db.session.commit()
        return True

    def ttl(self, key: str) -> int:
        """获取键剩余有效时间（秒），不存在或已过期返回0"""
        record = SystemKV.query.filter_by(key=key).first()
        if not record or not record.expire_time:
            return 0

        remaining = (record.expire_time - datetime.now()).total_seconds()
        return int(remaining) if remaining > 0 else 0

    def cleanup_expired(self) -> int:
        """清理所有已过期的记录，返回清理数量"""
        now = datetime.now()
        expired_records = SystemKV.query.filter(
            SystemKV.expire_time.isnot(None),
            SystemKV.expire_time <= now
        ).all()

        count = len(expired_records)
        for record in expired_records:
            db.session.delete(record)

        if count:
            db.session.commit()

        return count


kv_store = KVStore()
