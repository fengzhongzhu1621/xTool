from datetime import datetime
from typing import Any, Set

from django.db.models import Model
from django.utils import timezone

from core.utils import from_iso_format


def get_model_value(model: Model, field: str, datetime_fields: Set) -> Any:
    """获得模型的值 ."""
    # 获得模型中字段的值
    value = getattr(model, field)
    # 如果同步的是datetime类型的字段，转换为本地时区的时间字符串
    if datetime_fields and value and field in datetime_fields:
        if isinstance(value, str):
            value = from_iso_format(value)
        if isinstance(value, datetime):
            current_timezone = timezone.get_current_timezone()
            value_at_current_timezone = value.astimezone(current_timezone)
            value = timezone.make_naive(value_at_current_timezone).strftime("%Y-%m-%dT%H:%M:%S")

    return value
