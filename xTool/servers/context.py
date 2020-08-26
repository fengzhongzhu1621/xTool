# -*- coding: utf-8 -*-

import asyncio
from collections import defaultdict


class Context:
    __slots__ = ("_storage", "_loop")

    EVENT_OBJECTS = dict()

    def close(self):
        self._storage.clear()
        self.EVENT_OBJECTS.pop(self._loop, None)

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        # 创建附加到事件循环的asyncio.Future对象
        # 创建一个任务（Future对象），没绑定任何行为，则这个任务永远不知道什么时候结束
        self._storage = defaultdict(loop.create_future)
        self.EVENT_OBJECTS[loop] = self

    def __getitem__(self, item):
        """从仓库中获取Future，没有则创建一个没有绑定行为的Future，等待结果赋值 ."""
        return self._storage[item]

    def __setitem__(self, item, value):
        """给Future设置返回值 ."""
        self._loop.call_soon_threadsafe(self.__setter, item, value)

    def __setter(self, item, value):
        if self._storage[item].done():
            del self._storage[item]

        self._storage[item].set_result(value)


def get_context(loop: asyncio.AbstractEventLoop = None) -> Context:
    loop = loop or asyncio.get_event_loop()

    if loop.is_closed():
        raise RuntimeError("event loop is closed")

    # 没有则抛出KeyError
    return Context.EVENT_OBJECTS[loop]


__all__ = ("get_context", "Context")
