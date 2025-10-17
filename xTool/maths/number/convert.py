import decimal
from typing import Any, Union

# create a new context for this task
ctx = decimal.Context()

# 20 digits should be enough for everyone :D
ctx.prec = 20


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


def safe_int(int_str, dft=0):
    try:
        int_val = int(int_str)
    except Exception:  # noqa
        try:
            int_val = int(float(int_str))
        except Exception:  # noqa
            int_val = dft
    return int_val


def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return float("nan")


def float_to_str(f):
    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    d1 = ctx.create_decimal(repr(f))
    return format(d1, "f")
