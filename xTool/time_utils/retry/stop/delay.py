from typing import TYPE_CHECKING

from xTool.time_utils.time import to_seconds
from xTool.type_hint import time_unit_type

from .base import stop_base

if TYPE_CHECKING:
    from xTool.time_utils.retry.state import RetryCallState

__all__ = ["stop_before_delay", "stop_after_delay"]


class stop_before_delay(stop_base):
    """
    Stop right before the next attempt would take place after the time from the first attempt >= limit.

    Most useful when you are using with a `wait` function like wait_random_exponential, but need to make
    sure that the max_delay is not exceeded.
    """

    def __init__(self, max_delay: time_unit_type) -> None:
        self.max_delay = to_seconds(max_delay)

    def __call__(self, retry_state: "RetryCallState") -> bool:
        """下一次执行间隔前的执行时间过长，触发超时停止 ."""
        if retry_state.seconds_since_start is None:
            raise RuntimeError("__call__() called but seconds_since_start is not set")
        return retry_state.seconds_since_start + retry_state.upcoming_sleep >= self.max_delay


class stop_after_delay(stop_base):
    """
    Stop when the time from the first attempt >= limit.

    Note: `max_delay` will be exceeded, so when used with a `wait`, the actual total delay will be greater
    than `max_delay` by some of the final sleep period before `max_delay` is exceeded.

    If you need stricter timing with waits, consider `stop_before_delay` instead.
    """

    def __init__(self, max_delay: time_unit_type) -> None:
        self.max_delay = to_seconds(max_delay)

    def __call__(self, retry_state: "RetryCallState") -> bool:
        """执行时间过长，触发超时停止 ."""
        # 判断重试的耗时
        if retry_state.seconds_since_start is None:
            raise RuntimeError("__call__() called but seconds_since_start is not set")
        return retry_state.seconds_since_start >= self.max_delay
