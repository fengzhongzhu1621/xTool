import time

from asgiref.sync import sync_to_async


def sync_task():
    time.sleep(0.1)
    return True


async def test_sync_to_async(event_loop):
    async_task = sync_to_async(sync_task)
    actual = await async_task()
    expect = True
    assert actual == expect
