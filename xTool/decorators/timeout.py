import asyncio
from functools import wraps


def timeout(value):
    def decorator(func):
        # 如果 func 是一个 协程函数 则返回 True
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Function is not a coroutine function")

        @wraps(func)
        async def wrap(*args, **kwargs):
            return await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=value,
            )

        return wrap

    return decorator
