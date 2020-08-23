# -*- coding: utf-8 -*-

import weakref
from contextlib import suppress
from math import ceil


def _weakref_handle(info):  # type: ignore
    ref, name = info
    ob = ref()
    if ob is not None:
        with suppress(Exception):
            getattr(ob, name)()


def weakref_handle(ob, name, timeout, loop, ceil_timeout=True):  # type: ignore
    """延迟执行对象的方法 ."""
    if timeout is not None and timeout > 0:
        when = loop.time() + timeout
        if ceil_timeout:
            when = ceil(when)

        return loop.call_at(when, _weakref_handle, (weakref.ref(ob), name))
