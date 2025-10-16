import time
from datetime import timedelta

import arrow
from django.conf import settings

from apps.backend.data.api import exists, incr_expireat
from apps.logger import logger

__all__ = [
    "generate_random_sequence",
]


def generate_random_sequence(key: str, prefix: str = "", pad: int = 6) -> str:
    """生成随机串 ."""
    # 定义缓存 key
    if prefix:
        key = f"{prefix}:{key}"
    when = None
    # 当前时间，支持国际化
    now_time = arrow.now()
    # 重试次数
    repeat_times = settings.RANDOM_STR_GENERATE_REPEAT_TIMES
    err = None
    random_str = ""
    for _ in range(repeat_times):
        try:
            # 计算缓存过期时间
            if not exists(key):
                # 设置第二天的0:00:00过期
                when = arrow.Arrow(now_time.year, now_time.month, now_time.day) + timedelta(days=1)
                when = int(when.timestamp())

            # 值自增 1
            num = incr_expireat(key, when=when)

            # 0填充
            random_str = now_time.to(settings.TIME_ZONE).strftime("%Y%m%d%H%M%S") + f"{{:0>{pad}}}".format(num)
            err = None
            break
        except Exception as exc_info:  # pylint: disable=broad-except
            logger.exception(exc_info)
            err = exc_info
            time.sleep(0.1)

    if err:
        raise Exception("generate_random_sequence(%s, %s) %s", key, prefix, str)

    return random_str
