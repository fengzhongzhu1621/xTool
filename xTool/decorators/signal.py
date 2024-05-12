"""
基于信号的观察者模式

定义对象间一种一对多的依赖关系，使得当每一个对象改变状态，则所有依赖于它的对象都会得到通知并自动更新。
"""

import inspect


class Signal:

    __slots__ = ("_receivers", "_is_frozen")

    def __init__(self) -> None:
        self._receivers = set()

    def reset_receivers(self):
        self._receivers = set()

    def set_receivers(self, receivers):
        self._receivers = receivers

    def get_receivers(self):
        return self._receivers

    def connect(self, receiver):
        """添加一个接收者 ."""
        if self.is_frozen:
            raise RuntimeError(
                "Can't connect receiver (%r) to the frozen signal",
                receiver,
            )

        if not inspect.iscoroutinefunction(receiver):
            raise RuntimeError("%r is not a coroutine function", receiver)
        self._receivers.add(receiver)

    async def call(self, *args, **kwargs):
        """等待所有的接收者处理完消息 ."""
        for receiver in self._receivers:
            await receiver(*args, **kwargs)

    def copy(self):
        clone = Signal()
        # unfreeze on copy
        clone.set_receivers(self._receivers)
        return clone

    @property
    def is_frozen(self):
        return isinstance(self._receivers, frozenset)

    def freeze(self):
        self._receivers = frozenset(self._receivers)


def receiver(s: Signal):
    def decorator(func):
        s.connect(func)
        return func

    return decorator
