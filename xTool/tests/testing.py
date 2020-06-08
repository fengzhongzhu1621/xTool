# -*- coding: utf-8 -*-

from socket import socket

import httpx

from xTool.exceptions import MethodNotSupported
from xTool.response import text
from xTool.log.log import logger
from xTool.servers.asgi import ASGIApp
from xTool.clients.http_client import async_httpx_request


ASGI_HOST = "mockserver"
HOST = "127.0.0.1"
PORT = None


class SanicTestClient:
    def __init__(self, app, port=PORT, host=HOST):
        """Use port=None to bind to a random port"""
        self.app = app
        self.port = port
        self.host = host

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
                return text(
                    "", exception.status_code, headers=exception.headers
                )
            else:
                # 默认异常处理
                return self.app.error_handler.default(request, exception)

        if self.port:
            server_kwargs = dict(
                host=host or self.host, port=self.port, **server_kwargs,
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
        if uri.startswith(
            ("http:", "https:", "ftp:", "ftps://", "//", "ws:", "wss:")
        ):
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
                response = await async_httpx_request(
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


class SanicASGIDispatch(httpx.ASGIDispatch):
    pass


class SanicASGITestClient(httpx.AsyncClient):
    def __init__(
        self,
        app,
        base_url: str = f"http://{ASGI_HOST}",
        suppress_exceptions: bool = False,
    ) -> None:
        app.__class__.__call__ = app_call_with_return
        app.asgi = True

        self.app = app
        self.gather_request = True

        dispatch = SanicASGIDispatch(app=app, client=(ASGI_HOST, PORT or 0))
        super().__init__(dispatch=dispatch, base_url=base_url, trust_env=False)

        self.last_request = None

        def _collect_request(request):
            self.last_request = request

        app.request_middleware.appendleft(_collect_request)

    async def request(self, method, url, gather_request=True, *args, **kwargs):
        self.gather_request = gather_request
        response = await super().request(method, url, *args, **kwargs)
        response.status = response.status_code
        response.body = response.content
        response.content_type = response.headers.get("content-type")

        return self.last_request, response

    async def websocket(self, uri, subprotocols=None, *args, **kwargs):
        scheme = "ws"
        path = uri
        root_path = f"{scheme}://{ASGI_HOST}"

        headers = kwargs.get("headers", {})
        headers.setdefault("connection", "upgrade")
        headers.setdefault("sec-websocket-key", "testserver==")
        headers.setdefault("sec-websocket-version", "13")
        if subprotocols is not None:
            headers.setdefault(
                "sec-websocket-protocol", ", ".join(subprotocols)
            )

        scope = {
            "type": "websocket",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "headers": [map(lambda y: y.encode(), x) for x in headers.items()],
            "scheme": scheme,
            "root_path": root_path,
            "path": path,
            "query_string": b"",
        }

        async def receive():
            return {}

        async def send(message):
            pass

        await self.app(scope, receive, send)

        return None, {}
