# -*- coding: utf-8 -*-

import sys
import gc
import contextlib
from socket import socket
from json import JSONDecodeError
from functools import wraps
import asyncio
from typing import (  # noqa
    TYPE_CHECKING,
    Any,
    Callable,
    Iterator,
    List,
    Optional,
    Type,
    Union,
)

import httpx
import websockets

from xTool.exceptions import MethodNotSupported
from xTool.response import text
from xTool.log.log import logger
from xTool.servers.asgi import ASGIApp
from xTool.servers import server

ASGI_HOST = "mockserver"
HOST = "127.0.0.1"
PORT = None

old_conn = None
CONFIG_FOR_TESTS = {"KEEP_ALIVE_TIMEOUT": 2, "KEEP_ALIVE": True}
# test_keep_alive_timeout_reuse doesn't work with random port
KEEP_ALIVE_TIMEOUT_REUSE_PORT = 42101


class SanicTestClient:
    def __init__(self, app, port=PORT, host=HOST):
        """Use port=None to bind to a random port"""
        self.app = app
        self.port = port
        self.host = host

    def get_new_session(self):
        return httpx.AsyncClient(verify=False, trust_env=False)

    async def _local_request(self, method, url, *args, **kwargs):
        logger.info(url)
        raw_cookies = kwargs.pop("raw_cookies", None)

        if method == "websocket":
            async with websockets.connect(url, *args, **kwargs) as websocket:
                websocket.opened = websocket.open
                return websocket
        else:
            async with self.get_new_session() as session:

                try:
                    response = await getattr(session, method.lower())(
                        url, *args, **kwargs
                    )
                except NameError:
                    raise Exception(response.status_code)

                response.body = await response.aread()
                response.status = response.status_code
                response.content_type = response.headers.get("content-type")

                # response can be decoded as json after response._content
                # is set by response.aread()
                try:
                    response.json = response.json()
                except (JSONDecodeError, UnicodeDecodeError):
                    response.json = None

                if raw_cookies:
                    response.raw_cookies = {}

                    for cookie in response.cookies.jar:
                        response.raw_cookies[cookie.name] = cookie

                return response

    def _endpoint(
            self,
            method="get",
            uri="/",
            gather_request=True,
            debug=False,
            server_kwargs={"auto_reload": False},
            host=None,
            *request_args,
            **request_kwargs,
    ):
        results = [None, None]
        exceptions = []

        # 添加请求中间件，记录上一次的请求对象
        if gather_request:

            def _collect_request(request):
                if results[0] is None:
                    results[0] = request

            # 添加为第一个请求中间件
            self.app.request_middleware.appendleft(_collect_request)

        # 注册错误处理器
        @self.app.exception(MethodNotSupported)
        async def error_handler(request, exception):
            if request.method in ["HEAD", "PATCH", "PUT", "DELETE"]:
                return text("", exception.status_code, headers=exception.headers)
            else:
                # 默认异常处理
                return self.app.error_handler.default(request, exception)

        if self.port:
            server_kwargs = dict(
                host=host or self.host,
                port=self.port,
                **server_kwargs,
            )
            host, port = host or self.host, self.port
        else:
            sock = socket()
            sock.bind((host or self.host, 0))
            server_kwargs = dict(sock=sock, **server_kwargs)
            # 获取本地套接口的名字，包括它的IP和端口
            host, port = sock.getsockname()
            self.port = port

        # 获得访问路径
        if uri.startswith(("http:", "https:", "ftp:", "ftps://", "//", "ws:", "wss:")):
            url = uri
        else:
            uri = uri if uri.startswith("/") else f"/{uri}"
            scheme = "ws" if method == "websocket" else "http"
            url = f"{scheme}://{host}:{port}{uri}"
        # Tests construct URLs using PORT = None, which means random port not
        # known until this function is called, so fix that here
        url = url.replace(":None/", f":{port}/")

        # 注册服务事件处理器，用于服务启动后的初始化
        @self.app.listener("after_server_start")
        async def _collect_response(sanic, loop):
            try:
                # 模拟客户端请求
                response = await self._local_request(
                    method, url, *request_args, **request_kwargs
                )
                # 记录上一次请求的响应
                results[-1] = response
            except Exception as e:
                logger.exception("Exception")
                # 记录请求的异常
                exceptions.append(e)
            # 关闭服务
            self.app.stop()

        # 启动http server
        self.app.run(debug=debug, **server_kwargs)
        # 启动成功后，删除after_server_start事件处理器
        self.app.listeners["after_server_start"].pop()

        if exceptions:
            raise ValueError(f"Exception during request: {exceptions}")

        if gather_request:
            try:
                request, response = results
                return request, response
            except BaseException:  # noqa
                raise ValueError(
                    f"Request and response object expected, got ({results})"
                )
        else:
            try:
                return results[-1]
            except BaseException:  # noqa
                raise ValueError(f"Request object expected, got ({results})")

    def get(self, *args, **kwargs):
        return self._endpoint("get", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._endpoint("post", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._endpoint("put", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._endpoint("delete", *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._endpoint("patch", *args, **kwargs)

    def options(self, *args, **kwargs):
        return self._endpoint("options", *args, **kwargs)

    def head(self, *args, **kwargs):
        return self._endpoint("head", *args, **kwargs)

    def websocket(self, *args, **kwargs):
        return self._endpoint("websocket", *args, **kwargs)


class TestASGIApp(ASGIApp):
    async def __call__(self):
        await super().__call__()
        return self.request


async def app_call_with_return(self, scope, receive, send):
    asgi_app = await TestASGIApp.create(self, scope, receive, send)
    return await asgi_app()


_LOOP_FACTORY = Callable[[], asyncio.AbstractEventLoop]


def setup_test_loop(
        loop_factory: _LOOP_FACTORY = asyncio.new_event_loop,
) -> asyncio.AbstractEventLoop:
    """Create and return an asyncio.BaseEventLoop
    instance.
    The caller should also call teardown_test_loop,
    once they are done with the loop.
    """
    loop = loop_factory()
    try:
        module = loop.__class__.__module__
        skip_watcher = "uvloop" in module
    except AttributeError:  # pragma: no cover
        # Just in case
        skip_watcher = True
    asyncio.set_event_loop(loop)
    if sys.platform != "win32" and not skip_watcher:
        policy = asyncio.get_event_loop_policy()
        watcher = asyncio.SafeChildWatcher()
        watcher.attach_loop(loop)
        with contextlib.suppress(NotImplementedError):
            policy.set_child_watcher(watcher)
    return loop


def teardown_test_loop(loop: asyncio.AbstractEventLoop, fast: bool = False) -> None:
    """Teardown and cleanup an event_loop created
    by setup_test_loop.
    """
    closed = loop.is_closed()
    if not closed:
        loop.call_soon(loop.stop)
        loop.run_forever()
        loop.close()

    if not fast:
        gc.collect()

    asyncio.set_event_loop(None)


@contextlib.contextmanager
def loop_context(
        loop_factory: _LOOP_FACTORY = asyncio.new_event_loop, fast: bool = False
) -> Iterator[asyncio.AbstractEventLoop]:
    """A contextmanager that creates an event_loop, for test purposes.
    Handles the creation and cleanup of a test loop.
    """
    loop = setup_test_loop(loop_factory)
    yield loop
    teardown_test_loop(loop, fast=fast)


def pytest_async(func):
    """协程装饰器，用于测试协程方法 ."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(func(*args, **kwargs))

    return wrapper
