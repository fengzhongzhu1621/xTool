# -*- coding: utf-8 -*-

import asyncio
import inspect
import threading
import typing
from collections import deque


T = typing.TypeVar("T")
R = typing.TypeVar("R")

GenType = typing.Generator[T, R, None]
FuncType = typing.Callable[[], GenType]


class IteratorWrapper(typing.AsyncIterator):
    """将迭代器在线程中运行，并在遍历迭代器前加一个缓冲队列 ."""
    __slots__ = (
        "__close_event", "__closed", "__gen_func", "__gen_task", "__queue",
        "__queue_maxsize", "__read_event", "__write_event", "executor", "loop",
    )
    """Run iterables on dedicated thread pool ."""
    def __init__(
        self, gen_func: FuncType, loop=None,
        max_size=0, executor=None,
    ):

        self.loop = loop or asyncio.get_event_loop()
        self.executor = executor

        self.__closed = False
        self.__close_event = asyncio.Event()
        self.__queue = deque()  # 加一个缓冲队列，存放迭代器的值
        self.__queue_maxsize = max_size
        self.__gen_task = None      # type: asyncio.Task
        self.__gen_func = gen_func  # type: typing.Callable
        self.__write_event = threading.Event()
        self.__read_event = asyncio.Event()

    @property
    def closed(self):
        return self.__closed

    @staticmethod
    def __throw(_):
        pass

    def _set_read_event(self):
        """设置信号 ."""
        def setter():
            if self.__read_event.is_set():
                return
            self.__read_event.set()
        self.loop.call_soon_threadsafe(setter)

    def _in_thread(self) -> None:
        """在线程中的执行函数，用于在线程中执行迭代器 ."""
        try:
            # 执行业务函数，返回的是一个生成器
            gen = iter(self.__gen_func())

            throw = self.__throw
            if inspect.isgenerator(gen):
                throw = gen.throw

            while not self.closed:
                # 遍历生成器的返回结果
                item = next(gen)

                while len(self.__queue) > self.__queue_maxsize:
                    # 队列已满，停止写入
                    self.__write_event.wait(0.1)

                    if self.closed:
                        throw(asyncio.CancelledError())
                        return
                # 将结果添加到队列
                self.__queue.append((item, False))
                # 设置读结束信号
                self._set_read_event()
                # 清除写信号
                if self.__write_event.is_set():
                    self.__write_event.clear()
        except StopIteration as e:
            if self.closed:
                return
            self.__queue.append((e, None))
            self._set_read_event()
        except Exception as e:
            if self.closed:
                return
            self.__queue.append((e, True))
            self.loop.call_soon_threadsafe(self.__read_event.set)
        finally:
            self._set_read_event()
            self.loop.call_soon_threadsafe(self.__close_event.set)

    async def _run(self):
        return await self.loop.run_in_executor(self.executor, self._in_thread)

    async def close(self):
        self.__closed = True
        self.__queue.clear()

        if not self.__gen_task.done():
            self.__gen_task.cancel()

        await self.__close_event.wait()
        await asyncio.gather(
            self.__gen_task, loop=self.loop, return_exceptions=True,
        )
        del self.__queue

    def __aiter__(self):
        if self.__gen_task is not None:
            return self
        # 创建一个线程任务
        self.__gen_task = self.loop.create_task(self._run())
        return self

    async def __anext__(self) -> typing.Awaitable[T]:
        while len(self.__queue) == 0:
            await self.__read_event.wait()
        # 从队列中获取结果
        item, is_exc = self.__queue.popleft()
        # 队列不满通知线程继续往队列里写数据
        self.__write_event.set()

        if len(self.__queue) == 0:
            self.__read_event.clear()

        if is_exc is None:
            await self.close()
            raise StopAsyncIteration(*item.args) from item
        elif is_exc:
            await self.close()
            raise item from item

        return item

    #############################################################
    # 定义上下文管理器 async with IteratorWrapper() as ctx:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.closed:
            return

        await self.close()
