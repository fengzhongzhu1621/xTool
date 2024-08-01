from typing import TYPE_CHECKING

from .base import stop_base

if TYPE_CHECKING:
    from xTool.time_utils.retry.state import RetryCallState

__all__ = ["stop_after_attempt"]


class stop_after_attempt(stop_base):
    """Stop when the previous attempt >= max_attempt."""

    def __init__(self, max_attempt_number: int) -> None:
        self.max_attempt_number = max_attempt_number

    def __call__(self, retry_state: "RetryCallState") -> bool:
        """超过最大重试此时则停止 ."""
        return retry_state.attempt_number >= self.max_attempt_number
