import typing

from .base import retry_base

if typing.TYPE_CHECKING:
    from xTool.time_utils.retry.state import RetryCallState

__all__ = [
    "retry_never",
]


class _retry_never(retry_base):
    """Retry strategy that never rejects any result."""

    def __call__(self, retry_state: "RetryCallState") -> bool:
        return False


retry_never = _retry_never()
