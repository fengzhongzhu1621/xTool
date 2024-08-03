import dataclasses
import time
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple, Type

from xTool.compat import dataclass_kwargs
from xTool.type_hint import Future, WrappedFn

from .action import RetryAction

if TYPE_CHECKING:
    import types  # noqa

__all__ = [
    "IterState",
    "RetryCallState",
]


@dataclasses.dataclass(**dataclass_kwargs)
class IterState:
    """状态机中状态节点的上下文 ."""

    actions: List[Callable[["RetryCallState"], Any]] = dataclasses.field(default_factory=list)
    retry_run_result: bool = False
    delay_since_first_attempt: int = 0
    stop_run_result: bool = False
    is_explicit_retry: bool = False

    def reset(self) -> None:
        # 状态包含的所有策略
        self.actions = []
        # 通过重试策略判断是否可以重试的结果
        self.retry_run_result = False
        self.delay_since_first_attempt = 0
        # 是否可以停止的结果
        self.stop_run_result = False
        # 如果执行抛出了 TryAgain 异常，说明必须要进行重试
        self.is_explicit_retry = False


class RetryCallState:
    """State related to a single call wrapped with Retrying，任务执行后的状态，即状态机中的状态节点"""

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
        # 第几次执行任务
        self.attempt_number: int = 1
        #: Last outcome (result or exception) produced by the function
        # 上一次调用的执行结果
        self.outcome: Optional[Future] = None
        #: Timestamp of the last outcome
        self.outcome_timestamp: Optional[float] = None
        #: Time spent sleeping in retries
        # 总的 sleep 耗时
        self.idle_for: float = 0.0
        #: Next action as decided by the retry manager
        # 下一次调用
        self.next_action: Optional[RetryAction] = None
        #: Next sleep time as decided by the retry manager.
        # 当前调用完成后和下一次开始调用的间隔秒数
        self.upcoming_sleep: float = 0.0

    @property
    def seconds_since_start(self) -> Optional[float]:
        """任务执行耗时 ."""
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
