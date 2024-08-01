import abc
from typing import TYPE_CHECKING, Callable, Union

if TYPE_CHECKING:
    from xTool.time_utils.retry.state import RetryCallState

__all__ = [
    "stop_base",
    "stop_any",
    "stop_all",
    "StopBaseT",
]


class stop_base(abc.ABC):
    """Abstract base class for stop strategies."""

    @abc.abstractmethod
    def __call__(self, retry_state: "RetryCallState") -> bool:
        pass

    def __and__(self, other: "stop_base") -> "stop_all":
        return stop_all(self, other)

    def __or__(self, other: "stop_base") -> "stop_any":
        return stop_any(self, other)


StopBaseT = Union[stop_base, Callable[["RetryCallState"], bool]]


class stop_any(stop_base):
    """Stop if any of the stop condition is valid，任意一个状态是停止的，则结果才是停止的 ."""

    def __init__(self, *stops: stop_base) -> None:
        self.stops = stops

    def __call__(self, retry_state: "RetryCallState") -> bool:
        return any(x(retry_state) for x in self.stops)


class stop_all(stop_base):
    """Stop if all the stop conditions are valid，所有的状态都是停止的，结果才是停止的 ."""

    def __init__(self, *stops: stop_base) -> None:
        self.stops = stops

    def __call__(self, retry_state: "RetryCallState") -> bool:
        return all(x(retry_state) for x in self.stops)
