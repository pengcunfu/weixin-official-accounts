from app.extensions.database import db
from datetime import datetime
import json
from typing import Dict, Any, List, Union, Optional


class BaseModel(db.Model):
    """
    模型基类，提供通用功能
    
    包含：
    - JSON字段处理方法
    - 软删除功能
    - 通用的to_dict方法
    - 时间字段处理
    """
    __abstract__ = True

    # 通用时间字段
    created_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_time = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    deleted_time = db.Column(db.DateTime, nullable=True, comment='删除时间（软删除）')

    def _set_json_field(self, field_name: str, data: Union[List, Dict, None]) -> None:
        """
        通用的JSON字段设置方法
        
        Args:
            field_name: 字段名称
            data: 要设置的数据，None表示清空
        """
        if data is None:
            setattr(self, field_name, None)
        else:
            setattr(self, field_name, json.dumps(data, ensure_ascii=False))

    def _get_json_field(self, field_name: str) -> Union[List, Dict, None]:
        """
        通用的JSON字段获取方法
        
        Args:
            field_name: 字段名称
            
        Returns:
            解析后的数据，解析失败返回None
        """
        field_value = getattr(self, field_name, None)
        if not field_value:
            return None
            
        try:
            return json.loads(field_value) if isinstance(field_value, str) else field_value
        except (json.JSONDecodeError, TypeError):
            return None

    def soft_delete(self) -> None:
        """软删除记录，设置删除时间"""
        self.deleted_time = datetime.now()
        db.session.commit()

    @classmethod
    def get_active(cls):
        """获取所有未被软删除的记录"""
        return cls.query.filter_by(deleted_time=None)

    @property
    def is_deleted(self) -> bool:
        """判断记录是否已被删除"""
        return self.deleted_time is not None

    def _format_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """
        格式化日期时间为字符串
        
        Args:
            dt: 日期时间对象
            
        Returns:
            格式化后的日期时间字符串，如果为None则返回None
        """
        return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None

    def to_dict(self) -> Dict[str, Any]:
        """
        将模型实例转换为字典，子类应该重写此方法
        
        Returns:
            包含基本字段的字典
        """
        return {
            'id': getattr(self, 'id', None),
            'created_time': self._format_datetime(self.created_time),
            'updated_time': self._format_datetime(self.updated_time),
            'deleted_time': self._format_datetime(self.deleted_time),
        }

    def update_from_dict(self, data: Dict[str, Any], exclude_fields: Optional[List[str]] = None) -> None:
        """
        从字典更新模型字段
        
        Args:
            data: 包含更新数据的字典
            exclude_fields: 要排除的字段列表
        """
        if exclude_fields is None:
            exclude_fields = ['id', 'created_time', 'deleted_time']
            
        for key, value in data.items():
            if key not in exclude_fields and hasattr(self, key):
                setattr(self, key, value)
                
        self.updated_time = datetime.now()
