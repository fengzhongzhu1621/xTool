from typing import Any, Union


def to_int_or_default(val: Any, default: Any = None) -> Union[int, Any, None]:
    try:
        return int(val)
    except ValueError:
        return default


def make_int(value):
    """将值转换为int类型 ."""
    if value is not None and not isinstance(value, (int, float)):
        return int(value)
    return value
