from typing import List

import pytest

from xTool.type_hint import Protocol


class Duck(Protocol):
    def quack(self):
        pass


class Proto(Protocol):
    def meth(self) -> int: ...  # noqa


class C:
    def meth(self) -> int:
        return 0


class D:
    pass


def func(x: Proto) -> int:
    return x.meth()


class Template(Protocol):
    name: str  # This is a protocol member
    value: int = 0  # This one too (with default)

    def method(self) -> None:
        self.temp: List[int] = []  # Error in type checker


def test_func():
    func(C())  # Passes static type check
    with pytest.raises(AttributeError):
        func(D())
