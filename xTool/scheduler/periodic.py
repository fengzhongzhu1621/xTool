import asyncio
import logging
from functools import partial
from typing import Tuple, Type, Union

from xTool.asynchronous import aiomisc

log = logging.getLogger(__name__)


class PeriodicCallback:
    """周期回调 ."""

    __slots__ = "_cb", "_closed", "_task", "_loop", "_handle", "__name"

    def __init__(self, coroutine_func, *args, **kwargs):
        self.__name = repr(coroutine_func)
        self._cb = partial(aiomisc.awaitable(coroutine_func), *args, **kwargs)
        self._closed = False
        self._loop = None
        self._handle = None
        self._task = None

    async def _run(self, suppress_exceptions=()):
        try:
            await self._cb()
        except suppress_exceptions:
            return
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Periodic task error:")

    def start(
        self,
        interval: Union[int, float],
        loop=None,
        *,
        delay: Union[int, float] = 0,
        shield: bool = False,
        suppress_exceptions: Tuple[Type[Exception]] = (),
    ):
        if self._task and not self._task.done():
            raise asyncio.InvalidStateError

        self._loop = loop or asyncio.get_event_loop()

        self._closed = False

        def periodic():
            if self._loop.is_closed():
                return

            if self._task and not self._task.done():
                log.warning("Task %r still running skipping", self)
                return

            del self._task
            self._task = None

            if self._closed:
                return

            # 创建任务
            runner = aiomisc.shield(self._run) if shield else self._run
            self._task = self._loop.create_task(runner(suppress_exceptions))

            # 任务执行完成，继续下一个周期的调用，每隔interval执行一次
            self._task.add_done_callback(call)

        def call(*_):
            if self._handle is not None:
                self._handle.cancel()
                del self._handle

            self._handle = self._loop.call_later(interval, periodic)

        # 延迟指定delay后，启动周期调用
        self._loop.call_later(delay, self._loop.call_soon_threadsafe, periodic)

    def stop(self):
        self._closed = True

        if self._task is None:
            self._task = self._loop.create_future()
            self._task.set_exception(RuntimeError("Callback not started"))
        elif not self._task.done():
            self._task.cancel()

        if self._handle:
            self._handle.cancel()

        return self._task

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.__name)

    @property
    def task(self):
        return self._task
