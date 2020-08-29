# -*- coding: utf-8 -*-

import pytest

from xTool.decorators.signal import Signal, receiver


@pytest.fixture
def signal():
    return Signal()


def test_connect_to_frozen_signal(signal):
    signal.freeze()

    async def cb():
        ...

    with pytest.raises(RuntimeError):
        signal.connect(cb)


@pytest.mark.parametrize(
    "callback", [
        None,
        max,
        lambda x: x,
    ],
)
def test_wrong_callback(signal, callback):
    with pytest.raises(RuntimeError):
        signal.connect(callback)


async def test_receiver_decorator(signal):
    called = False

    @receiver(signal)
    async def foo():
        nonlocal called
        called = True

    await signal.call()
    assert called


async def test_call_arguments(signal):
    received_args, received_kwargs = None, None

    @receiver(signal)
    async def foo(*args, **kwargs):
        nonlocal received_args, received_kwargs
        received_args, received_kwargs = args, kwargs

    await signal.call("foo", "bar", spam="spam")
    assert received_args == ("foo", "bar")
    assert received_kwargs == {"spam": "spam"}


async def multiple_receivers(signal):
    foo_called, bar_called = False, False

    @receiver(signal)
    async def foo():
        nonlocal foo_called
        foo_called = True

    @receiver(signal)
    async def bar():
        nonlocal bar_called
        bar_called = True

    await signal.call()

    assert all(foo_called, bar_called)
