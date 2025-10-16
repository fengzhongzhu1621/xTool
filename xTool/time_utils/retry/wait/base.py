import abc
import typing

if typing.TYPE_CHECKING:
    from xTool.time_utils.retry.state import RetryCallState

__all__ = [
    "wait_base",
    "wait_combine",
    "WaitBaseT",
]


class wait_base(abc.ABC):
    """Abstract base class for wait strategies."""

    @abc.abstractmethod
    def __call__(self, retry_state: "RetryCallState") -> float:
        pass

    def __add__(self, other: "wait_base") -> "wait_combine":
        # 多个等待结果求和
        # 使用a + b的形式进行加法运算时，Python会首先尝试调用a.__add__(b)。
        # 如果a没有实现__add__方法或者__add__方法返回NotImplemented，Python会尝试调用b.__radd__(a)
        return wait_combine(self, other)

    def __radd__(self, other: "wait_base") -> typing.Union["wait_combine", "wait_base"]:
        # 实现反向加法，以便在左侧操作数不是类的实例时调用
        # make it possible to use multiple waits with the built-in sum function
        if other == 0:  # type: ignore[comparison-overlap]
            return self
        return self.__add__(other)


WaitBaseT = typing.Union[wait_base, typing.Callable[["RetryCallState"], typing.Union[float, int]]]


class wait_combine(wait_base):
    """Combine several waiting strategies."""

    def __init__(self, *strategies: wait_base) -> None:
        self.wait_funcs = strategies

    def __call__(self, retry_state: "RetryCallState") -> float:
        """多个等待结果求和 ."""
        return sum(x(retry_state=retry_state) for x in self.wait_funcs)
