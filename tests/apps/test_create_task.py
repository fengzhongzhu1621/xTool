# -*- coding: utf-8 -*-

import asyncio

from queue import Queue
from threading import Event

from xTool.response import text


def test_create_task(app):
    e = Event()

    async def coro():
        await asyncio.sleep(1)
        e.set()

    app.add_task(coro)

    @app.route("/early")
    def not_set(request):
        return text(str(e.is_set()))

    @app.route("/late")
    async def set(request):
        await asyncio.sleep(2)
        return text(str(e.is_set()))

    request, response = app.test_client.get("/early")
    assert response.body == b"False"

    request, response = app.test_client.get("/late")
    assert response.body == b"True"


def test_create_task_with_app_arg(app):
    q = Queue()

    @app.route("/")
    def not_set(request):
        return text("hello")

    async def coro(app):
        q.put(app.name)

    app.add_task(coro)

    request, response = app.test_client.get("/")
    assert q.get() == "test_create_task_with_app_arg"
