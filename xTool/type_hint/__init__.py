# -*- coding: utf-8 -*-

import sys
from typing import get_type_hints
from typing import (  # noqa
    Awaitable,
    Any,
    Optional,
    Iterable,
    Tuple,
    TypeVar,
    Callable,
    Union,
)
from xTool.compat import PY3, unicode_type

try:
    import typing  # noqa
    from typing import cast
    ObjectDictBase = typing.Dict[str, typing.Any]
except ImportError:
    ObjectDictBase = dict

    def cast(typ, x):
        return x
else:
    from typing import Any, AnyStr, Union, Optional, Dict, Mapping  # noqa
    from typing import Tuple, Match, Callable  # noqa
    if PY3:
        BaseString = str
    else:
        BaseString = Union[bytes, unicode_type]


if PY3:
    if sys.version_info >= (3, 6):
        PathLike = Union[str, 'os.PathLike[str]']
    else:
        import pathlib  # noqa
        PathLike = Union[str, pathlib.PurePath]


T = TypeVar('T')
OptionsType = Iterable[Tuple[int, int, int]]
F = TypeVar('F', bound=Callable[..., Any])
IP_ADDRESS = Tuple[str, int]


def get_class_object_init_type(class_obj: object, name: str) -> type:
    """获得类对象构造函数中指定参数的类型 ."""
    # 获得运行时类型提示字典，构造必须标注才可以获取到
    object_type = get_type_hints(type(class_obj).__init__).get(name)
    # 如果参数类型为int且默认值为None，会返回typing.Union[int, NoneType]，需要处理这种特殊情况
    if getattr(object_type, '__origin__', None) == Union:
        union_args = object_type.__args__
        object_type = union_args[0]
    return object_type
