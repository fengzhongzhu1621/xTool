# -*- coding: utf-8 -*-

from socket import socket
from json import JSONDecodeError
import asyncio

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
KEEP_ALIVE_TIMEOUT_REUSE_PORT = 42101  # test_keep_alive_timeout_reuse doesn't work with random port


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


class ReusableSanicConnectionPool(
    httpx.dispatch.connection_pool.ConnectionPool
):
    @property
    def cert(self):
        return self.ssl.cert

    @property
    def verify(self):
        return self.ssl.verify

    @property
    def trust_env(self):
        return self.ssl.trust_env

    @property
    def http2(self):
        return self.ssl.http2

    async def acquire_connection(self, origin, timeout):
        global old_conn
        connection = self.pop_connection(origin)

        if connection is None:
            pool_timeout = None if timeout is None else timeout.pool_timeout

            await self.max_connections.acquire(timeout=pool_timeout)
            ssl_config = httpx.config.SSLConfig(
                cert=self.cert,
                verify=self.verify,
                trust_env=self.trust_env,
                http2=self.http2
            )
            connection = httpx.dispatch.connection.HTTPConnection(
                origin,
                ssl=ssl_config,
                backend=self.backend,
                release_func=self.release_connection,
                uds=self.uds,
            )

        self.active_connections.add(connection)

        # 判断HTTP连接是否复用
        if old_conn is not None:
            if old_conn != connection:
                raise RuntimeError(
                    "We got a new connection, wanted the same one!"
                )
        old_conn = connection

        return connection


class ResusableSanicSession(httpx.AsyncClient):
    def __init__(self, *args, **kwargs) -> None:
        dispatch = ReusableSanicConnectionPool()
        super().__init__(dispatch=dispatch, trust_env=False, *args, **kwargs)


class ReuseableSanicTestClient(SanicTestClient):
    def __init__(self, app, loop=None):
        super().__init__(app)
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self._server = None
        self._tcp_connector = None
        self._session = None

    def get_new_session(self):
        return ResusableSanicSession()

    # Copied from SanicTestClient, but with some changes to reuse the
    # same loop for the same app.
    def _endpoint(
        self,
        method="get",
        uri="/",
        gather_request=True,
        debug=False,
        server_kwargs=None,
        *request_args,
        **request_kwargs,
    ):
        loop = self._loop
        results = [None, None]
        exceptions = []
        server_kwargs = server_kwargs or {"return_asyncio_server": True}
        if gather_request:

            def _collect_request(request):
                if results[0] is None:
                    results[0] = request

            self.app.request_middleware.appendleft(_collect_request)

        if uri.startswith(
            ("http:", "https:", "ftp:", "ftps://", "//", "ws:", "wss:")
        ):
            url = uri
        else:
            uri = uri if uri.startswith("/") else f"/{uri}"
            scheme = "http"
            url = f"{scheme}://{HOST}:{KEEP_ALIVE_TIMEOUT_REUSE_PORT}{uri}"

        @self.app.listener("after_server_start")
        async def _collect_response(loop):
            try:
                # 给自己发送请求
                response = await self._local_request(
                    method, url, *request_args, **request_kwargs
                )
                results[-1] = response
            except Exception as e2:
                exceptions.append(e2)

        if self._server is not None:
            _server = self._server
        else:
            _server_co = self.app.create_server(
                host=HOST, debug=debug, port=KEEP_ALIVE_TIMEOUT_REUSE_PORT, **server_kwargs
            )

            server.trigger_events(
                self.app.listeners["before_server_start"], loop
            )

            try:
                loop._stopping = False
                _server = loop.run_until_complete(_server_co)
            except Exception as e1:
                raise e1
            self._server = _server
        server.trigger_events(self.app.listeners["after_server_start"], loop)
        self.app.listeners["after_server_start"].pop()

        if exceptions:
            raise ValueError(f"Exception during request: {exceptions}")

        if gather_request:
            self.app.request_middleware.pop()
            try:
                request, response = results
                return request, response
            except Exception:
                raise ValueError(
                    f"Request and response object expected, got ({results})"
                )
        else:
            try:
                return results[-1]
            except Exception:
                raise ValueError(
                    f"Request object expected, got ({results})"
                )

    def kill_server(self):
        try:
            if self._server:
                self._server.close()
                self._loop.run_until_complete(self._server.wait_closed())
                self._server = None

            if self._session:
                self._loop.run_until_complete(self._session.aclose())
                self._session = None

        except Exception as e3:
            raise e3

    # Copied from SanicTestClient, but with some changes to reuse the
    # same TCPConnection and the sane ClientSession more than once.
    # Note, you cannot use the same session if you are in a _different_
    # loop, so the changes above are required too.
    async def _local_request(self, method, url, *args, **kwargs):
        raw_cookies = kwargs.pop("raw_cookies", None)
        request_keepalive = kwargs.pop(
            "request_keepalive", CONFIG_FOR_TESTS["KEEP_ALIVE_TIMEOUT"]
        )
        if not self._session:
            self._session = self.get_new_session()
        try:
            response = await getattr(self._session, method.lower())(
                url, timeout=request_keepalive, *args, **kwargs
            )
        except NameError:
            raise Exception(response.status_code)

        try:
            response.json = response.json()
        except (JSONDecodeError, UnicodeDecodeError):
            response.json = None

        response.body = await response.aread()
        response.status = response.status_code
        response.content_type = response.headers.get("content-type")

        if raw_cookies:
            response.raw_cookies = {}
            for cookie in response.cookies:
                response.raw_cookies[cookie.name] = cookie

        return response


class DelayableHTTPConnection(httpx.dispatch.connection.HTTPConnection):
    def __init__(self, *args, **kwargs):
        self._request_delay = None
        if "request_delay" in kwargs:
            self._request_delay = kwargs.pop("request_delay")
        super().__init__(*args, **kwargs)

    async def send(self, request, timeout=None):

        if self.connection is None:
            self.connection = (await self.connect(timeout=timeout))

        if self._request_delay:
            await asyncio.sleep(self._request_delay)

        response = await self.connection.send(request, timeout=timeout)

        return response


class DelayableSanicConnectionPool(
    httpx.dispatch.connection_pool.ConnectionPool
):
    def __init__(self, request_delay=None, *args, **kwargs):
        self._request_delay = request_delay
        super().__init__(*args, **kwargs)

    async def acquire_connection(self, origin, timeout=None):
        connection = self.pop_connection(origin)

        if connection is None:
            pool_timeout = None if timeout is None else timeout.pool_timeout

            await self.max_connections.acquire(timeout=pool_timeout)
            connection = DelayableHTTPConnection(
                origin,
                ssl=self.ssl,
                backend=self.backend,
                release_func=self.release_connection,
                uds=self.uds,
                request_delay=self._request_delay,
            )

        self.active_connections.add(connection)

        return connection


class DelayableSanicSession(httpx.AsyncClient):
    def __init__(self, request_delay=None, *args, **kwargs) -> None:
        dispatch = DelayableSanicConnectionPool(request_delay=request_delay)
        super().__init__(dispatch=dispatch, trust_env=False, *args, **kwargs)


class DelayableSanicTestClient(SanicTestClient):
    def __init__(self, app, request_delay=None):
        super().__init__(app)
        self._request_delay = request_delay
        self._loop = None

    def get_new_session(self):
        return DelayableSanicSession(request_delay=self._request_delay)
