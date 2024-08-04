"""
* Optional[...]是Union[..., None]的简写符号，告诉类型检查器需要特定类型的对象，或者需要None。
...代表任何有效的类型提示，包括复杂的复合类型或更多类型的Union[]。每当你有一个默认值None的关键字参数时，你应该使用Optional。

"""

import os  # noqa
import sys
from concurrent import futures
from datetime import timedelta
from types import ModuleType, TracebackType
from typing import Any, Callable, Iterable, Optional, Tuple, Type, TypeVar, Union

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
F = TypeVar("F", bound=Callable[..., Any])
WrappedFn = TypeVar("WrappedFn", bound=Callable[..., Any])
WrappedFnReturnT = typing.TypeVar("WrappedFnReturnT")
OptionsType = Iterable[Tuple[int, int, int]]
Namespace = Union[ModuleType, type]

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

if sys.version_info >= (3, 9):
    FutureGenericT = futures.Future[typing.Any]
else:
    FutureGenericT = futures.Future


# 是一个包含异常信息的元组，包括异常类型、异常实例和追踪信息。
ExcInfo = Tuple[Type[BaseException], BaseException, Optional[TracebackType]]


class Future(FutureGenericT):
    """Encapsulates a (future or past) attempted call to a target function."""

    def __init__(self, attempt_number: int) -> None:
        super().__init__()
        self.attempt_number = attempt_number

    @property
    def failed(self) -> bool:
        """Return whether a exception is being held in this future."""
        return self.exception() is not None

    @classmethod
    def construct(cls, attempt_number: int, value: Any, has_exception: bool) -> "Future":
        """Construct a new Future object."""
        fut = cls(attempt_number)
        if has_exception:
            fut.set_exception(value)
        else:
            fut.set_result(value)
        return fut
