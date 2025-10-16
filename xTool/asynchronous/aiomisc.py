import asyncio
import logging
import socket
import sys
import warnings
from asyncio import events, open_connection
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from functools import partial, wraps
from math import ceil
from multiprocessing import cpu_count
from typing import Any, Awaitable, Callable, Iterable, List, Optional, Tuple, TypeVar  # noqa

from xTool.net.ip import is_ipv6

UVLOOP_INSTALLED = False

try:
    import uvloop  # type: ignore # noqa

    UVLOOP_INSTALLED = True
    event_loop_policy = uvloop.EventLoopPolicy()
except ImportError:
    event_loop_policy = asyncio.DefaultEventLoopPolicy()


except ImportError:
    pass

log = logging.getLogger(__name__)

T = TypeVar("T")
OptionsType = Iterable[Tuple[int, int, int]]
F = TypeVar("F", bound=Callable[..., Any])

try:
    import contextvars

    def context_partial(func: F, *args: Any, **kwargs: Any) -> Any:
        context = contextvars.copy_context()
        return partial(context.run, func, *args, **kwargs)

except ImportError:
    context_partial = partial

try:
    from trio import Path
    from trio import open_file as open_async  # type: ignore

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
    from asyncio import create_task, get_running_loop
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
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> asyncio.AbstractEventLoop:
    if loop is None:
        loop = asyncio.get_event_loop()
    if not loop.is_running():
        warnings.warn(
            "The object should be created from async function",
            DeprecationWarning,
            stacklevel=3,
        )
        if loop.get_debug():
            log.warning("The object should be created from async function", stack_info=True)
    return loop


def uvloop_installed():
    try:
        import uvloop  # noqa

        return True
    except ImportError:
        return False


def load_uvloop():
    try:
        import uvloop  # type: ignore

        if not isinstance(asyncio.get_event_loop_policy(), uvloop.EventLoopPolicy):
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass


async def null_callback(*args):
    return args


def create_default_event_loop(
    pool_size=None,
    policy=event_loop_policy,
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


async def noop(*args, **kwargs):  # type: ignore
    return  # type: ignore


async def noop2(*args, **kwargs):
    return


class DeprecationWaiter:
    __slots__ = ("_awaitable", "_awaited")

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


def wrap_func(func):
    """将函数转换为协程，参考asyncio.coroutine ."""
    if not asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return func


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
    """保护一个 可等待对象 防止其被 取消
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
                "Skipping object %r because it's not a Task or Future",
                task,
            )

    if not cancelled_tasks:
        return future

    # 创建等待任务取消的future
    waiter = asyncio.ensure_future(
        asyncio.gather(*cancelled_tasks, return_exceptions=True),
    )

    return waiter


def set_future_exception(waiter, exc):
    """将future标为执行完成，并设置Exception ."""
    if waiter is not None:
        # 判断waiter任务是否已经取消
        # 如果没有取消，将waiter future标为执行完成，并设置Exception
        if not waiter.cancelled():
            waiter.set_exception(exc)


def set_future_result(waiter, value):
    """设置future的返回结果 ."""
    if waiter is not None:
        if not waiter.cancelled():
            waiter.set_result(value)


def set_future_finish(future, result, exc):
    """设置future结束 ."""
    if not future.done():
        if exc is None:
            future.set_result(result)
        else:
            future.set_exception(exc)


async def wait_for_data(loop=None):
    """等待数据准备好 ."""
    if loop is None:
        _loop = events.get_event_loop()
    else:
        _loop = loop
    _waiter = _loop.create_future()
    try:
        # 等待future的返回结果
        await _waiter
    finally:
        _waiter = None
    return _waiter


def wakeup_waiter(waiter):
    """唤醒等待者 ."""
    _waiter = waiter
    if _waiter is not None:
        waiter = None
        if not _waiter.cancelled():
            _waiter.set_result(None)
    return waiter


async def open_connection(host: str, port: int, timeout: float, loop: asyncio.AbstractEventLoop):
    if is_ipv6(host):
        family = socket.AF_INET6
    else:
        family = socket.AF_UNSPEC
    return await asyncio.wait_for(
        open_connection(host=host, port=port, loop=loop, family=family),
        timeout,
        loop=loop,
    )


try:
    import trio  # type: ignore

    def stat_async(path):
        return trio.Path(path).stat()

    open_async = trio.open_file
    CancelledErrors = tuple([asyncio.CancelledError, trio.Cancelled])
except ImportError:
    from aiofiles import open as aio_open  # type: ignore
    from aiofiles.os import stat as stat_async  # type: ignore  # noqa: F401

    async def open_async(file, mode="r", **kwargs):
        return aio_open(file, mode, **kwargs)

    CancelledErrors = tuple([asyncio.CancelledError])


async def await_many_dispatch(consumer_callables, dispatch):
    """
    Given a set of consumer callables, awaits on them all and passes results
    from them to the dispatch awaitable as they come in.
    """
    # Call all callables, and ensure all return types are Futures
    tasks = [asyncio.ensure_future(consumer_callable()) for consumer_callable in consumer_callables]
    try:
        while True:
            # Wait for any of them to complete
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            # Find the completed one(s), yield results, and replace them
            for i, task in enumerate(tasks):
                if task.done():
                    result = task.result()
                    await dispatch(result)
                    tasks[i] = asyncio.ensure_future(consumer_callables[i]())
    finally:
        # Make sure we clean up tasks on exit
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


async def await_many_dispatch(consumer_callables: List[Awaitable], dispatch: Callable):
    """
    Given a set of consumer callables, awaits on them all and passes results
    from them to the dispatch awaitable as they come in.
    """
    # Call all callables, and ensure all return types are Futures
    # 从协程创建任务，创建多个消费者
    tasks = [asyncio.ensure_future(consumer_callable()) for consumer_callable in consumer_callables]
    try:
        while True:
            # Wait for any of them to complete
            # 等待任意一个任务完成，即其中有一个消费者任务已处理完毕
            #
            # asyncio.ALL_COMPLETED（默认值）：当所有输入任务都完成时返回。
            # 这意味着 done 集合将包含所有已完成的任务，而 pending 集合将为空。
            #
            # asyncio.FIRST_COMPLETED：当第一个输入任务完成时返回。此时，done 集合将包含一个或多个已完成的任务（取决于哪个任务首先完成），
            # 而 pending 集合将包含剩余未完成的任务。
            #
            # asyncio.FIRST_EXCEPTION：当第一个输入任务引发异常时返回。如果没有任何任务引发异常，
            # 则行为与 asyncio.FIRST_COMPLETED 相同。
            _done, _pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            # Find the completed one(s), yield results, and replace them
            # 定位已完成的任务
            for i, task in enumerate(tasks):
                if task.done():
                    # 返回已完成任务的执行结果
                    result = task.result()
                    # 重新给消费者分配任务
                    await dispatch(result)
                    # 添加一个新的消费者，所有的消费者继续等待下一轮的处理
                    tasks[i] = asyncio.ensure_future(consumer_callables[i]())
    finally:
        # Make sure we clean up tasks on exit
        # 关闭消费者任务
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
