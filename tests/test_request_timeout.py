# -*- coding: utf-8 -*-

from xTool.apps.sanic import Sanic
from xTool.response import text
from xTool.tests.testing import DelayableSanicTestClient


request_timeout_default_app = Sanic("test_request_timeout_default")
request_no_timeout_app = Sanic("test_request_no_timeout")
request_timeout_default_app.config.REQUEST_TIMEOUT = 0.6
request_no_timeout_app.config.REQUEST_TIMEOUT = 0.6


@request_timeout_default_app.route("/1")
async def handler1(request):
    return text("OK")


@request_no_timeout_app.route("/1")
async def handler2(request):
    return text("OK")


@request_timeout_default_app.websocket("/ws1")
async def ws_handler1(request, ws):
    await ws.send("OK")


def test_default_server_error_request_timeout():
    client = DelayableSanicTestClient(request_timeout_default_app, 2)
    request, response = client.get("/1")
    assert response.status == 408
    assert "Request Timeout" in response.text


def test_default_server_error_request_dont_timeout():
    client = DelayableSanicTestClient(request_no_timeout_app, 0.2)
    request, response = client.get("/1")
    assert response.status == 200
    assert response.text == "OK"


def test_default_server_error_websocket_request_timeout():

    headers = {
        "Upgrade": "websocket",
        "Connection": "upgrade",
        "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
        "Sec-WebSocket-Version": "13",
    }

    client = DelayableSanicTestClient(request_timeout_default_app, 2)
    request, response = client.get("/ws1", headers=headers)

    assert response.status == 408
    assert "Request Timeout" in response.text
