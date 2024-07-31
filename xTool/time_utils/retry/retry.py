import sys
import time
from typing import TYPE_CHECKING, Any, Optional, Tuple, Type

from xTool.type_hint import Future, WrappedFn

from .action import RetryAction

if TYPE_CHECKING:
    import types  # noqa

# sys.maxsize:
# An integer giving the maximum value a variable of type Py_ssize_t can take.
MAX_WAIT = sys.maxsize / 2


def PowersOf(logbase, count, lower=0, include_zero=True):
    """Returns a list of count powers of logbase (from logbase**lower)."""
    if not include_zero:
        return [logbase**i for i in range(lower, count + lower)]
    else:
        return [0] + [logbase**i for i in range(lower, count + lower)]


class RetryCallState:
    """State related to a single call wrapped with Retrying."""

    def __init__(
        self,
        retry_object,
        fn: Optional[WrappedFn],
        args: Any,
        kwargs: Any,
    ) -> None:
        #: Retry call start timestamp
        self.start_time = time.monotonic()
        #: Retry manager object
        self.retry_object = retry_object
        #: Function wrapped by this retry call
        self.fn = fn
        #: Arguments of the function wrapped by this retry call
        self.args = args
        #: Keyword arguments of the function wrapped by this retry call
        self.kwargs = kwargs

        #: The number of the current attempt
        self.attempt_number: int = 1
        #: Last outcome (result or exception) produced by the function
        self.outcome: Optional[Future] = None
        #: Timestamp of the last outcome
        self.outcome_timestamp: Optional[float] = None
        #: Time spent sleeping in retries
        self.idle_for: float = 0.0
        #: Next action as decided by the retry manager
        self.next_action: Optional[RetryAction] = None
        #: Next sleep time as decided by the retry manager.
        self.upcoming_sleep: float = 0.0

    @property
    def seconds_since_start(self) -> Optional[float]:
        if self.outcome_timestamp is None:
            return None
        return self.outcome_timestamp - self.start_time

    def prepare_for_next_attempt(self) -> None:
        self.outcome = None
        self.outcome_timestamp = None
        self.attempt_number += 1
        self.next_action = None

    def set_result(self, val: Any) -> None:
        ts = time.monotonic()
        fut = Future(self.attempt_number)
        fut.set_result(val)
        self.outcome, self.outcome_timestamp = fut, ts

    def set_exception(
        self,
        exc_info: Tuple[Type[BaseException], BaseException, "types.TracebackType| None"],
    ) -> None:
        ts = time.monotonic()
        fut = Future(self.attempt_number)
        fut.set_exception(exc_info[1])
        self.outcome, self.outcome_timestamp = fut, ts

    def __repr__(self) -> str:
        if self.outcome is None:
            result = "none yet"
        elif self.outcome.failed:
            exception = self.outcome.exception()
            result = f"failed ({exception.__class__.__name__} {exception})"
        else:
            result = f"returned {self.outcome.result()}"

        slept = float(round(self.idle_for, 2))
        clsname = self.__class__.__name__
        return f"<{clsname} {id(self)}: attempt #{self.attempt_number}; slept for {slept}; last result: {result}>"
