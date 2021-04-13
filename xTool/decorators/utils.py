# -*- coding: utf-8 -*-

import functools


class CallableContextManager(object):
    """将上下文管理器转换为装饰器 ."""
    def __call__(self, fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)
        return inner


def safe_wraps(wrapper, *args, **kwargs):
    """Safely wraps partial functions."""
    while isinstance(wrapper, functools.partial):
        wrapper = wrapper.func
    return functools.wraps(wrapper, *args, **kwargs)
