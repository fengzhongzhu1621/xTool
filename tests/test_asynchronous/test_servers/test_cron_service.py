import asyncio

from xTool.asynchronous.servers.cron import CronService


def test_str_representation():
    class FooCronService(CronService):
        pass

    svc = FooCronService()

    async def runner():
        pass

    svc.register(runner, "* * * * * *")
    assert str(svc) == "FooCronService(CronCallback(runner): * * * * * *)"


def test_cron(loop):
    counter = 0

    async def callback():
        nonlocal counter
        counter += 1
        await asyncio.sleep(0)

    svc = CronService()

    svc.register(callback, spec="* * * * * *")

    async def assert_counter():
        nonlocal counter, svc

        await svc.start()

        counter = 0
        await asyncio.sleep(1)
        assert counter == 1

        await svc.stop()

        await asyncio.sleep(1)
        assert counter == 1

    loop.run_until_complete(asyncio.wait_for(assert_counter(), timeout=10))


def test_register(loop):
    counter = 0

    async def callback():
        nonlocal counter
        counter += 1
        await asyncio.sleep(0)

    svc = CronService()

    svc.register(callback, spec="* * * * * *")
    svc.register(callback, spec="* * * * * */2")  # even second
    svc.register(callback, spec="* * * * * *")

    async def assert_counter():
        nonlocal counter, svc

        await svc.start()

        counter = 0
        await asyncio.sleep(2)
        assert counter == 5

        await svc.stop()

        await asyncio.sleep(1)
        assert counter == 5

    loop.run_until_complete(asyncio.wait_for(assert_counter(), timeout=10))
