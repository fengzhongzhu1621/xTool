from typing import TYPE_CHECKING

from .base import stop_base

if TYPE_CHECKING:
    import threading

    from xTool.time_utils.retry.state import RetryCallState

__all__ = ["stop_when_event_set"]


class stop_when_event_set(stop_base):
    """Stop when the given event is set."""

    def __init__(self, event: "threading.Event") -> None:
        self.event = event

    def __call__(self, retry_state: "RetryCallState") -> bool:
        """信号标记设置时，需要切换到停止状态 ."""
        # 检查信号标志是否已经被设置。
        # 当一个线程设置了这个信号标志，任何其他线程都可以通过调用is_set()方法来检查这个标志是否已经被设置。
        # 如果标志被设置，is_set()将返回True，否则返回False。
        return self.event.is_set()
