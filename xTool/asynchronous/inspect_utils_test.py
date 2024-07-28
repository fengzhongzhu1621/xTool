import functools

from xTool.asynchronous.inspect_utils import is_coroutine_callable


def test_is_coroutine_callable() -> None:
    async def async_func() -> None:
        pass

    def sync_func() -> None:
        pass

    class AsyncClass:
        async def __call__(self) -> None:
            pass

    class SyncClass:
        def __call__(self) -> None:
            pass

    lambda_fn = lambda: None  # noqa: E731

    partial_async_func = functools.partial(async_func)
    partial_sync_func = functools.partial(sync_func)
    partial_async_class = functools.partial(AsyncClass().__call__)
    partial_sync_class = functools.partial(SyncClass().__call__)
    partial_lambda_fn = functools.partial(lambda_fn)

    assert is_coroutine_callable(async_func) is True
    assert is_coroutine_callable(sync_func) is False
    assert is_coroutine_callable(AsyncClass) is False
    assert is_coroutine_callable(AsyncClass()) is True
    assert is_coroutine_callable(SyncClass) is False
    assert is_coroutine_callable(SyncClass()) is False
    assert is_coroutine_callable(lambda_fn) is False

    assert is_coroutine_callable(partial_async_func) is True
    assert is_coroutine_callable(partial_sync_func) is False
    assert is_coroutine_callable(partial_async_class) is True
    assert is_coroutine_callable(partial_sync_class) is False
    assert is_coroutine_callable(partial_lambda_fn) is False
