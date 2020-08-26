# -*- coding: utf-8 -*-

import asyncio
import pytest
from xTool.decorators import timeout


async def test_simple(loop):
    @timeout.timeout(0)
    async def test():
        await asyncio.sleep(0.05)

    with pytest.raises(asyncio.TimeoutError):
        await test()


async def test_already_done_2(loop):
    @timeout.timeout(0.5)
    async def test(sec):
        await asyncio.sleep(sec)

    task = loop.create_task(test(10))
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task


async def test_non_coroutine(loop):
    with pytest.raises(TypeError):
        @timeout.timeout(0)
        def test():
            return
