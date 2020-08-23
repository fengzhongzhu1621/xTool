# -*- coding: utf-8 -*-

import asyncio
import collections
from typing import Any, Optional

try:
    from typing import Deque
except ImportError:
    from typing_extensions import Deque  # noqa


class EventResultOrError:
    """
    This class wrappers the Event asyncio lock allowing either awake the
    locked Tasks without any error or raising an exception.

    thanks to @vorpalsmith for the simple design.
    """
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._exc = None  # type: Optional[BaseException]
        # 通过维护内部的标识符来实现线程间的同步问题
        self._event = asyncio.Event(loop=loop)
        self._waiters = collections.deque()  # type: Deque[asyncio.Future[Any]]

    def set(self, exc: Optional[BaseException]=None) -> None:
        # 可以通过设置异常来唤醒任务
        self._exc = exc
        # 设置Event对象内部的信号标志为真
        self._event.set()

    async def wait(self) -> Any:
        # 当Event对象的内部信号标志为假时，则wait方法一直等到其为真时才返回
        waiter = self._loop.create_task(self._event.wait())
        self._waiters.append(waiter)
        try:
            # 等待Event对象的内部信号标志为True
            val = await waiter
        finally:
            self._waiters.remove(waiter)

        # 使用异常唤醒任务后，抛出此异常
        if self._exc is not None:
            raise self._exc

        return val

    def cancel(self) -> None:
        """ Cancel all waiters """
        for waiter in self._waiters:
            waiter.cancel()
