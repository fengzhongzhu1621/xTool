import functools
import inspect
from typing import Callable

import six

from xTool.type_hint import F

if six.PY34:
    import asyncio  # pylint: disable=import-error,g-import-not-at-top  # pytype: disable=import-error

# Python 3.12 deprecates asyncio.iscoroutinefunction() as an alias for
# inspect.iscoroutinefunction(), whilst also removing the _is_coroutine marker.
# The latter is replaced with the inspect.markcoroutinefunction decorator.
# Until 3.12 is the minimum supported Python version, provide a shim.

if hasattr(inspect, "markcoroutinefunction"):
    iscoroutinefunction = inspect.iscoroutinefunction
    markcoroutinefunction: Callable[[F], F] = inspect.markcoroutinefunction
else:
    iscoroutinefunction = asyncio.iscoroutinefunction  # type: ignore[assignment]

    def markcoroutinefunction(func: F) -> F:
        func._is_coroutine = asyncio.coroutines._is_coroutine  # type: ignore
        return func


def is_coroutine_function(fn):
    try:
        return six.PY34 and asyncio.iscoroutinefunction(fn)
    except:  # pylint: disable=bare-except # noqa
        return False


def is_coroutine_callable(call: F) -> bool:
    if inspect.isclass(call):
        return False
    if inspect.iscoroutinefunction(call):
        return True
    partial_call = isinstance(call, functools.partial) and call.func
    dunder_call = partial_call or getattr(call, "__call__", None)
    return inspect.iscoroutinefunction(dunder_call)
