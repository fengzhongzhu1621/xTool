import functools


class CallableContextManager:
    """将上下文管理器转换为装饰器 ."""

    def __call__(self, fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)

        return inner
