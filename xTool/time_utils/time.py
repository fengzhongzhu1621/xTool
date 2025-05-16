from datetime import timedelta

from dateutil import parser

from xTool.type_hint import time_unit_type


def to_seconds(time_unit: time_unit_type) -> float:
    """转换为秒数 ."""
    return float(time_unit.total_seconds() if isinstance(time_unit, timedelta) else time_unit)


def has_timezone(time_str: str) -> bool:
    """判断时间字符串是否包含时区 ."""
    try:
        dt = parser.parse(time_str)
        return dt.tzinfo is not None
    except (ValueError, OverflowError):
        return False
