# -*- coding: utf-8 -*-

import asyncio
import logging
import sys

from inspect import isawaitable

import pytest

from xTool.apps.sanic import Sanic
from xTool.exceptions import HttpStatusException
from xTool.response import text
from xTool.aiomisc import uvloop_installed


def test_app_loop_running(app):
    @app.get("/test")
    async def handler(request):
        assert isinstance(app.loop, asyncio.AbstractEventLoop)
        return text("pass")

    request, response = app.test_client.get("/test")
    assert response.text == "pass"


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="requires python3.7 or higher"
)
def test_create_asyncio_server(app):
    if not uvloop_installed():
        loop = asyncio.get_event_loop()
        # 创建服务时自动启动
        asyncio_srv_coro = app.create_server(return_asyncio_server=True)
        assert isawaitable(asyncio_srv_coro)
        srv = loop.run_until_complete(asyncio_srv_coro)
        assert srv.is_serving() is True


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="requires python3.7 or higher"
)
def test_asyncio_server_no_start_serving(app):
    if not uvloop_installed():
        loop = asyncio.get_event_loop()
        asyncio_srv_coro = app.create_server(
            port=43123,
            return_asyncio_server=True,
            asyncio_server_kwargs=dict(
                start_serving=False),    # 创建server时不自动启动
        )
        srv = loop.run_until_complete(asyncio_srv_coro)
        assert srv.is_serving() is False


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="requires python3.7 or higher"
)
def test_asyncio_server_start_serving(app):
    if not uvloop_installed():
        loop = asyncio.get_event_loop()
        asyncio_srv_coro = app.create_server(
            port=43124,
            return_asyncio_server=True,
            asyncio_server_kwargs=dict(start_serving=False),
        )
        srv = loop.run_until_complete(asyncio_srv_coro)
        assert srv.is_serving() is False
        loop.run_until_complete(srv.start_serving())
        assert srv.is_serving() is True
        # 返回一个等待关闭任务
        wait_close = srv.close()
        loop.run_until_complete(wait_close)
        # Looks like we can't easily test `serve_forever()`


def test_app_loop_not_running(app):
    with pytest.raises(HttpStatusException) as excinfo:
        app.loop

    assert str(excinfo.value) == (
        "Loop can only be retrieved after the app has started "
        "running. Not supported with `create_server` function"
    )


def test_app_run_raise_type_error(app):

    with pytest.raises(TypeError) as excinfo:
        app.run(loop="loop")

    assert str(excinfo.value) == (
        "loop is not a valid argument. To use an existing loop, "
        "change to create_server().\nSee more: "
        "https://sanic.readthedocs.io/en/latest/sanic/deploying.html"
        "#asynchronous-support"
    )


def test_app_route_raise_value_error(app):

    with pytest.raises(ValueError) as excinfo:

        @app.route("/test")
        async def handler():
            return text("test")

    assert (
        str(excinfo.value)
        == "Required parameter `request` missing in the handler() route?"
    )


def test_app_handle_request_handler_is_none(app, monkeypatch):
    def mockreturn(*args, **kwargs):
        return None, [], {}, "", ""

    # Not sure how to make app.router.get() return None, so use mock here.
    monkeypatch.setattr(app.router, "get", mockreturn)

    @app.get("/test")
    def handler(request):
        return text("test")

    request, response = app.test_client.get("/test")

    assert "'None' was returned while requesting a handler from the router" in response.text


@pytest.mark.parametrize("websocket_enabled", [True, False])
@pytest.mark.parametrize("enable", [True, False])
def test_app_enable_websocket(app, websocket_enabled, enable):
    app.websocket_enabled = websocket_enabled
    app.enable_websocket(enable=enable)

    assert app.websocket_enabled == enable

    @app.websocket("/ws")
    async def handler(request, ws):
        await ws.send("test")

    assert app.websocket_enabled


def test_handle_request_with_nested_exception(app, monkeypatch):

    err_msg = "Mock Exception"

    # Not sure how to raise an exception in app.error_handler.response(), use
    # mock here
    def mock_error_handler_response(*args, **kwargs):
        raise Exception(err_msg)

    monkeypatch.setattr(
        app.error_handler, "response", mock_error_handler_response
    )

    @app.get("/")
    def handler(request):
        raise Exception

    request, response = app.test_client.get("/")
    assert response.status == 500
    assert response.text == "An error occurred while handling an error"


def test_handle_request_with_nested_exception_debug(app, monkeypatch):

    err_msg = "Mock Exception"

    # Not sure how to raise an exception in app.error_handler.response(), use
    # mock here
    def mock_error_handler_response(*args, **kwargs):
        raise Exception(err_msg)

    monkeypatch.setattr(
        app.error_handler, "response", mock_error_handler_response
    )

    @app.get("/")
    def handler(request):
        raise Exception

    request, response = app.test_client.get("/", debug=True)
    assert response.status == 500
    assert response.text.startswith(
        f"Error while handling error: {err_msg}\nStack: Traceback (most recent call last):\n"
    )


def test_handle_request_with_nested_sanic_exception(app, monkeypatch, caplog):

    # Not sure how to raise an exception in app.error_handler.response(), use
    # mock here
    def mock_error_handler_response(*args, **kwargs):
        raise HttpStatusException("Mock HttpStatusException")

    monkeypatch.setattr(
        app.error_handler, "response", mock_error_handler_response
    )

    @app.get("/")
    def handler(request):
        raise Exception

    # 临时修改日志级别
    with caplog.at_level(logging.ERROR):
        request, response = app.test_client.get("/")

    port = request.server_port
    assert port > 0
    assert response.status == 500
    assert "Mock HttpStatusException" in response.text
    assert (
        "xTool.root",
        logging.ERROR,
        f"Exception occurred while handling uri: 'http://127.0.0.1:{port}/'",
    ) in caplog.record_tuples


def test_app_name_required():
    with pytest.deprecated_call():
        Sanic()
