# -*- coding: utf-8 -*-

import asyncio
from asyncio import Future, AbstractEventLoop, Task  # noqa
from asyncio.events import get_event_loop
from functools import partial, wraps
import inspect
import typing
from types import MappingProxyType
from typing import NamedTuple, Any, Optional, TypeVar, Callable  # noqa
from concurrent.futures import ThreadPoolExecutor
import threading
import logging

from xTool.aiomisc import awaiter, context_partial
from xTool.iterator_wrapper import IteratorWrapper


T = typing.TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

log = logging.getLogger(__name__)


def run_in_executor(
    func: F,
    executor: ThreadPoolExecutor = None,
    args: Any = (),
    kwargs: Any = MappingProxyType({}),
) -> Future:
    """将耗时函数加入到线程池 ."""
    loop = get_event_loop()
    # noinspection PyTypeChecker
    return loop.run_in_executor(  # type: ignore
        executor, context_partial(func, *args, **kwargs),
    )


def threaded_iterable(
    func: F = None,
    max_size: int = 0
) -> Any:
    """线程迭代器 ."""
    if isinstance(func, int):
        return partial(threaded_iterable, max_size=func)
    if func is None:
        return partial(threaded_iterable, max_size=max_size)

    @wraps(func)
    def wrap(*args: Any, **kwargs: Any) -> Any:
        return IteratorWrapper(
            context_partial(func, *args, **kwargs),  # type: ignore
            max_size=max_size,
        )

    return wrap


def threaded(func: F) -> Callable[..., typing.Awaitable[Any]]:
    """在线程池中新建一个线程来执行耗时函数 ."""
    # 判断是否时
    if asyncio.iscoroutinefunction(func):
        raise TypeError("Can not wrap coroutine")
    # 判断是否为生成器函数
    if inspect.isgeneratorfunction(func):
        return threaded_iterable(func)

    @wraps(func)
    def wrap(*args: Any, **kwargs: Any) -> typing.Awaitable[Any]:
        # 在线程池中新建一个线程来执行耗时函数
        future = run_in_executor(func=func, args=args, kwargs=kwargs)
        # 等待future执行结束，返回执行结果
        result = awaiter(future)  # type: Any
        return result

    return wrap


def run_in_new_thread(
    func: F,
    args: Any = (),
    kwargs: Any = MappingProxyType({}),
    detouch: bool = True,
    no_return: bool = False,
) -> asyncio.Future:
    """创建一个独立线程运行任务 ."""
    loop = asyncio.get_event_loop()
    future = loop.create_future()

    def set_result(result: Any) -> None:
        if future.done() or loop.is_closed():
            return

        future.set_result(result)

    def set_exception(exc: Exception) -> None:
        if future.done() or loop.is_closed():
            return

        future.set_exception(exc)

    @wraps(func)
    def in_thread(target: F) -> None:
        try:
            # 执行业务逻辑，设置成功结果到future
            loop.call_soon_threadsafe(
                set_result, target(),
            )
        except Exception as exc:
            if loop.is_closed() and no_return:
                return

            elif loop.is_closed():
                log.exception("Uncaught exception from separate thread")
                return

            # 设置失败结果到future
            loop.call_soon_threadsafe(set_exception, exc)

    thread = threading.Thread(
        target=in_thread, name=func.__name__,
        args=(
            context_partial(func, *args, **kwargs),
        ),
    )

    # 默认为True： 主线程结束时，子线程也随之结束
    thread.daemon = detouch

    thread.start()
    return future


def threaded_separate(
    func: F,
    detouch: bool = True
) -> Callable[..., typing.Awaitable[Any]]:
    """独立线程运行任务装饰器 ."""
    if isinstance(func, bool):
        return partial(threaded_separate, detouch=detouch)

    if asyncio.iscoroutinefunction(func):
        raise TypeError("Can not wrap coroutine")

    @wraps(func)
    def wrap(*args: Any, **kwargs: Any) -> Any:
        future = run_in_new_thread(
            func, args=args, kwargs=kwargs, detouch=detouch,
        )

        return awaiter(future)

    return wrap


class IteratorWrapperSeparate(IteratorWrapper):
    @threaded_separate
    def _run(self) -> None:
        return self._in_thread()


def threaded_iterable_separate(func: F = None, max_size: int = 0) -> Any:
    if isinstance(func, int):
        return partial(threaded_iterable, max_size=func)
    if func is None:
        return partial(threaded_iterable, max_size=max_size)

    @wraps(func)
    def wrap(*args: Any, **kwargs: Any) -> Any:
        return IteratorWrapperSeparate(
            context_partial(func, *args, **kwargs),  # type: ignore
            max_size=max_size,
        )

    return wrap


class CoroutineWaiter:
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        coroutine_func: F,
        *args: Any,
        **kwargs: Any
    ):
        self.__func = partial(
            coroutine_func, *args, **kwargs
        )  # type: partial[Any]
        self.__loop = loop
        self.__event = threading.Event()
        self.__result = None
        self.__exception = None  # type: Optional[BaseException]

    def _on_result(self, task: asyncio.Task) -> None:
        self.__exception = task.exception()
        if self.__exception is None:
            self.__result = task.result()
        self.__event.set()

    def _awaiter(self) -> None:
        task = self.__loop.create_task(self.__func())  # type: Task[Any]
        task.add_done_callback(self._on_result)

    def start(self) -> None:
        self.__loop.call_soon_threadsafe(self._awaiter)

    def wait(self) -> Any:
        """阻塞等待 ."""
        self.__event.wait()
        if self.__exception is not None:
            raise self.__exception
        return self.__result


def sync_wait_coroutine(
    loop: AbstractEventLoop,
    coro_func: F,
    *args: Any,
    **kwargs: Any
) -> Any:
    """同步协程等待器 ."""
    waiter = CoroutineWaiter(loop, coro_func, *args, **kwargs)
    waiter.start()
    return waiter.wait()
