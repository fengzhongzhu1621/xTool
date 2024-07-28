import abc
from functools import wraps
from typing import Callable, Dict

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from pydantic import validate_arguments

from xTool.exceptions import XToolException
from xTool.inspect_utils.module_loading import import_string


class InvocationMeta(type):
    """
    Metaclass for function invocation
    """

    def __new__(cls, name, bases, dct):
        # ensure initialization is only performed for subclasses of Plugin
        parents = [b for b in bases if isinstance(b, InvocationMeta)]
        if not parents:
            return super().__new__(cls, name, bases, dct)

        new_cls = super().__new__(cls, name, bases, dct)

        # meta validation
        meta_obj = getattr(new_cls, "Meta", None)
        if not meta_obj:
            raise AttributeError("Meta class is required")

        func_name = getattr(meta_obj, "func_name", None)
        if not func_name:
            raise AttributeError("func_name is required in Meta")

        desc = getattr(meta_obj, "desc", None)
        if desc is not None and not isinstance(desc, str):
            raise AttributeError("desc in Meta should be str")

        # register func
        FunctionsManager.register_invocation_cls(new_cls)

        return new_cls


class FunctionsManager:
    """函数管理器 ."""

    # 存放注册的可执行对象
    __hub = {}  # type: ignore

    @classmethod
    def register_invocation_cls(cls, invocation_cls: InvocationMeta, name=None) -> None:
        if not name:
            func_name = invocation_cls.Meta.func_name
        else:
            func_name = name
        if not isinstance(func_name, str):
            raise ValueError(f"func_name {func_name} should be string")
        existed_invocation_cls = cls.__hub.get(func_name)
        if existed_invocation_cls:
            raise RuntimeError(
                "func register error, {}'s func_name {} conflict with {}".format(
                    existed_invocation_cls, func_name, invocation_cls
                )
            )

        # 存放类的实例
        cls.__hub[func_name] = invocation_cls()

    @classmethod
    def register_funcs(cls, func_dict) -> None:
        for func_name, func_obj in func_dict.items():
            if not isinstance(func_name, str):
                raise ValueError(f"func_name {func_name} should be string")
            if func_name in cls.__hub:
                raise ValueError(
                    "func register error, {}'s func_name {} conflict with {}".format(
                        func_obj, func_name, cls.__hub[func_name]
                    )
                )
            if isinstance(func_obj, str):
                func = import_string(func_obj)
            elif isinstance(func_obj, Callable):
                func = func_obj
            else:
                raise ValueError("func register error, {} is not be callable".format(func_name))

            cls.__hub[func_name] = func

    @classmethod
    def clear(cls) -> None:
        """清空注册信息 ."""
        cls.__hub = {}

    @classmethod
    def all_funcs(cls) -> Dict:
        """获得所有的注册信息."""
        return cls.__hub

    @classmethod
    def get_func(cls, func_name: str) -> Callable:
        """获得注册的函数 ."""
        func_obj = cls.__hub.get(func_name)
        if not func_obj:
            raise ValueError("func object {} not found".format(func_name))
        return func_obj

    @classmethod
    def func_call(cls, func_name: str, *args, **kwargs):
        """根据函数名执行注册的函数 ."""
        func = cls.get_func(func_name)
        return func(*args, **kwargs)


class BaseInvocation(metaclass=InvocationMeta):
    """
    Base class for function invocation
    """

    class Inputs(BaseModel):
        """
        输入校验器
        """

        pass

    @validate_arguments  # type: ignore
    def __call__(self, *args, **kwargs):

        # 输入参数校验, 仅可能是 args 或 kwargs 之一
        try:
            params = {}
            if args:
                inputs_meta = getattr(self.Inputs, "Meta", None)
                inputs_ordering = getattr(inputs_meta, "ordering", None)
                if isinstance(inputs_ordering, list):
                    if len(args) > len(inputs_ordering):
                        raise XToolException(f"Too many arguments for inputs: {args}")
                    params = dict(zip(inputs_ordering, args))
            elif kwargs:
                params = kwargs

            # 参数校验
            if params:
                self.Inputs(**params)
        except PydanticValidationError as e:
            raise XToolException(e)

        # 执行自定义业务逻辑
        return self.invoke(*args, **kwargs)

    @abc.abstractmethod
    def invoke(self, *args, **kwargs):
        """自定义业务逻辑 ."""
        raise NotImplementedError()


def register_class(name: str):
    def _register_class(cls: BaseInvocation):
        FunctionsManager.register_invocation_cls(cls, name=name)

        @wraps(cls)
        def wrapper():
            return cls()

        return wrapper

    return _register_class


def register_func(name: str):
    def _register_func(func: Callable):
        FunctionsManager.register_funcs({name: func})

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return _register_func
