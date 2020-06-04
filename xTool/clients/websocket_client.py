# -*- coding: utf-8 -*-

from contextlib import contextmanager

import websockets


@contextmanager
async def connect(url, *args, **kwargs):
    async with websockets.connect(url, *args, **kwargs) as websocket:
        websocket.opened = websocket.open
        yield websocket
