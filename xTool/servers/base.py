# -*- coding: utf-8 -*-

import asyncio
from xTool.servers.context import Context, get_context
from xTool.aiomisc import cancel_tasks


class ServiceMeta(type):
    """在对象中添加变量__async_required__和__required__ . """
    def __new__(cls, name, bases, namespace, **kwds):
        instance = type.__new__(cls, name, bases, dict(namespace))

        for key in ("__async_required__", "__required__"):
            setattr(instance, key, frozenset(getattr(instance, key, ())))

        check_instance = all(
            asyncio.iscoroutinefunction(getattr(instance, method))
            for method in instance.__async_required__
        )

        if not check_instance:
            raise TypeError(
                "Following methods must be coroutine functions", tuple(
                    "%s.%s" %
                    (name, m) for m in instance.__async_required__), )

        return instance


class Service(metaclass=ServiceMeta):
    # 协程
    __async_required__ = "start", "stop"
    # 必填参数
    __required__ = ()

    def __init__(self, **kwargs):
        lost_kw = self.__required__ - kwargs.keys()
        if lost_kw:
            raise AttributeError("Absent attributes", lost_kw)

        self.loop = None
        self._set_params(**kwargs)
        self.__context = None
        self.start_event = None       # type: asyncio.Event

    @property
    def context(self) -> Context:
        if self.__context is None:
            self.__context = get_context()
        return self.__context

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.start_event = asyncio.Event()

    def _set_params(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    async def start(self):
        raise NotImplementedError

    async def stop(self, exception: Exception = None):
        pass


class SimpleServer(Service):
    def __init__(self, **kwargs):
        self.server = None
        self.tasks = set()
        super().__init__(**kwargs)

    def create_task(self, coro):
        task = self.loop.create_task(coro)
        self.tasks.add(task)
        # 任务执行完成后从集合中删除
        task.add_done_callback(self.tasks.remove)
        return task

    async def start(self):
        raise NotImplementedError

    async def stop(self, exc: Exception = None):
        await cancel_tasks(self.tasks)
        self.server.close()
