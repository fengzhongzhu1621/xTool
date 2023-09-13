import functools
import json

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder

from apps.core.constants import TimeEnum
from xTool.misc import md5 as md5_sum
from xTool.log import logger


def using_cache(key: str, duration, need_md5=False):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            # 获得缓存key
            try:
                actual_key = key.format(*args, **kwargs)
            except (IndexError, KeyError):
                actual_key = key
            logger.debug(
                f"[using cache] build key => [{actual_key}] duration => [{duration}]"
            )
            if need_md5:
                actual_key = md5_sum(actual_key)

            # 获得缓冲的结果
            cache_result = cache.get(actual_key)
            if cache_result:
                return json.loads(cache_result)

            # 缓冲结果
            result = func(*args, **kwargs)
            if result:
                cache.set(
                    actual_key, json.dumps(result, cls=DjangoJSONEncoder), duration
                )
            return result

        return inner

    return decorator


cache_half_minute = functools.partial(
    using_cache, duration=0.5 * TimeEnum.ONE_MINUTE_SECOND.value
)
cache_one_minute = functools.partial(
    using_cache, duration=TimeEnum.ONE_MINUTE_SECOND.value
)
cache_five_minute = functools.partial(
    using_cache, duration=5 * TimeEnum.ONE_MINUTE_SECOND.value
)
cache_ten_minute = functools.partial(
    using_cache, duration=10 * TimeEnum.ONE_MINUTE_SECOND.value
)
cache_one_hour = functools.partial(using_cache, duration=TimeEnum.ONE_HOUR_SECOND.value)
cache_one_day = functools.partial(using_cache, duration=TimeEnum.ONE_DAY_SECOND.value)
