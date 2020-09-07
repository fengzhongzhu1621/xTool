# -*- coding: utf-8 -*-

import asyncio
import gc
import os
import threading
import time
import weakref
from contextlib import suppress
import concurrent
from concurrent.futures import ThreadPoolExecutor

import pytest
from async_timeout import timeout

from xTool import thread_pool

try:
    import contextvars
except ImportError:
    contextvars = None


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


async def test_future_gc(loop):
    pool = ThreadPoolExecutor(2)
    event = threading.Event()

    async def run():
        future = loop.create_future()

        cfuture = pool.submit(time.sleep, 0.5)

        cfuture.add_done_callback(
            lambda *_: loop.call_soon_threadsafe(
                future.set_result, True,
            ),
        )

        weakref.finalize(cfuture, lambda *_: event.set())
        await future

    await run()

    gc.collect()
    event.wait(1)

    assert event.is_set()


async def test_threaded(threaded_decorator, timer):
    sleep = threaded_decorator(time.sleep)

    async with timeout(5):
        with timer(1):
            await asyncio.gather(
                sleep(1),
                sleep(1),
                sleep(1),
                sleep(1),
                sleep(1),
            )


async def test_threaded_exc(threaded_decorator):
    @threaded_decorator
    def worker():
        raise Exception

    async with timeout(1):
        number = 90

        done, _ = await asyncio.wait([worker() for _ in range(number)])
        for task in done:
            with pytest.raises(Exception):
                task.result()


async def test_future_already_done(executor: thread_pool.ThreadPoolExecutor):
    futures = []

    async with timeout(10):
        for _ in range(10):
            futures.append(executor.submit(time.sleep, 0.1))

        for future in futures:
            future.set_exception(asyncio.CancelledError())

        with pytest.raises(Exception):
            await asyncio.gather(*futures, return_exceptions=True)


async def test_failed_future_already_done(executor):
    futures = []

    def exc():
        time.sleep(0.1)
        raise Exception

    async with timeout(10):
        for _ in range(10):
            futures.append(executor.submit(exc))

        for future in futures:
            future.set_exception(asyncio.CancelledError())

        with pytest.raises(Exception):
            await asyncio.gather(*futures, return_exceptions=True)


async def test_simple(threaded_decorator, loop, timer):
    sleep = threaded_decorator(time.sleep)

    async with timeout(2):
        with timer(1):
            await asyncio.gather(
                sleep(1),
                sleep(1),
                sleep(1),
                sleep(1),
            )


gen_decos = (
    thread_pool.threaded_iterable,
    thread_pool.threaded_iterable_separate,
)


@pytest.fixture(params=gen_decos)
def iterator_decorator(request):
    return request.param


async def test_threaded_generator(loop, timer):
    @thread_pool.threaded
    def arange(*args):
        return (yield from range(*args))

    async with timeout(10):
        count = 10

        result = []
        agen = arange(count)
        async for item in agen:
            result.append(item)

        assert result == list(range(count))


async def test_threaded_generator_max_size(iterator_decorator, loop, timer):
    @iterator_decorator(max_size=1)
    def arange(*args):
        return (yield from range(*args))

    async with timeout(2):
        arange2 = thread_pool.threaded_iterable(max_size=1)(range)

        count = 10

        result = []
        agen = arange(count)
        async for item in agen:
            result.append(item)

        assert result == list(range(count))

        result = []
        agen = arange2(count)
        async for item in agen:
            result.append(item)

        assert result == list(range(count))


async def test_threaded_generator_exception(iterator_decorator, loop, timer):
    @iterator_decorator
    def arange(*args):
        yield from range(*args)
        raise ZeroDivisionError

    async with timeout(2):
        count = 10

        result = []
        agen = arange(count)

        with pytest.raises(ZeroDivisionError):
            async for item in agen:
                result.append(item)

        assert result == list(range(count))


async def test_threaded_generator_close(iterator_decorator, loop, timer):
    stopped = False

    @iterator_decorator(max_size=2)
    def noise():
        nonlocal stopped

        try:
            while True:
                yield os.urandom(32)
        finally:
            stopped = True

    async with timeout(2):
        counter = 0

        async with noise() as gen:
            async for _ in gen:     # NOQA
                counter += 1
                if counter > 9:
                    break

        wait_counter = 0
        while not stopped and wait_counter < 5:
            await asyncio.sleep(1)
            wait_counter += 1

        assert stopped


async def test_threaded_generator_close_cm(iterator_decorator, loop, timer):
    stopped = threading.Event()

    @iterator_decorator(max_size=1)
    def noise():
        nonlocal stopped

        try:
            while True:
                yield os.urandom(32)
        finally:
            stopped.set()

    async with timeout(2):
        async with noise() as gen:
            counter = 0
            async for _ in gen:     # NOQA
                counter += 1
                if counter > 9:
                    break

        stopped.wait(timeout=5)
        assert stopped.is_set()


async def test_threaded_generator_non_generator_raises(
        iterator_decorator, loop, timer
):
    @iterator_decorator()
    def errored():
        raise RuntimeError("Aaaaaaaa")

    async with timeout(2):
        with pytest.raises(RuntimeError):
            async for _ in errored():       # NOQA
                pass


async def test_threaded_generator_func_raises(iterator_decorator, loop, timer):
    @iterator_decorator
    def errored(val):
        if val:
            raise RuntimeError("Aaaaaaaa")

        yield

    async with timeout(2):
        with pytest.raises(RuntimeError):
            async for _ in errored(True):    # NOQA
                pass


@pytest.mark.skipif(contextvars is None, reason="no contextvars support")
async def test_context_vars(threaded_decorator, loop):
    ctx_var = contextvars.ContextVar("test")

    @threaded_decorator
    def test(arg):
        value = ctx_var.get()
        assert value == arg * arg

    futures = []

    for i in range(8):
        ctx_var.set(i * i)
        futures.append(test(i))

    await asyncio.gather(*futures)


async def test_wait_coroutine_sync(threaded_decorator, loop):
    result = 0

    async def coro():
        nonlocal result
        await asyncio.sleep(1)
        result = 1

    @threaded_decorator
    def test():
        thread_pool.sync_wait_coroutine(loop, coro)

    await test()
    assert result == 1


async def test_wait_coroutine_sync_exc(threaded_decorator, loop):
    result = 0

    async def coro():
        nonlocal result
        await asyncio.sleep(1)
        result = 1
        raise RuntimeError("Test")

    @threaded_decorator
    def test():
        thread_pool.sync_wait_coroutine(loop, coro)

    with pytest.raises(RuntimeError):
        await test()

    assert result == 1
