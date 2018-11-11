#coding: utf-8


"""
The "methods" object holds the list of functions that can be called by remote calls.

Add as many methods as needed.

Methods can take either positional or named arguments (but not both, this is a
limitation of JSON-RPC).
"""
from typing import Any, Callable, Optional

from funcsigs import signature  # type: ignore

# 可以通过对类型提示中的参数列表替换一个文本省略号来声明一个可调用的返回类型，而不指定调用参数
Method = Callable[..., Any]


def validate_args(func: Method, *args: Any, **kwargs: Any) -> Method:
    """
    验证参数args, kwargs是否和func的签名一致，如果签名一致，则返回func
    Check if the request's arguments match a function's signature.

    Raises TypeError exception if arguments cannot be passed to a function.

    Args:
        func: The function to check.
        args: Positional arguments.
        kwargs: Keyword arguments.

    Raises:
        TypeError: If the arguments cannot be passed to the function.
    """
    signature(func).bind(*args, **kwargs)
    return func


def validate(method: Callable) -> Callable:
    """验证method是否可调用，如果可调用则返回此方法，否则抛出AssertionError ."""
    assert callable(method)
    return method


class Methods:
    """Holds a list of methods that can be called by a JSON-RPC request."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.items = {}  # type: dict
        self.add(*args, **kwargs)

    def add(self, *args: Any, **kwargs: Any) -> Optional[Callable]:
        """
        Register a function to the list.

        Args:
            *args: Set/Sequence of positional arguments.
            **kwargs: Mapping of named arguments.

        Raises:
            AttributeError: Raised if the method being added has no name. (i.e. it has
                no `__name__` property, and no `name` argument was given.)

        Examples:
            methods = Methods()
            @methods.add
            def subtract(minuend, subtrahend):
                return minuend - subtrahend
        """
        self.items = {
            **self.items,
            # Methods passed as positional args need a __name__ attribute, raises
            # AttributeError otherwise.
            **{m.__name__: validate(m) for m in args},
            **{k: validate(v) for k, v in kwargs.items()},
        }
        if len(args):
            return args[0]  # for the decorator to work
        return None


# 全局方法容器
# A default Methods object which can be used, or user can create their own.
global_methods = Methods()


def add(*args: Any, **kwargs: Any) -> Optional[Callable]:
    """将方法添加到全局容器中 ."""
    return global_methods.add(*args, **kwargs)
