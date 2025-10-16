import traceback

from django.conf import settings
from django.utils.module_loading import import_string

__all__ = ["incr_expireat", "exists"]

__BACKEND = None

if not __BACKEND:
    try:
        backend_cls = import_string(settings.DATA_BACKEND)
        __BACKEND = backend_cls()
    except ImportError as e:
        raise ImportError(
            'data backend({}) import error with exception: {}'.format(settings.DATA_BACKEND, traceback.format_exc(e))
        )


def exists(key: str) -> bool:
    """判断指定缓存是否存在 ."""
    return __BACKEND.exists(key)


def incr_expireat(name, amount=1, when=None):
    """缓存的值自增，且支持添加过期时间 ."""
    return __BACKEND.incr_expireat(name, amount, when)
