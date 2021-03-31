# -*- coding: utf-8 -*-

from asyncio import open_connection
import sys
from math import ceil
from functools import wraps
import asyncio
from typing import (  # noqa
    Awaitable,
    Any,
    Optional,
    Iterable,
    Tuple,
    TypeVar,
    Callable,
)
import warnings
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from contextlib import suppress
from functools import partial
import logging
import socket

from xTool.utils.net import is_ip_v6


try:
    import uvloop
    event_loop_policy = uvloop.EventLoopPolicy()
except ImportError:
    event_loop_policy = asyncio.DefaultEventLoopPolicy()


log = logging.getLogger(__name__)

T = TypeVar('T')
OptionsType = Iterable[Tuple[int, int, int]]
F = TypeVar('F', bound=Callable[..., Any])


try:
    import contextvars

    def context_partial(func: F, *args: Any, **kwargs: Any) -> Any:
        context = contextvars.copy_context()
        return partial(context.run, func, *args, **kwargs)

except ImportError:
    context_partial = partial


try:
    from trio import open_file as open_async, Path  # type: ignore

    def stat_async(path):
        return Path(path).stat()
except ImportError:

    try:
        from aiofiles import open as aio_open  # type: ignore
        from aiofiles.os import stat as stat_async  # type: ignore  # noqa: F401

        async def open_async(file, mode="r", **kwargs):
            return aio_open(file, mode, **kwargs)
    except ImportError:
        pass


if sys.version_info >= (3, 7):
    from asyncio import get_running_loop
    from asyncio import create_task
else:
    from asyncio import _get_running_loop

    def get_running_loop():
        loop = _get_running_loop()
        if loop is None:
            raise RuntimeError("no running event loop")
        return loop

    def create_task(coro):
        loop = get_running_loop()
        return loop.create_task(coro)


def get_and_check_running_loop(
    loop: Optional[asyncio.AbstractEventLoop] = None
) -> asyncio.AbstractEventLoop:
    if loop is None:
        loop = asyncio.get_event_loop()
    if not loop.is_running():
        warnings.warn("The object should be created from async function",
                      DeprecationWarning, stacklevel=3)
        if loop.get_debug():
            log.warning(
                "The object should be created from async function",
                stack_info=True)
    return loop


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


async def awaiter(future: asyncio.Future) -> T:
    """等待future执行结束，返回执行结果 ."""
    try:
        result = await future
        return result
    except asyncio.CancelledError as e:
        if not future.done():
            future.set_exception(e)
        raise


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
            log.warning(
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


def set_exception(waiter, exc):
    """将future标为执行完成，并设置Exception ."""
    if waiter is not None:
        # 判断任务是否已经取消，如果已取消，返回True
        if not waiter.cancelled():
            waiter.set_exception(exc)


def set_result(waiter, value):
    """设置future的返回结果 ."""
    if waiter is not None:
        if not waiter.cancelled():
            waiter.set_result(value)


async def open_connection(host: str, port: int, timeout: float, loop: asyncio.AbstractEventLoop):
    if is_ip_v6(host):
        family = socket.AF_INET6
    else:
        family = socket.AF_UNSPEC
    return await asyncio.wait_for(open_connection(host=host, port=port, loop=loop, family=family),
                                  timeout, loop=loop)


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
