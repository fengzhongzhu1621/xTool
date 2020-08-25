# -*- coding: utf-8 -*-

import logging
import asyncio
from math import ceil
from functools import wraps
from typing import (  # noqa
    Awaitable,
    Any,
    Optional,
)
import warnings

try:
    import uvloop
    event_loop_policy = uvloop.EventLoopPolicy()
except ImportError:
    event_loop_policy = asyncio.DefaultEventLoopPolicy()


def uvloop_installed():
    try:
        import uvloop  # noqa

        return True
    except ImportError:
        return False


def load_uvlopo():
    try:
        import uvloop  # type: ignore

        if not isinstance(
                asyncio.get_event_loop_policy(),
                uvloop.EventLoopPolicy):
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass


def get_running_loop(
    loop: Optional[asyncio.AbstractEventLoop] = None
) -> asyncio.AbstractEventLoop:
    if loop is None:
        loop = asyncio.get_event_loop()
    if not loop.is_running():
        warnings.warn("The object should be created from async function",
                      DeprecationWarning, stacklevel=3)
        if loop.get_debug():
            logging.warning(
                "The object should be created from async function",
                stack_info=True)
    return loop


def call_later(cb, timeout, loop):  # type: ignore
    if timeout is not None and timeout > 0:
        # loop.time() 以float类型返回当前时间循环的内部时间
        when = ceil(loop.time() + timeout)
        return loop.call_at(when, cb)


@asyncio.coroutine
def noop(*args, **kwargs):  # type: ignore
    return  # type: ignore


async def noop2(*args, **kwargs):
    return


class DeprecationWaiter:
    __slots__ = ('_awaitable', '_awaited')

    def __init__(self, awaitable: Awaitable[Any]) -> None:
        self._awaitable = awaitable
        self._awaited = False

    def __await__(self) -> Any:
        self._awaited = True
        return self._awaitable.__await__()

    def __del__(self) -> None:
        if not self._awaited:
            warnings.warn("please use await")


def awaitable(func):
    """将函数转换为可await函数 ."""
    # Avoid python 3.8+ warning
    # 如果 func 是一个 协程函数 则返回 True
    if asyncio.iscoroutinefunction(func):
        return func

    async def awaiter(obj):
        return obj

    @wraps(func)
    def wrap(*args, **kwargs):
        # 执行业务函数
        result = func(*args, **kwargs)

        if hasattr(result, "__await__"):
            return result
        if asyncio.iscoroutine(result) or asyncio.isfuture(result):
            return result

        return awaiter(result)

    return wrap


if __name__ == "__main__":
    async def noop2(*args, **kwargs):
        return asyncio.sleep(1)

    async def task():
        return await DeprecationWaiter(noop2())

    async def task2():
        return DeprecationWaiter(noop2())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(task())
    loop.run_until_complete(task2())

    loop.close()
