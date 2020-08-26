# -*- coding: utf-8 -*-

import logging
from math import ceil
from functools import wraps
import asyncio
from typing import (  # noqa
    Awaitable,
    Any,
    Optional,
    Iterable,
)
import warnings
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from contextlib import suppress

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


def create_default_event_loop(
    pool_size=None, policy=event_loop_policy,
    debug=False,
):
    with suppress(RuntimeError):
        asyncio.get_event_loop().close()

    # 创建新的事件循环
    asyncio.set_event_loop_policy(policy)
    loop = asyncio.new_event_loop()
    loop.set_debug(debug)
    asyncio.set_event_loop(loop)
    # 设置线程池
    pool_size = pool_size or cpu_count()
    thread_pool = ThreadPoolExecutor(pool_size)
    loop.set_default_executor(thread_pool)

    return loop, thread_pool


def new_event_loop(
    pool_size=None,
    policy=event_loop_policy,
) -> asyncio.AbstractEventLoop:
    loop, _ = create_default_event_loop(pool_size, policy)
    return loop


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


def shield(func):
    """ 保护一个 可等待对象 防止其被 取消
    Simple and useful decorator for wrap the coroutine to `asyncio.shield`.

    假如有个Task(叫做something)被shield保护，如下：

    outer = shield(something())
    res = await outer
    如果outer被取消了，不会影响Task本身(something)的执行。

    >>> @shield
    ... async def non_cancelable_func():
    ...     await asyncio.sleep(1)

    """

    async def awaiter(future):
        return await future

    @wraps(func)
    def wrap(*args, **kwargs):
        return wraps(func)(awaiter)(asyncio.shield(func(*args, **kwargs)))

    return wrap


def cancel_tasks(tasks: Iterable[asyncio.Future]) -> asyncio.Future:
    """取消任务 ."""
    future = asyncio.get_event_loop().create_future()
    future.set_result(None)

    # 如果没有要取消的任务，返回一个future
    if not tasks:
        return future

    cancelled_tasks = []
    exc = asyncio.CancelledError()

    for task in tasks:
        # 忽略完成的任务
        if task.done():
            continue

        if isinstance(task, asyncio.Task):
            # 取消任务
            task.cancel()
            cancelled_tasks.append(task)
        elif isinstance(task, asyncio.Future):
            # 将future标为执行完成，并设置Exception
            task.set_exception(exc)
        else:
            logging.warning(
                "Skipping object %r because it's not a Task or Future", task,
            )

    if not cancelled_tasks:
        return future

    # 创建等待任务取消的future
    waiter = asyncio.ensure_future(
        asyncio.gather(
            *cancelled_tasks, return_exceptions=True
        ),
    )

    return waiter


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
