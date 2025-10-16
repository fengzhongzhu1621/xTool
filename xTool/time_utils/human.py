import datetime
from typing import Union

__all__ = [
    "countdown2str",
]


def countdown2str(countdown: Union[int, datetime.timedelta]) -> str:
    """
    自定义倒计时时间的格式化，格式为类似: 1day, 5h32m45s
    :param countdown: 倒计时，单位为s(即unix时间戳)
    """

    if isinstance(countdown, datetime.timedelta):
        countdown = int(countdown.total_seconds())

    time_unit_list = [("day, ", 24 * 60 * 60), ("h", 60 * 60), ("m", 60), ("s", 1)]
    countdown_format_str = []
    for unit in time_unit_list:
        unit_value = int(countdown // unit[1])
        countdown = countdown % unit[1]
        if unit_value:
            countdown_format_str.append(f"{unit_value}{unit[0]}")

    return "".join(countdown_format_str)
