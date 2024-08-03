import functools
import threading
import time
import typing as t
from abc import ABC, abstractmethod

from xTool.time_utils.retry.action import *  # noqa
from xTool.time_utils.retry.exceptions import *  # noqa
from xTool.time_utils.retry.log import *  # noqa
from xTool.time_utils.retry.manager import *  # noqa
from xTool.time_utils.retry.retry import *  # noqa
from xTool.time_utils.retry.state import *  # noqa
from xTool.time_utils.retry.stop import *  # noqa
from xTool.time_utils.retry.wait import *  # noq
from xTool.type_hint import Future, WrappedFn, WrappedFnReturnT

if t.TYPE_CHECKING:
    from xTool.time_utils.retry.retry import RetryBaseT
    from xTool.time_utils.retry.stop import StopBaseT
    from xTool.time_utils.retry.wait import WaitBaseT

__all__ = [
    "DoAttempt",
    "DoSleep",
    "BaseRetrying",
]

NO_RESULT = object()
_unset = object()


class DoAttempt:
    pass


class DoSleep(float):
    pass


def _first_set(first: t.Union[t.Any, object], second: t.Any) -> t.Any:
    return second if first is _unset else first


class BaseRetrying(ABC):
    """重试状态管理器


    是一个状态的实例指针，随着重试进度的推进个，指向不同的状态。
    每个状态都包含一个执行上下文 iter_state 和 统计信息 statistics
    """

    def __init__(
        self,
        sleep: t.Callable[[t.Union[int, float]], None] = time.sleep,
        stop: "StopBaseT" = stop_never,
        wait: "WaitBaseT" = wait_none(),
        retry: "RetryBaseT" = retry_if_exception_type(),  # 存在异常就会chong's
        before: t.Callable[["RetryCallState"], None] = before_nothing,
        after: t.Callable[["RetryCallState"], None] = after_nothing,
        before_sleep: t.Optional[t.Callable[["RetryCallState"], None]] = None,
        reraise: bool = False,
        retry_error_cls: t.Type[RetryError] = RetryError,
        retry_error_callback: t.Optional[t.Callable[["RetryCallState"], t.Any]] = None,
    ):
        self.sleep = sleep
        self.stop = stop
        self.wait = wait
        self.retry = retry
        self.before = before
        self.after = after
        self.before_sleep = before_sleep
        self.reraise = reraise
        self._local = threading.local()
        self.retry_error_cls = retry_error_cls
        self.retry_error_callback = retry_error_callback

    def copy(
        self,
        sleep: t.Union[t.Callable[[t.Union[int, float]], None], object] = _unset,
        stop: t.Union["StopBaseT", object] = _unset,
        wait: t.Union["WaitBaseT", object] = _unset,
        retry: t.Union[retry_base, object] = _unset,
        before: t.Union[t.Callable[["RetryCallState"], None], object] = _unset,
        after: t.Union[t.Callable[["RetryCallState"], None], object] = _unset,
        before_sleep: t.Union[t.Optional[t.Callable[["RetryCallState"], None]], object] = _unset,
        reraise: t.Union[bool, object] = _unset,
        retry_error_cls: t.Union[t.Type[RetryError], object] = _unset,
        retry_error_callback: t.Union[t.Optional[t.Callable[["RetryCallState"], t.Any]], object] = _unset,
    ) -> "BaseRetrying":
        """Copy this object with some parameters changed if needed."""
        return self.__class__(
            sleep=_first_set(sleep, self.sleep),
            stop=_first_set(stop, self.stop),
            wait=_first_set(wait, self.wait),
            retry=_first_set(retry, self.retry),
            before=_first_set(before, self.before),
            after=_first_set(after, self.after),
            before_sleep=_first_set(before_sleep, self.before_sleep),
            reraise=_first_set(reraise, self.reraise),
            retry_error_cls=_first_set(retry_error_cls, self.retry_error_cls),
            retry_error_callback=_first_set(retry_error_callback, self.retry_error_callback),
        )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} object at 0x{id(self):x} ("
            f"stop={self.stop}, "
            f"wait={self.wait}, "
            f"sleep={self.sleep}, "
            f"retry={self.retry}, "
            f"before={self.before}, "
            f"after={self.after})>"
        )

    @property
    def statistics(self) -> t.Dict[str, t.Any]:
        """Return a dictionary of runtime statistics. 返回当前线程的统计信息

        This dictionary will be empty when the controller has never been
        ran. When it is running or has ran previously it should have (but
        may not) have useful and/or informational keys and values when
        running is underway and/or completed.

        .. warning:: The keys in this dictionary **should** be some what
                     stable (not changing), but there existence **may**
                     change between major releases as new statistics are
                     gathered or removed so before accessing keys ensure that
                     they actually exist and handle when they do not.

        .. note:: The values in this dictionary are local to the thread
                  running call (so if multiple threads share the same retrying
                  object - either directly or indirectly) they will each have
                  there own view of statistics they have collected (in the
                  future we may provide a way to aggregate the various
                  statistics from each thread).
        """
        try:
            return self._local.statistics  # type: ignore[no-any-return]
        except AttributeError:
            self._local.statistics = t.cast(t.Dict[str, t.Any], {})
            return self._local.statistics

    @property
    def iter_state(self) -> IterState:
        try:
            return self._local.iter_state  # type: ignore[no-any-return]
        except AttributeError:
            self._local.iter_state = IterState()
            return self._local.iter_state

    def wraps(self, f: WrappedFn) -> WrappedFn:
        """Wrap a function for retrying.

        :param f: A function to wraps for retrying.
        """

        @functools.wraps(f, functools.WRAPPER_ASSIGNMENTS + ("__defaults__", "__kwdefaults__"))
        def wrapped_f(*args: t.Any, **kw: t.Any) -> t.Any:
            # Always create a copy to prevent overwriting the local contexts when
            # calling the same wrapped functions multiple times in the same stack
            copy = self.copy()
            wrapped_f.statistics = copy.statistics  # type: ignore[attr-defined]
            return copy(f, *args, **kw)

        def retry_with(*args: t.Any, **kwargs: t.Any) -> WrappedFn:
            return self.copy(*args, **kwargs).wraps(f)

        # Preserve attributes
        wrapped_f.retry = self  # type: ignore[attr-defined]
        wrapped_f.retry_with = retry_with  # type: ignore[attr-defined]
        wrapped_f.statistics = {}  # type: ignore[attr-defined]

        return wrapped_f  # type: ignore[return-value]

    def begin(self) -> None:
        """初始化数据 ."""
        self.statistics.clear()
        self.statistics["start_time"] = time.monotonic()
        self.statistics["attempt_number"] = 1
        self.statistics["idle_for"] = 0

    def _add_action_func(self, fn: t.Callable[..., t.Any]) -> None:
        self.iter_state.actions.append(fn)

    def _run_retry(self, retry_state: "RetryCallState") -> None:
        """计算是否可以重试 ."""
        self.iter_state.retry_run_result = self.retry(retry_state)

    def _run_wait(self, retry_state: "RetryCallState") -> None:
        """计算重试间隔秒数 ."""
        if self.wait:
            sleep = self.wait(retry_state)
        else:
            sleep = 0.0

        retry_state.upcoming_sleep = sleep

    def _run_stop(self, retry_state: "RetryCallState") -> None:
        """计算是否可以停止 ."""
        # 记录任务执行耗时
        self.statistics["delay_since_first_attempt"] = retry_state.seconds_since_start
        self.iter_state.stop_run_result = self.stop(retry_state)

    def iter(self, retry_state: "RetryCallState") -> t.Union[DoAttempt, DoSleep, t.Any]:  # noqa
        """添加策略并执行 ."""
        # 添加策略
        self._begin_iter(retry_state)
        result = None
        # 执行策略
        for action in self.iter_state.actions:
            result = action(retry_state)
        return result

    def _begin_iter(self, retry_state: "RetryCallState") -> None:  # noqa
        self.iter_state.reset()

        # 获得上一次调用的执行结果
        fut = retry_state.outcome
        # 判断是否是未执行状态
        if fut is None:
            # 重试任务前打印开始日志
            if self.before is not None:
                self._add_action_func(self.before)
            # 执行任务
            self._add_action_func(lambda rs: DoAttempt())
            return
        # 如果任务已经执行且抛出了 TryAgain 异常
        self.iter_state.is_explicit_retry = fut.failed and isinstance(fut.exception(), TryAgain)
        if not self.iter_state.is_explicit_retry:
            # 计算是否可以重试
            self._add_action_func(self._run_retry)
        # 添加任务执行后的后置操作
        self._add_action_func(self._post_retry_check_actions)

    def _post_retry_check_actions(self, retry_state: "RetryCallState") -> None:
        """添加任务执行后的后置操作 ."""
        # 如果不可以重试，则直接获得上一次的执行结果
        if not (self.iter_state.is_explicit_retry or self.iter_state.retry_run_result):
            self._add_action_func(lambda rs: rs.outcome.result())
            return

        # 添加重试后的动作
        if self.after is not None:
            self._add_action_func(self.after)

        # 计算重试间隔秒数
        self._add_action_func(self._run_wait)
        # 计算是否可以停止
        self._add_action_func(self._run_stop)
        #
        self._add_action_func(self._post_stop_check_actions)

    def _post_stop_check_actions(self, retry_state: "RetryCallState") -> None:
        if self.iter_state.stop_run_result:
            # 添加失败回调
            if self.retry_error_callback:
                self._add_action_func(self.retry_error_callback)
                return

            # 重新抛出异常
            def exc_check(rs: "RetryCallState") -> None:
                fut = t.cast(Future, rs.outcome)
                retry_exc = self.retry_error_cls(fut)
                if self.reraise:
                    raise retry_exc.reraise()
                raise retry_exc from fut.exception()

            self._add_action_func(exc_check)
            return

        def next_action(rs: "RetryCallState") -> None:
            # 当前调用完成后和下一次开始调用的间隔秒数
            sleep = rs.upcoming_sleep
            rs.next_action = RetryAction(sleep)
            rs.idle_for += sleep
            self.statistics["idle_for"] += sleep
            self.statistics["attempt_number"] += 1

        # 切换到下一次执行状态
        self._add_action_func(next_action)

        # 打印上一次的执行结果
        if self.before_sleep is not None:
            self._add_action_func(self.before_sleep)

        # 开始休眠
        self._add_action_func(lambda rs: DoSleep(rs.upcoming_sleep))

    def __iter__(self) -> t.Generator[AttemptManager, None, None]:
        # 初始化数据
        self.begin()

        # 定义一个初始状态
        retry_state = RetryCallState(self, fn=None, args=(), kwargs={})

        while True:
            # 执行状态关联的策略
            do = self.iter(retry_state=retry_state)
            if isinstance(do, DoAttempt):
                # 此状态可以执行重试任务
                yield AttemptManager(retry_state=retry_state)
            elif isinstance(do, DoSleep):
                # 此状态需要休眠，需要为下一次重试重置状态
                # 可以理解为当前指针指向下一个状态
                retry_state.prepare_for_next_attempt()
                self.sleep(do)
            else:
                break

    @abstractmethod
    def __call__(
        self,
        fn: t.Callable[..., WrappedFnReturnT],
        *args: t.Any,
        **kwargs: t.Any,
    ) -> WrappedFnReturnT:
        pass
