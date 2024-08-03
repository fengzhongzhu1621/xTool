import abc
import typing

if typing.TYPE_CHECKING:
    from xTool.time_utils.retry.state import RetryCallState

__all__ = [
    "retry_base",
    "retry_any",
    "retry_all",
    "RetryBaseT",
]


class retry_base(abc.ABC):
    """Abstract base class for retry strategies."""

    @abc.abstractmethod
    def __call__(self, retry_state: "RetryCallState") -> bool:
        pass

    def __and__(self, other: "retry_base") -> "retry_all":
        return other.__rand__(self)

    def __rand__(self, other: "retry_base") -> "retry_all":
        return retry_all(other, self)

    def __or__(self, other: "retry_base") -> "retry_any":
        return other.__ror__(self)

    def __ror__(self, other: "retry_base") -> "retry_any":
        return retry_any(other, self)


RetryBaseT = typing.Union[retry_base, typing.Callable[["RetryCallState"], bool]]


class retry_any(retry_base):
    """Retries if any of the retries condition is valid."""

    def __init__(self, *retries: retry_base) -> None:
        self.retries = retries

    def __call__(self, retry_state: "RetryCallState") -> bool:
        return any(r(retry_state) for r in self.retries)


class retry_all(retry_base):
    """Retries if all the retries condition are valid."""

    def __init__(self, *retries: retry_base) -> None:
        self.retries = retries

    def __call__(self, retry_state: "RetryCallState") -> bool:
        return all(r(retry_state) for r in self.retries)
