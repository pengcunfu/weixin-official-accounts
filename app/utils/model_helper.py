from datetime import datetime
from typing import Any, Optional
from flask_wtf import FlaskForm


def update_model_fields(model: Any, form: FlaskForm, exclude_fields: Optional[list] = None,
                        auto_update_time: bool = True) -> None:
    """
    通用模型更新函数，自动遍历表单字段并更新模型属性

    Args:
        model: 要更新的模型实例
        form: 验证后的表单实例
        exclude_fields: 要排除的字段列表，默认为None
        auto_update_time: 是否自动更新update_time字段，默认为True
    """
    if exclude_fields is None:
        exclude_fields = []

    # 遍历表单的所有字段
    for field_name, field in form._fields.items():
        # 跳过排除的字段
        if field_name in exclude_fields:
            continue

        # 检查模型是否有该属性
        if hasattr(model, field_name):
            field_value = field.data

            # 只有当字段有值时才更新（避免None值覆盖现有数据）
            if field_value is not None:
                # 对于字符串类型，还要检查是否为空字符串
                if isinstance(field_value, str) and field_value.strip() == '':
                    continue

                # 更新模型属性
                setattr(model, field_name, field_value)

    # 自动更新时间戳
    if auto_update_time and hasattr(model, 'update_time'):
        model.update_time = datetime.utcnow()


def update_model_from_dict(model: Any, data: dict, exclude_fields: Optional[list] = None,
                           auto_update_time: bool = True) -> None:
    """
    通用模型更新函数，从字典数据更新模型属性

    Args:
        model: 要更新的模型实例
        data: 包含更新数据的字典
        exclude_fields: 要排除的字段列表，默认为None
        auto_update_time: 是否自动更新update_time字段，默认为True
    """
    if exclude_fields is None:
        exclude_fields = []

    for field_name, field_value in data.items():
        # 跳过排除的字段
        if field_name in exclude_fields:
            continue

        # 检查模型是否有该属性
        if hasattr(model, field_name):
            # 只有当字段有值时才更新
            if field_value is not None:
                # 对于字符串类型，还要检查是否为空字符串
                if isinstance(field_value, str) and field_value.strip() == '':
                    continue

                # 更新模型属性
                setattr(model, field_name, field_value)

    # 自动更新时间戳
    if auto_update_time and hasattr(model, 'update_time'):
        model.update_time = datetime.utcnow()


def create_model_from_form(model_class: type, form: FlaskForm, exclude_fields: Optional[list] = None,
                           **extra_fields) -> Any:
    """
    从表单创建模型实例

    Args:
        model_class: 模型类
        form: 验证后的表单实例
        exclude_fields: 要排除的字段列表，默认为None
        **extra_fields: 额外的字段值

    Returns:
        创建的模型实例
    """
    if exclude_fields is None:
        exclude_fields = []

    # 从表单提取数据
    model_data = {}
    for field_name, field in form._fields.items():
        if field_name not in exclude_fields and field.data is not None:
            model_data[field_name] = field.data

    # 添加额外字段
    model_data.update(extra_fields)

    # 创建模型实例
    return model_class(**model_data)
