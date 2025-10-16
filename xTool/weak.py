import weakref
from contextlib import suppress
from math import ceil


def proxy(obj):
    """weakref.proxy的参数可以为proxy对象 ."""
    if isinstance(obj, weakref.ProxyType):
        return weakref.proxy(obj.__repr__.__self__)
    else:
        return weakref.proxy(obj)


def _weakref_handle(info):  # type: ignore
    ref, name = info
    # 如果弱引用的对象被回收，返回None
    ob = ref()
    if ob is not None:
        # 忽略异常
        with suppress(Exception):
            getattr(ob, name)()


def weakref_handle(ob, name, timeout, loop, ceil_timeout=True):  # type: ignore
    """延迟执行对象的方法 ."""
    if timeout is not None and timeout > 0:
        when = loop.time() + timeout
        if ceil_timeout:
            when = ceil(when)

        return loop.call_at(when, _weakref_handle, (weakref.ref(ob), name))
