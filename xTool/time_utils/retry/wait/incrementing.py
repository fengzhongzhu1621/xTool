from typing import TYPE_CHECKING

from xTool.constants import MAX_WAIT
from xTool.time_utils.time import to_seconds
from xTool.type_hint import time_unit_type

from .base import wait_base

if TYPE_CHECKING:
    from xTool.time_utils.retry.state import RetryCallState

__all__ = [
    "wait_incrementing",
    "PowersOf",
]


def PowersOf(logbase, count, lower=0, include_zero=True):
    """Returns a list of count powers of logbase (from logbase**lower)."""
    if not include_zero:
        return [logbase**i for i in range(lower, count + lower)]
    else:
        return [0] + [logbase**i for i in range(lower, count + lower)]


class wait_incrementing(wait_base):
    """Wait an incremental amount of time after each attempt.

    Starting at a starting value and incrementing by a value for each attempt
    (and restricting the upper limit to some maximum value).
    """

    def __init__(
        self,
        start: time_unit_type = 0,
        increment: time_unit_type = 100,  # 倍数
        max: time_unit_type = MAX_WAIT,  # noqa
    ) -> None:
        self.start = to_seconds(start)
        self.increment = to_seconds(increment)
        self.max = to_seconds(max)

    def __call__(self, retry_state: "RetryCallState") -> float:
        result = self.start + (self.increment * (retry_state.attempt_number - 1))
        return max(0, min(result, self.max))
