from typing import (
    Any,
    Callable,
)


class reify:
    """Use as a class method decorator.  It operates almost exactly like
    the Python `@property` decorator, but it puts the result of the
    method it decorates into the instance dict after the first call,
    effectively replacing the function it decorates with an instance
    variable.  It is, in Python parlance, a data descriptor.

    懒加载装饰器，将第一次调用方法的返回结果存储在类变量中
    """

    def __init__(self, wrapped: Callable[..., Any]) -> None:
        self.wrapped = wrapped
        self.__doc__ = wrapped.__doc__
        # 属性名
        self.name = wrapped.__name__

    def __get__(self, inst: Any, owner: Any) -> Any:
        try:
            # 第一次加载属性时，结果缓存，保证只运行一次
            try:
                return inst._cache[self.name]
            except KeyError:
                val = self.wrapped(inst)
                inst._cache[self.name] = val
                return val
        except AttributeError:
            if inst is None:
                return self
            raise

    def __set__(self, inst: Any, value: Any) -> None:
        raise AttributeError("reified property is read-only")


reify_py = reify

try:
    from ._helpers import reify as reify_c

    reify = reify_c  # type: ignore
except ImportError:
    pass
