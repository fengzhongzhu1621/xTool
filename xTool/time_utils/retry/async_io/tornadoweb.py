import sys
import typing

from tornado import gen

from xTool.time_utils.retry.retring.base import BaseRetrying, DoAttempt, DoSleep, RetryCallState

if typing.TYPE_CHECKING:
    from tornado.concurrent import Future

_RetValT = typing.TypeVar("_RetValT")

__all__ = ["TornadoRetrying"]


class TornadoRetrying(BaseRetrying):
    def __init__(
        self,
        sleep: "typing.Callable[[float], Future[None]]" = gen.sleep,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(**kwargs)
        self.sleep = sleep

    @gen.coroutine  # type: ignore[misc]
    def __call__(
        self,
        fn: "typing.Callable[..., typing.Union[typing.Generator[typing.Any, typing.Any, _RetValT], Future[_RetValT]]]",
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> "typing.Generator[typing.Any, typing.Any, _RetValT]":
        self.begin()

        retry_state = RetryCallState(retry_object=self, fn=fn, args=args, kwargs=kwargs)
        while True:
            do = self.iter(retry_state=retry_state)
            if isinstance(do, DoAttempt):
                try:
                    result = yield fn(*args, **kwargs)
                except BaseException:  # noqa: B902
                    retry_state.set_exception(sys.exc_info())  # type: ignore[arg-type]
                else:
                    retry_state.set_result(result)
            elif isinstance(do, DoSleep):
                retry_state.prepare_for_next_attempt()
                yield self.sleep(do)
            else:
                raise gen.Return(do)
