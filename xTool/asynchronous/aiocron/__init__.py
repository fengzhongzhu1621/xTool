"""
异步定时器，精确到秒级别

如果当前的任务没有执行完成，下一个调度不会等待上一个任务执行完毕，所以业务层需要自行解决任务的幂等问题
"""

import asyncio
import functools
import time
from datetime import datetime
from uuid import uuid4

from croniter.croniter import croniter
from tzlocal import get_localzone


async def null_callback(*args):
    return args


def wrap_func(func):
    """将方法转换为协程 ."""
    if not asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return func


class Cron:

    def __init__(self, spec, func=None, args=(), start=False, uuid=None, loop=None, tz=None):
        self.spec = spec
        # 将执行函数转换为协程
        if func is not None:
            self.func = func if not args else functools.partial(func, *args)
        else:
            self.func = null_callback
        self.cron = wrap_func(self.func)
        # 获得当前时区
        self.tz = get_localzone() if tz is None else tz
        # 是否自动启动调度器，默认不执行
        self.auto_start = start
        # 调度唯一标识
        self.uuid = uuid if uuid is not None else uuid4()
        self.handle = self.future = self.croniter = None
        # 事件循环
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        # 如果默认启动调度器，则在下一个事件循环启动开始任务
        if self.auto_start and self.func is not null_callback:
            self.handle = self.loop.call_soon_threadsafe(self.start)

    def start(self):
        """Start scheduling"""
        self.stop()
        self.initialize()
        self.handle = self.loop.call_at(self.get_next(), self.call_next)

    def stop(self):
        """Stop scheduling"""
        if self.handle is not None:
            self.handle.cancel()
        self.handle = self.future = self.croniter = None

    async def next(self, *args):
        """yield from .next()"""
        self.initialize()
        self.future = asyncio.Future(loop=self.loop)
        self.handle = self.loop.call_at(self.get_next(), self.call_func, *args)
        return await self.future

    def initialize(self):
        """Initialize croniter and related times"""
        if self.croniter is None:
            self.time = time.time()
            self.datetime = datetime.now(self.tz)
            # 返回当前时间，一个float值，根据事件循环的内部时钟。
            self.loop_time = self.loop.time()
            self.croniter = croniter(self.spec, start_time=self.datetime)

    def get_next(self):
        """Return next iteration time related to loop time"""
        return self.loop_time + (self.croniter.get_next(float) - self.time)

    def call_next(self):
        """Set next hop in the loop. Call task"""
        if self.handle is not None:
            # 创建future的时候，task为pending，事件循环调用执行的时候当然就是running，调用完毕自然就是done，
            # 如果需要停止事件循环，就需要先把task取消，状态为cancel。
            # 即在下一次事件循环，
            self.handle.cancel()
        next_time = self.get_next()
        # 在 3.8 版更改: 在 Python 3.7 和更早版本的默认事件循环实现中，when 和当前时间相差不能超过一天。 在这 Python
        # 3.8 中已被修复。
        self.handle = self.loop.call_at(next_time, self.call_next)
        self.call_func()

    def call_func(self, *args, **kwargs):
        """Called. Take care of exceptions using gather"""
        # 如果业务逻辑返回异常，则不会退出，会将异常放在future中
        asyncio.gather(
            self.cron(*args, **kwargs), loop=self.loop, return_exceptions=True  # 业务逻辑处理函数
        ).add_done_callback(self.set_result)

    def set_result(self, result):
        """Set future's result if needed (can be an exception).
        Else raise if needed."""
        result = result.result()[0]
        if self.future is not None:
            if isinstance(result, Exception):
                self.future.set_exception(result)
            else:
                self.future.set_result(result)
            self.future = None
        elif isinstance(result, Exception):
            raise result

    def __call__(self, func):
        """Used as a decorator"""
        self.func = func
        self.cron = wrap_func(func)
        if self.auto_start:
            self.loop.call_soon_threadsafe(self.start)
        return self

    def __str__(self):
        return "{0.spec} {0.func}".format(self)

    def __repr__(self):
        return "<Cron {0.spec} {0.func}>".format(self)


def crontab(spec, func=None, args=(), start=True, loop=None, tz=None):
    return Cron(spec, func=func, args=args, start=start, loop=loop, tz=tz)
