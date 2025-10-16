from typing import TYPE_CHECKING

from .base import stop_base

if TYPE_CHECKING:
    from xTool.time_utils.retry.state import RetryCallState

__all__ = ["stop_never"]


class _stop_never(stop_base):
    """Never stop."""

    def __call__(self, retry_state: "RetryCallState") -> bool:
        return False


stop_never = _stop_never()
