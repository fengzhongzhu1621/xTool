from typing import Callable, Union, Generator

from xTool.type_hint import T


class Result:
    pass


_HookImplFunction = Callable[..., Union[T, Generator[None, Result[T], None]]]
