import typing

from .base import retry_base

if typing.TYPE_CHECKING:
    from xTool.time_utils.retry.state import RetryCallState

__all__ = [
    "retry_always",
]


class _retry_always(retry_base):
    """Retry strategy that always rejects any result."""

    def __call__(self, retry_state: "RetryCallState") -> bool:
        return True


retry_always = _retry_always()
