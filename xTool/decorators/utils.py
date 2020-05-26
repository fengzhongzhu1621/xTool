# -*- coding: utf-8 -*-

from functools import wraps


class _callable_context_manager(object):
    """将类转换为装饰器 ."""
    def __call__(self, fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)
        return inner
