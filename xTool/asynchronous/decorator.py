from typing import Any, Awaitable, Callable

from xTool.asynchronous.inspect_utils import is_coroutine_callable


def wrap_to_async_func(
    call: Callable[..., Any],
) -> Callable[..., Awaitable[Any]]:
    """将同步函数转换为协程 ."""
    if is_coroutine_callable(call):
        return call

    async def inner(*args: Any, **kwargs: Any) -> Any:
        return call(*args, **kwargs)

    return inner
