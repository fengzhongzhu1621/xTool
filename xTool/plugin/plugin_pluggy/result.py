from __future__ import annotations

from typing import Callable, Generator, Generic, Union, cast, final

from xTool.type_hint import ExcInfo, T

from .type_hint import ResultType


@final
class Result(Generic[ResultType]):
    """An object used to inspect and set the result in a :ref:`hook wrapper
    <hookwrappers>`."""

    __slots__ = ("_result", "_exception", "_traceback")

    def __init__(
        self,
        result: ResultType | None,
        exception: BaseException | None,
    ) -> None:
        """:meta private:"""
        # 用于存储结果
        self._result = result
        # 用于存储异常
        self._exception = exception
        # 用于存储异常的追踪信息。
        # Exception __traceback__ is mutable, this keeps the original.
        self._traceback = exception.__traceback__ if exception is not None else None

    @property
    def excinfo(self) -> ExcInfo | None:
        """返回一个包含异常信息的元组，如果没有异常发生，则返回 None"""
        exc = self._exception
        if exc is None:
            return None
        else:
            return (type(exc), exc, self._traceback)

    @property
    def exception(self) -> BaseException | None:
        """返回存储的异常对象，如果没有异常发生，则返回 None"""
        return self._exception

    @classmethod
    def from_call(cls, func: Callable[[], ResultType]) -> Result[ResultType]:
        """用于从函数调用中创建 Result 实例，且忽略堆栈信息。"""
        # __tracebackhide__ 是一个特殊的属性，用于控制在异常处理中是否显示 traceback（追踪记录）。
        # 这个属性通常用在测试框架中，以便在测试失败时隐藏某些特定的 traceback 信息，从而使得错误报告更加清晰。
        __tracebackhide__ = True
        result = exception = None
        try:
            result = func()
        except BaseException as exc:
            exception = exc
        return cls(result, exception)

    def force_result(self, result: ResultType) -> None:
        """Force the result(s) to ``result``.强制将结果设置为指定的值，并清除任何异常信息。

        If the hook was marked as a ``firstresult`` a single value should
        be set, otherwise set a (modified) list of results. Any exceptions
        found during invocation will be deleted.

        This overrides any previous result or exception.
        """
        self._result = result
        self._exception = None
        self._traceback = None

    def force_exception(self, exception: BaseException) -> None:
        """Force the result to fail with ``exception``. 强制将结果设置为抛出指定的异常，并清除任何之前的结果。

        This overrides any previous result or exception.

        .. versionadded:: 1.1.0
        """
        self._result = None
        self._exception = exception
        self._traceback = exception.__traceback__ if exception is not None else None

    def get_result(self) -> ResultType:
        """Get the result(s) for this hook call. 获取钩子调用的结果。
        如果钩子被标记为 firstresult，则只返回单个值；否则返回一个结果列表。如果有异常发生，则重新抛出该异常。

        If the hook was marked as a ``firstresult`` only a single value
        will be returned, otherwise a list of results.
        """
        __tracebackhide__ = True
        exc = self._exception
        tb = self._traceback
        if exc is None:
            return cast(ResultType, self._result)
        else:
            raise exc.with_traceback(tb)


_HookImplFunction = Callable[..., Union[T, Generator[None, Result[T], None]]]
