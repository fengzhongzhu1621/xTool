from typing import Optional

from django.conf import settings

from xTool.cache import Cache
from xTool.lock import share_lock as _share_lock


def share_lock(
    ttl: int = 600,
    identify: Optional[str] = None,
    hash_param: bool = False,
    typed: bool = False,
    key_prefix="share_lock",
):
    def wrapper(func):
        cache = Cache(connection_conf=settings.REDIS_CELERY_CONF)
        return _share_lock(cache, ttl, identify, hash_param, typed, key_prefix)(func)

    return wrapper
