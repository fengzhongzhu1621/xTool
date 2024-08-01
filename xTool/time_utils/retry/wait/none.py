from typing import TYPE_CHECKING

from xTool.time_utils.time import to_seconds
from xTool.type_hint import time_unit_type

from .base import wait_base

if TYPE_CHECKING:
    from xTool.time_utils.retry.state import RetryCallState

__all__ = ["wait_fixed", "wait_none"]


class wait_fixed(wait_base):
    """Wait strategy that waits a fixed amount of time between each retry."""

    def __init__(self, wait: time_unit_type) -> None:
        self.wait_fixed = to_seconds(wait)

    def __call__(self, retry_state: "RetryCallState") -> float:
        return self.wait_fixed


class wait_none(wait_fixed):
    """Wait strategy that doesn't wait at all before retrying."""

    def __init__(self) -> None:
        super().__init__(0)
