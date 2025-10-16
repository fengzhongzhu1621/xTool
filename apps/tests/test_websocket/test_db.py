import time

import pytest
from asgiref.sync import SyncToAsync


def sync_function():
    print("Running in a synchronous context")
    time.sleep(1)
    print("Synchronous context finished")
    return "Result from synchronous function"


@pytest.mark.asyncio
async def test_async_function():
    """测试将同步函数转换为异步函数执行 ."""
    print("Running in an asynchronous context")
    # 将同步函数转换为异步函数
    wrapped_sync_function = SyncToAsync(sync_function)
    result = await wrapped_sync_function()
    print("Asynchronous context finished")
    return result
