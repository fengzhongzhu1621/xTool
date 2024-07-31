from typing import TYPE_CHECKING, Optional, Type

if TYPE_CHECKING:
    import types

    from xTool.time_utils.retry.state import RetryCallState


class AttemptManager:
    """Manage attempt context."""

    def __init__(self, retry_state: "RetryCallState"):
        self.retry_state = retry_state

    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional["types.TracebackType"],
    ) -> Optional[bool]:
        if exc_type is not None and exc_value is not None:
            self.retry_state.set_exception((exc_type, exc_value, traceback))
            return True  # Swallow exception.
        else:
            # We don't have the result, actually.
            self.retry_state.set_result(None)
            return None
