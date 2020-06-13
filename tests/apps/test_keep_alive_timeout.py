# -*- coding: utf-8 -*-

import asyncio
from asyncio import sleep as aio_sleep

from xTool.apps.sanic import Sanic
from xTool.response import text
from xTool.tests.testing import ReuseableSanicTestClient


CONFIG_FOR_TESTS = {"KEEP_ALIVE_TIMEOUT": 2, "KEEP_ALIVE": True}


keep_alive_timeout_app_reuse = Sanic("test_ka_timeout_reuse")
keep_alive_app_client_timeout = Sanic("test_ka_client_timeout")
keep_alive_app_server_timeout = Sanic("test_ka_server_timeout")

keep_alive_timeout_app_reuse.config.update(CONFIG_FOR_TESTS)
keep_alive_app_client_timeout.config.update(CONFIG_FOR_TESTS)
keep_alive_app_server_timeout.config.update(CONFIG_FOR_TESTS)


@keep_alive_timeout_app_reuse.route("/1")
async def handler1(request):
    return text("OK")


@keep_alive_app_client_timeout.route("/1")
async def handler2(request):
    return text("OK")


@keep_alive_app_server_timeout.route("/1")
async def handler3(request):
    return text("OK")


def test_keep_alive_timeout_reuse():
    """If the server keep-alive timeout and client keep-alive timeout are
     both longer than the delay, the client _and_ server will successfully
     reuse the existing connection."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = ReuseableSanicTestClient(keep_alive_timeout_app_reuse, loop)
        headers = {"Connection": "keep-alive"}
        request, response = client.get("/1", headers=headers)
        assert response.status == 200
        assert response.text == "OK"
        loop.run_until_complete(aio_sleep(1))
        request, response = client.get("/1")
        assert response.status == 200
        assert response.text == "OK"
    finally:
        client.kill_server()


def test_keep_alive_client_timeout():
    """If the server keep-alive timeout is longer than the client
    keep-alive timeout, client will try to create a new connection here."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = ReuseableSanicTestClient(keep_alive_app_client_timeout, loop)
        headers = {"Connection": "keep-alive"}
        try:
            request, response = client.get(
                "/1", headers=headers, request_keepalive=1
            )
            assert response.status == 200
            assert response.text == "OK"
            loop.run_until_complete(aio_sleep(2))
            exception = None
            client.get("/1", request_keepalive=1)
        except ValueError as excinfo:
            exception = excinfo
        assert exception is not None
        assert isinstance(exception, ValueError)
        assert "got a new connection" in exception.args[0]
    finally:
        client.kill_server()


def test_keep_alive_server_timeout():
    """If the client keep-alive timeout is longer than the server
    keep-alive timeout, the client will either a 'Connection reset' error
    _or_ a new connection. Depending on how the event-loop handles the
    broken server connection."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # 服务器的KEEP_ALIVE_TIMEOUT为2
        client = ReuseableSanicTestClient(keep_alive_app_server_timeout, loop)
        headers = {"Connection": "keep-alive"}
        try:
            request, response = client.get(
                "/1", headers=headers, request_keepalive=60
            )
            assert response.status == 200
            assert response.text == "OK"
            loop.run_until_complete(aio_sleep(3))
            exception = None
            client.get("/1", request_keepalive=60)
        except ValueError as e:
            exception = e
        assert exception is not None
        assert isinstance(exception, ValueError)
        assert (
            "Connection reset" in exception.args[0]
            or "got a new connection" in exception.args[0]
        )
    finally:
        client.kill_server()
