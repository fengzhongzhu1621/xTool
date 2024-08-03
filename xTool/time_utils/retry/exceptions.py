from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    from xTool.type_hint import Future

__all__ = [
    "TryAgain",
    "RetryError",
]


class TryAgain(Exception):
    """Always retry the executed function when raised."""


class RetryError(Exception):
    """Encapsulates the last attempt instance right before giving up."""

    def __init__(self, last_attempt: "Future") -> None:
        self.last_attempt = last_attempt
        super().__init__(last_attempt)

    def reraise(self) -> NoReturn:
        if self.last_attempt.failed:
            raise self.last_attempt.result()
        raise self

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.last_attempt}]"
