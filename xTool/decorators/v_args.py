from functools import update_wrapper, wraps
from inspect import getmembers, getmro
from typing import Any, Callable, Optional


class Decoratable:
    "Provides support for decorating methods with @v_args"

    @classmethod
    def _apply_v_args(cls, visit_wrapper):
        mro = getmro(cls)
        assert mro[0] is cls
        libmembers = {name for _cls in mro[1:] for name, _ in getmembers(_cls)}
        for name, value in getmembers(cls):

            # Make sure the function isn't inherited (unless it's overwritten)
            if name.startswith("_") or (name in libmembers and name not in cls.__dict__):
                continue
            if not callable(value):
                continue

            # Skip if v_args already applied (at the function level)
            if isinstance(cls.__dict__[name], VArgsWrapper):
                continue

            # 使用装饰器 VArgsWrapper 装饰函数
            # cls.__dict__[name] 需要装饰的函数
            setattr(cls, name, VArgsWrapper(cls.__dict__[name], visit_wrapper))
        return cls

    def __class_getitem__(cls, _):
        return cls


class VArgsWrapper:
    """
    A wrapper around a Callable. It delegates `__call__` to the Callable.
    If the Callable has a `__get__`, that is also delegate and the resulting function is wrapped.
    Otherwise, we use the original function mirroring the behaviour without a __get__.
    We also have the visit_wrapper attribute to be used by Transformers.
    """

    base_func: Callable

    def __init__(self, func: Callable, visit_wrapper: Callable[[Callable, str, list, Any], Any]):
        if isinstance(func, VArgsWrapper):
            func = func.base_func
        # https://github.com/python/mypy/issues/708
        self.base_func = func  # type: ignore[assignment]
        self.visit_wrapper = visit_wrapper
        update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        """执行原始的函数 ."""
        return self.base_func(*args, **kwargs)

    def __get__(self, instance, owner=None):
        try:
            # Use the __get__ attribute of the type instead of the instance
            # to fully mirror the behavior of getattr
            g = type(self.base_func).__get__
        except AttributeError:
            return self
        else:
            return VArgsWrapper(g(self.base_func, instance, owner), self.visit_wrapper)

    def __set_name__(self, owner, name):
        try:
            f = type(self.base_func).__set_name__
        except AttributeError:
            return
        else:
            f(self.base_func, owner, name)


def apply_v_args(obj, visit_wrapper):
    """对类或类中的函数添加装饰器 ."""
    try:
        _apply = obj._apply_v_args
    except AttributeError:
        # 对指定的函数添加装饰器 VArgsWrapper, 给函数添加属性 visit_wrapper
        return VArgsWrapper(obj, visit_wrapper)
    else:
        # 对一个类执行 _apply_v_args()方法，对类中符合条件的函数添加装饰器 VArgsWrapper，给每个函数添加属性 visit_wrapper
        return _apply(visit_wrapper)


def apply_visit_wrapper(func, name, wrapper):
    @wraps(func)
    def f(children):
        return wrapper(func, name, children, None)

    return f


def _vargs_inline(f, name, *args, **kwargs):
    """将第一个数组格式的参数，拆分为多个参数"""
    return f(*args[0], **kwargs)


def v_args(
    inline: bool = False,
    wrapper: Optional[Callable] = None,
) -> Callable:
    """A convenience decorator factory for modifying the behavior of user-supplied visitor methods.

    By default, callback methods of transformers/visitors accept one argument - a list of the node's children.

    Parameters:
        inline (bool, optional): Children are provided as ``*args`` instead of a list argument (not recommended for very long lists).
        wrapper (function, optional): Provide a function to decorate all methods.
    """
    func = None
    if inline:
        func = _vargs_inline

    if wrapper is not None:
        if func is not None:
            raise ValueError("Cannot use 'wrapper' along with 'inline'.")
        func = wrapper

    def _visitor_args_dec(obj):
        return apply_v_args(obj, func)

    return _visitor_args_dec
