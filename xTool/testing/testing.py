import asyncio
from functools import wraps
from typing import (
    Callable,
)

import orjson as json

_LOOP_FACTORY = Callable[[], asyncio.AbstractEventLoop]


def format_serializer_data(serializer_data):
    return json.loads(json.dumps(serializer_data))


def assert_equal(actual, expect):
    actual = format_serializer_data(actual)
    assert actual == expect


def pytest_async(func):
    """协程装饰器，用于测试协程方法 ."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(func(*args, **kwargs))

    return wrapper
