"""
* Optional[...]是Union[..., None]的简写符号，告诉类型检查器需要特定类型的对象，或者需要None。
...代表任何有效的类型提示，包括复杂的复合类型或更多类型的Union[]。每当你有一个默认值None的关键字参数时，你应该使用Optional。

"""

import os  # noqa
import sys
from datetime import timedelta
from typing import (  # type: ignore # noqa # pylint: disable=unused-import
    Any,
    Awaitable,
    Callable,
    Iterable,
    Optional,
    Tuple,
    TypeVar,
    Union,
    get_type_hints,
)

from xTool.compat import PY3, unicode_type

try:
    import typing  # type: ignore # noqa # pylint: disable=unused-import
    from typing import cast

    ObjectDictBase = typing.Dict[str, typing.Any]
except ImportError:
    ObjectDictBase = dict

    def cast(typ, x):
        return x

else:
    from typing import Any, AnyStr, Callable, Dict, Mapping, Match, Optional, Tuple, Union  # noqa

    if PY3:
        BaseString = str
    else:
        BaseString = Union[bytes, unicode_type]

if PY3:
    if sys.version_info >= (3, 6):
        PathLike = Union[str, "os.PathLike[str]"]
    else:
        import pathlib  # noqa

        PathLike = Union[str, pathlib.PurePath]

T = TypeVar("T")
S = TypeVar("S")
OptionsType = Iterable[Tuple[int, int, int]]
F = TypeVar("F", bound=Callable[..., Any])
IP_ADDRESS = Tuple[str, int]
# 时间单位类型
time_unit_type = typing.Union[int, float, timedelta]

try:
    # Protocol and TypedDict are only added to typing module starting from
    # python 3.8
    from typing import Protocol, TypedDict, runtime_checkable  # type: ignore # noqa # pylint: disable=unused-import
except ImportError:
    from typing_extensions import Protocol, TypedDict, runtime_checkable  # type: ignore # noqa

if sys.version_info >= (3, 8):
    from typing import Literal  # noqa
else:
    from typing_extensions import Literal  # noqa
if sys.version_info >= (3, 10):
    from typing import TypeAlias  # noqa
else:
    from typing_extensions import TypeAlias  # noqa
