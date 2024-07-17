import datetime
import time

import pytest

from xTool.asynchronous.aiocron import asyncio, crontab


class CustomError(Exception):
    pass


def test_str():
    loop = asyncio.new_event_loop()

    @crontab("* * * * * *", loop=loop)
    def t():
        pass

    assert "* * * * *" in str(t)


def test_sleep():
    loop = asyncio.new_event_loop()

    # future = asyncio.Future(loop=loop)

    @crontab("* * * * * *", loop=loop)
    async def t():
        print(datetime.datetime.now(), "t.begin")
        await asyncio.sleep(3)
        print(datetime.datetime.now(), "t.end")

    # t.start()
    # loop.run_until_complete(future)


@pytest.mark.skip
def test_cron():
    loop = asyncio.new_event_loop()

    future = asyncio.Future(loop=loop)

    @crontab("* * * * * *", start=False, loop=loop)
    def t():
        # 调用一次就结束
        future.set_result(1)

    t.start()
    loop.run_until_complete(future)
    t.stop()
    assert future.result() == 1


@pytest.mark.skip
def test_raise():
    loop = asyncio.new_event_loop()

    future = asyncio.Future(loop=loop)

    @crontab("* * * * * *", start=False, loop=loop)
    def t():
        loop.call_later(1, future.set_result, 1)
        raise ValueError()

    t.start()
    loop.run_until_complete(future)
    t.stop()
    assert future.result() == 1


@pytest.mark.skip
def test_next():
    loop = asyncio.new_event_loop()

    def t():
        return 1

    t = crontab("* * * * * *", func=t, loop=loop)

    future = asyncio.ensure_future(t.next(), loop=loop)

    loop.run_until_complete(future)
    assert future.result() == 1


@pytest.mark.skip
def test_null_callback():
    loop = asyncio.new_event_loop()

    t = crontab("* * * * * *", loop=loop)

    assert t.handle is None  # not started

    future = asyncio.ensure_future(t.next(4), loop=loop)

    loop.run_until_complete(future)
    assert future.result() == (4,)


@pytest.mark.skip
def test_next_raise():
    loop = asyncio.new_event_loop()

    @crontab("* * * * * *", loop=loop)
    def t():
        raise CustomError()

    future = asyncio.ensure_future(t.next(), loop=loop)

    with pytest.raises(CustomError):
        loop.run_until_complete(future)


@pytest.mark.skip
def test_coro_next():
    loop = asyncio.new_event_loop()

    @crontab("* * * * * *", loop=loop)
    async def t():
        return 1

    future = asyncio.ensure_future(t.next(), loop=loop)

    loop.run_until_complete(future)
    assert future.result() == 1


@pytest.mark.skip
def test_coro_next_raise():
    loop = asyncio.new_event_loop()

    @crontab("* * * * * *", loop=loop)
    async def t():
        raise CustomError()

    future = asyncio.ensure_future(t.next(), loop=loop)

    with pytest.raises(CustomError):
        loop.run_until_complete(future)


def test_next_dst(monkeypatch):
    class mydatetime:
        @classmethod
        def now(cls, tzinfo=None):
            return datetime.datetime(2017, 10, 29, 2, 58, 58, tzinfo=tzinfo)

    monkeypatch.setattr("aiocron.datetime", mydatetime)
    monkeypatch.setattr("dateutil.tz.time.timezone", -3600)
    monkeypatch.setattr("dateutil.tz.time.altzone", -7200)
    monkeypatch.setattr("dateutil.tz.time.daylight", 1)
    monkeypatch.setattr("dateutil.tz.time.tzname", ("CET", "CEST"))

    loop = asyncio.new_event_loop()
    t = crontab("* * * * *", loop=loop)
    t.initialize()

    # last hit in DST
    a = t.get_next()
    time.sleep(3)
    # first hit after DST
    b = t.get_next()

    assert b - a == 60
