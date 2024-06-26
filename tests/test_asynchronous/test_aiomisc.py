import asyncio
from random import shuffle

import pytest

from xTool.asynchronous import aiomisc


async def test_awaitable_decorator(loop):
    future = loop.create_future()
    loop.call_soon(future.set_result, 1)

    @aiomisc.awaitable
    def no_awaitable():
        return 1

    @aiomisc.awaitable
    def pass_future():
        return future

    @aiomisc.awaitable
    async def coro():
        return await future

    assert pass_future() is future

    assert (await coro()) == 1
    assert (await pass_future()) == 1
    assert (await no_awaitable()) == 1

    async def do_callback(func, *args):
        awaitable_func = aiomisc.awaitable(func)

        return await awaitable_func(*args)

    await do_callback(asyncio.sleep, 0.01)
    await do_callback(lambda: 45)


def test_shield(loop):
    results = []

    @aiomisc.shield
    async def coro():
        nonlocal results
        await asyncio.sleep(0.5)
        results.append(True)

    async def main(loop):
        task = loop.create_task(coro())
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        finally:
            await asyncio.sleep(1)

    loop.run_until_complete(asyncio.wait_for(main(loop), timeout=10))

    assert results == [True]


async def test_cancel_tasks_wait(loop):
    done, pending = await asyncio.wait([asyncio.sleep(i) for i in range(10)], timeout=5)

    # 取消任务
    await aiomisc.cancel_tasks(pending)

    for task in pending:
        assert task.done()

        with pytest.raises(asyncio.CancelledError):
            await task


async def test_cancel_tasks(loop):
    semaphore = asyncio.Semaphore(10)

    # 创建20个资源获取task
    tasks = [loop.create_task(semaphore.acquire()) for _ in range(20)]
    done, pending = await asyncio.wait(tasks, timeout=0.5)

    for task in pending:
        assert not task.done()
    for task in done:
        assert task.done()

    # 取消任务
    await aiomisc.cancel_tasks(pending)

    assert len(done) == 10
    assert len(pending) == 10

    for task in pending:
        assert task.done()

        with pytest.raises(asyncio.CancelledError):
            await task


async def test_cancel_tasks_futures(loop):
    counter = 0

    def create_future():
        nonlocal counter

        future = loop.create_future()
        counter += 1

        # 将future标为执行完成，并且设置result的值
        if counter <= 10:
            loop.call_soon(future.set_result, True)

        return future

    tasks = [create_future() for _ in range(20)]

    # 用于执行call_soon中的任务
    await asyncio.sleep(0.5)

    done = tasks[:10]
    pending = tasks[10:]

    for task in pending:
        assert not task.done()

    for task in done:
        assert task.done()

    await aiomisc.cancel_tasks(pending)

    assert len(done) == 10
    assert len(pending) == 10

    for task in pending:
        assert isinstance(task, asyncio.Future) is True
        assert task.done()

        with pytest.raises(asyncio.CancelledError):
            await task


async def test_cancel_tasks_futures_and_tasks(loop):
    tasks = []

    counter = 0

    def create_future():
        nonlocal counter

        future = loop.create_future()
        counter += 1

        if counter <= 10:
            loop.call_soon(future.set_result, True)

        return future

    for _ in range(20):
        tasks.append(create_future())

    semaphore = asyncio.Semaphore(10)

    for _ in range(20):
        tasks.append(loop.create_task(semaphore.acquire()))

    shuffle(tasks)

    done, pending = await asyncio.wait(tasks, timeout=0.5)

    for task in pending:
        assert not task.done()

    for task in done:
        assert task.done()

    # 取消有semaphore的任务
    await aiomisc.cancel_tasks(pending)

    assert len(done) == 20
    assert len(pending) == 20

    for task in pending:
        assert task.done()

        with pytest.raises(asyncio.CancelledError):
            await task
