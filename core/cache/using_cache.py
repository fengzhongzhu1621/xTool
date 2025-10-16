import functools

from core.constants import TimeEnum

from .cache_key import CacheKeyTemplate


def using_method_cache(key_template: str, duration: TimeEnum, need_md5=False):
    def decorator(func):
        @functools.wraps(func)
        def inner(self, *args, **kwargs):
            # 获得缓存key
            cache = CacheKeyTemplate(key_template, need_md5)

            # 获得缓冲的结果
            cache_result = cache.get()
            if cache_result is not None:
                return cache_result

            # 缓冲结果
            result = func(self, *args, **kwargs)
            if result:
                cache.set(result, duration)
            return result

        return inner

    return decorator


def using_cache(key_template: str, duration: TimeEnum, need_md5=False):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            # 获得缓存key
            cache = CacheKeyTemplate(key_template, need_md5, *args, **kwargs)

            # 获得缓冲的结果
            cache_result = cache.get()
            if cache_result is not None:
                return cache_result

            # 缓冲结果
            result = func(*args, **kwargs)
            if result:
                cache.set(result, duration)
            return result

        return inner

    return decorator


cache_half_minute = functools.partial(using_cache, duration=TimeEnum.HALF_MINUTE_SECOND)
cache_one_minute = functools.partial(using_cache, duration=TimeEnum.ONE_MINUTE_SECOND)
cache_five_minute = functools.partial(using_cache, duration=TimeEnum.FIVE_MINUTE_SECOND)
cache_ten_minute = functools.partial(using_cache, duration=TimeEnum.TEN_MINUTE_SECOND)
cache_one_hour = functools.partial(using_cache, duration=TimeEnum.ONE_HOUR_SECOND)
cache_one_day = functools.partial(using_cache, duration=TimeEnum.ONE_DAY_SECOND)


cache_method_half_minute = functools.partial(using_method_cache, duration=TimeEnum.HALF_MINUTE_SECOND)
cache_method_one_minute = functools.partial(using_method_cache, duration=TimeEnum.ONE_MINUTE_SECOND)
cache_method_five_minute = functools.partial(using_method_cache, duration=TimeEnum.FIVE_MINUTE_SECOND)
cache_method_ten_minute = functools.partial(using_method_cache, duration=TimeEnum.TEN_MINUTE_SECOND)
cache_method_one_hour = functools.partial(using_method_cache, duration=TimeEnum.ONE_HOUR_SECOND)
cache_method_one_day = functools.partial(using_method_cache, duration=TimeEnum.ONE_DAY_SECOND)
