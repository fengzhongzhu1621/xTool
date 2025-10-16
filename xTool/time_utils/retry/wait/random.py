import random
from typing import TYPE_CHECKING

from xTool.time_utils.time import to_seconds
from xTool.type_hint import time_unit_type

from .base import wait_base

if TYPE_CHECKING:
    from xTool.time_utils.retry.state import RetryCallState

__all__ = [
    "wait_random",
]


class wait_random(wait_base):
    """Wait strategy that waits a random amount of time between min/max."""

    def __init__(self, min: time_unit_type = 0, max: time_unit_type = 1) -> None:  # noqa
        self.wait_random_min = to_seconds(min)
        self.wait_random_max = to_seconds(max)

    def __call__(self, retry_state: "RetryCallState") -> float:
        """随机等待 [min, max) 秒 ."""
        return self.wait_random_min + (random.random() * (self.wait_random_max - self.wait_random_min))
