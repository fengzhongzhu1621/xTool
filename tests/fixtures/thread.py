import asyncio
from contextlib import suppress

import pytest

from xTool.concurrency import thread_pool


@pytest.fixture(params=(thread_pool.threaded, thread_pool.threaded_separate))
def threaded_decorator(request, executor: thread_pool.ThreadPoolExecutor):
    assert executor
    return request.param


@pytest.fixture
def executor(loop: asyncio.AbstractEventLoop):
    pool = thread_pool.ThreadPoolExecutor(8)
    loop.set_default_executor(pool)
    try:
        yield pool
    finally:
        with suppress(Exception):
            pool.shutdown(wait=True)

        pool.shutdown(wait=True)


gen_decos = (
    thread_pool.threaded_iterable,
    thread_pool.threaded_iterable_separate,
)


@pytest.fixture(params=gen_decos)
def iterator_decorator(request):
    return request.param
