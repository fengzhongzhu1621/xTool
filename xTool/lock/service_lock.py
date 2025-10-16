import functools
import time
from typing import Optional

from xTool.cache.cachetools import hash_key, typed_key
from xTool.codec import md5


class ShareLockError(Exception):

    pass


def share_lock(
    cache: object,
    ttl: int = 600,
    identify: Optional[str] = None,
    hash_param: bool = False,
    typed: bool = False,
    key_prefix="share_lock",
):
    def wrapper(func):
        @functools.wraps(func)
        def _inner(*args, **kwargs):
            if identify:
                cache_key = identify
            elif hash_param:
                key = typed_key if typed else hash_key
                cache_key = md5(str(key(*args, **kwargs)))
            else:
                # 注意：可能存在多个模块下有重名的函数
                cache_key = f"{key_prefix}:{func.__module__}:{func.__name__}"
            cache_key = str(cache_key)
            func._cache_key = cache_key
            token = str(time.time())
            lock_success = cache.set(cache_key, token, ex=ttl, nx=True)
            # 在ttl时间范围内加锁失败，则终止任务执行，保证任务的唯一性
            if not lock_success:
                return ShareLockError()

            try:
                return func(*args, **kwargs)
            finally:
                # 任务执行完毕后解锁
                if cache.get(cache_key) == token:
                    # 解锁失败会导致同时间的另一个任务在ttl内卡死
                    cache.delete(cache_key)

        return _inner

    return wrapper
