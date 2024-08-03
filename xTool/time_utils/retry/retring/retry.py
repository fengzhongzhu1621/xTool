import sys
import time
import typing as t
import warnings

from xTool.asynchronous.inspect_utils import is_coroutine_callable
from xTool.time_utils.retry.exceptions import *  # noqa
from xTool.time_utils.retry.log import *  # noqa
from xTool.time_utils.retry.retry import *  # noqa
from xTool.time_utils.retry.state import *  # noqa
from xTool.time_utils.retry.stop import *  # noqa
from xTool.time_utils.retry.wait import *  # noqa
from xTool.type_hint import WrappedFn, WrappedFnReturnT

from .base import BaseRetrying, DoAttempt, DoSleep

__all__ = ["retry"]

try:
    import tornado
except ImportError:
    tornado = None


class Retrying(BaseRetrying):
    """Retrying controller."""

    def __call__(
        self,
        fn: t.Callable[..., WrappedFnReturnT],
        *args: t.Any,
        **kwargs: t.Any,
    ) -> WrappedFnReturnT:
        # 初始化数据
        self.begin()

        # 定义一个初始状态
        retry_state = RetryCallState(retry_object=self, fn=fn, args=args, kwargs=kwargs)
        while True:
            # 添加策略并执行
            do = self.iter(retry_state=retry_state)

            if isinstance(do, DoAttempt):
                # 执行重试任务
                try:
                    result = fn(*args, **kwargs)
                except BaseException:  # noqa: B902
                    retry_state.set_exception(sys.exc_info())  # type: ignore[arg-type]
                else:
                    retry_state.set_result(result)
            elif isinstance(do, DoSleep):
                # 执行休眠
                retry_state.prepare_for_next_attempt()
                self.sleep(do)
            else:
                return do  # type: ignore[no-any-return]


@t.overload
def retry(func: WrappedFn) -> WrappedFn: ...


@t.overload
def retry(
    sleep: t.Callable[[t.Union[int, float]], t.Union[None, t.Awaitable[None]]] = time.sleep,
    stop: "StopBaseT" = stop_never,
    wait: "WaitBaseT" = wait_none(),
    retry: "t.Union[RetryBaseT, tasyncio.retry.RetryBaseT]" = retry_if_exception_type(),
    before: t.Callable[["RetryCallState"], t.Union[None, t.Awaitable[None]]] = before_nothing,
    after: t.Callable[["RetryCallState"], t.Union[None, t.Awaitable[None]]] = after_nothing,
    before_sleep: t.Optional[t.Callable[["RetryCallState"], t.Union[None, t.Awaitable[None]]]] = None,
    reraise: bool = False,
    retry_error_cls: t.Type["RetryError"] = RetryError,
    retry_error_callback: t.Optional[t.Callable[["RetryCallState"], t.Union[t.Any, t.Awaitable[t.Any]]]] = None,
) -> t.Callable[[WrappedFn], WrappedFn]: ...


def retry(*dargs: t.Any, **dkw: t.Any) -> t.Any:
    """Wrap a function with a new `Retrying` object.

    :param dargs: positional arguments passed to Retrying object
    :param dkw: keyword arguments passed to the Retrying object
    """
    # support both @retry and @retry() as valid syntax
    if len(dargs) == 1 and callable(dargs[0]):
        return retry()(dargs[0])
    else:

        def wrap(f: WrappedFn) -> WrappedFn:
            if isinstance(f, retry_base):
                warnings.warn(
                    f"Got retry_base instance ({f.__class__.__name__}) as callable argument, "
                    f"this will probably hang indefinitely (did you mean retry={f.__class__.__name__}(...)?)"
                )
            r: "BaseRetrying"
            if is_coroutine_callable(f):
                r = AsyncRetrying(*dargs, **dkw)
            elif tornado and hasattr(tornado.gen, "is_coroutine_function") and tornado.gen.is_coroutine_function(f):
                r = TornadoRetrying(*dargs, **dkw)
            else:
                r = Retrying(*dargs, **dkw)

            return r.wraps(f)

        return wrap


from xTool.time_utils.retry.async_io import AsyncRetrying  # noqa:E402,I100

if tornado:
    from xTool.time_utils.retry.async_io.tornadoweb import TornadoRetrying
