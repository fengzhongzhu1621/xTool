# -*- coding: utf-8 -*-

"""
* Optional[...]是Union[..., None]的简写符号，告诉类型检查器需要特定类型的对象，或者需要None。
...代表任何有效的类型提示，包括复杂的复合类型或更多类型的Union[]。每当你有一个默认值None的关键字参数时，你应该使用Optional。

"""

import sys
from typing import get_type_hints
from typing import (   # type: ignore # noqa # pylint: disable=unused-import
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
    import typing   # type: ignore # noqa # pylint: disable=unused-import
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


try:
    # Protocol and TypedDict are only added to typing module starting from
    # python 3.8
    from typing import (  # type: ignore # noqa # pylint: disable=unused-import
        Protocol,
        TypedDict,
        runtime_checkable,
    )
except ImportError:
    from typing_extensions import Protocol, TypedDict, runtime_checkable  # type: ignore # noqa


def get_class_object_init_type(class_obj: object, name: str) -> type:
    """获得类对象构造函数中指定参数的类型 ."""
    # 获得运行时类型提示字典，构造必须标注才可以获取到
    object_type = get_type_hints(type(class_obj).__init__).get(name)
    # 如果参数类型为int且默认值为None，会返回typing.Union[int, NoneType]，需要处理这种特殊情况
    if getattr(object_type, '__origin__', None) == Union:
        union_args = object_type.__args__
        object_type = next(arg for arg in union_args if arg != type(None))
    return object_type
