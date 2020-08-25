# -*- coding: utf-8 -*-

import asyncio
import multiprocessing
import os

from functools import partial
from signal import SIG_IGN, SIGINT, SIGTERM, Signals
from signal import signal as signal_func
from socket import SO_REUSEADDR, SOL_SOCKET, socket

from xTool.log.log import logger
from xTool.utils.processes import ctrlc_workaround_for_windows
from xTool.misc import OS_IS_WINDOWS
from xTool.aiomisc import load_uvlopo
from xTool.servers.protocols.http_protocol import HttpProtocol
from xTool.servers.trigger import trigger_events
from xTool.servers.signal import Signal


load_uvlopo()


class AsyncioServer:
    """
    Wraps an asyncio server with functionality that might be useful to
    a user who needs to manage the server lifecycle manually.
    """

    __slots__ = (
        "loop",
        "serve_coro",
        "_after_start",
        "_before_stop",
        "_after_stop",
        "server",
        "connections",
    )

    def __init__(
        self,
        loop,
        serve_coro,
        connections,
        after_start,
        before_stop,
        after_stop,
    ):
        # Note, Sanic already called "before_server_start" events
        # before this helper was even created. So we don't need it here.
        self.loop = loop
        self.serve_coro = serve_coro
        self._after_start = after_start
        self._before_stop = before_stop
        self._after_stop = after_stop
        self.server = None
        self.connections = connections

    def after_start(self):
        """Trigger "after_server_start" events"""
        trigger_events(self._after_start, self.loop)

    def before_stop(self):
        """Trigger "before_server_stop" events"""
        trigger_events(self._before_stop, self.loop)

    def after_stop(self):
        """Trigger "after_server_stop" events"""
        trigger_events(self._after_stop, self.loop)

    def is_serving(self):
        """判断服务器是否已经启动 ."""
        if self.server:
            return self.server.is_serving()
        return False

    def wait_closed(self):
        if self.server:
            return self.server.wait_closed()

    def close(self):
        """关闭服务器 ."""
        if self.server:
            # 关闭服务器
            self.server.close()
            # 创建一个等待服务器关闭任务
            coro = self.wait_closed()
            task = asyncio.ensure_future(coro, loop=self.loop)
            return task

    def start_serving(self):
        """启动服务器 ."""
        if self.server:
            try:
                return self.server.start_serving()
            except AttributeError:
                raise NotImplementedError(
                    "server.start_serving not available in this version "
                    "of asyncio or uvloop."
                )

    def serve_forever(self):
        if self.server:
            try:
                return self.server.serve_forever()
            except AttributeError:
                raise NotImplementedError(
                    "server.serve_forever not available in this version "
                    "of asyncio or uvloop."
                )

    def __await__(self):
        """Starts the asyncio server, returns AsyncServerCoro"""
        task = asyncio.ensure_future(self.serve_coro)
        # 等待task执行完成
        while not task.done():
            yield
        # 获得task的执行结果
        self.server = task.result()
        # 返回AsyncioServer
        return self


def serve(
    host,
    port,
    app,
    before_start=None,
    after_start=None,
    before_stop=None,
    after_stop=None,
    ssl=None,
    sock=None,
    reuse_port=False,
    loop=None,
    protocol=HttpProtocol,
    backlog=100,
    register_sys_signals=True,
    run_multiple=False,
    run_async=False,
    connections=None,
    signal=Signal(),
    state=None,
    asyncio_server_kwargs=None,
):
    """Start asynchronous HTTP Server on an individual process.

    :param host: Address to host on
    :param port: Port to host on
    :param before_start: function to be executed before the server starts
                         listening. Takes arguments `app` instance and `loop`
    :param after_start: function to be executed after the server starts
                        listening. Takes  arguments `app` instance and `loop`
    :param before_stop: function to be executed when a stop signal is
                        received before it is respected. Takes arguments
                        `app` instance and `loop`
    :param after_stop: function to be executed when a stop signal is
                       received after it is respected. Takes arguments
                       `app` instance and `loop`
    :param ssl: SSLContext
    :param sock: Socket for the server to accept connections from
    :param reuse_port: `True` for multiple workers
    :param loop: asyncio compatible event loop
    :param run_async: bool: Do not create a new event loop for the server,
                      and return an AsyncServer object rather than running it
    :param asyncio_server_kwargs: key-value args for asyncio/uvloop
                                  create_server method
    :return: Nothing
    """
    if not run_async:
        # create new event_loop after fork
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if app.debug:
        loop.set_debug(app.debug)

    app.asgi = False

    connections = connections if connections is not None else set()
    server = partial(
        protocol,
        loop=loop,
        connections=connections,
        signal=signal,
        app=app,
        state=state,
    )
    asyncio_server_kwargs = (
        asyncio_server_kwargs if asyncio_server_kwargs else {}
    )
    # 创建一个http server coroutine
    server_coroutine = loop.create_server(
        server,
        host,
        port,
        ssl=ssl,
        reuse_port=reuse_port,
        sock=sock,
        backlog=backlog,
        **asyncio_server_kwargs,
    )

    if run_async:
        return AsyncioServer(
            loop=loop,
            serve_coro=server_coroutine,
            connections=connections,
            after_start=after_start,
            before_stop=before_stop,
            after_stop=after_stop,
        )

    trigger_events(before_start, loop)

    # 创建http server future
    try:
        http_server = loop.run_until_complete(server_coroutine)
    except BaseException:
        logger.exception("Unable to start server")
        return

    # 服务启动后的初始化
    trigger_events(after_start, loop)

    # Ignore SIGINT when run_multiple
    if run_multiple:
        signal_func(SIGINT, SIG_IGN)

    # 注册信号处理函数
    # Register signals for graceful termination
    if register_sys_signals:
        if OS_IS_WINDOWS:
            # 注册SIGINT
            ctrlc_workaround_for_windows(app)
        else:
            for _signal in [SIGTERM] if run_multiple else [SIGINT, SIGTERM]:
                loop.add_signal_handler(_signal, app.stop)

    # 获得主进程ID
    pid = os.getpid()

    # 运行http server
    try:
        logger.info("Starting worker [%s]", pid)
        loop.run_forever()
    finally:
        logger.info("Stopping worker [%s]", pid)

        # Run the on_stop function if provided
        trigger_events(before_stop, loop)

        # Wait for event loop to finish and all connections to drain
        http_server.close()
        loop.run_until_complete(http_server.wait_closed())

        # Complete all tasks on the loop
        signal.stopped = True
        for connection in connections:
            connection.close_if_idle()

        # Gracefully shutdown timeout.
        # We should provide graceful_shutdown_timeout,
        # instead of letting connection hangs forever.
        # Let's roughly calcucate time.
        graceful = app.config.GRACEFUL_SHUTDOWN_TIMEOUT
        start_shutdown = 0
        while connections and (start_shutdown < graceful):
            loop.run_until_complete(asyncio.sleep(0.1))
            start_shutdown = start_shutdown + 0.1

        # Force close non-idle connection after waiting for
        # graceful_shutdown_timeout
        coros = []
        for conn in connections:
            if hasattr(conn, "websocket") and conn.websocket:
                coros.append(conn.websocket.close_connection())
                _shutdown = asyncio.gather(*coros)
                loop.run_until_complete(_shutdown)
            else:
                conn.close()

        trigger_events(after_stop, loop)

        loop.close()


def serve_multiple(server_settings, workers):
    """Start multiple server processes simultaneously.  Stop on interrupt
    and terminate signals, and drain connections when complete.

    :param server_settings: kw arguments to be passed to the serve function
    :param workers: number of workers to launch
    :param stop_event: if provided, is used as a stop signal
    :return:
    """
    server_settings["reuse_port"] = True
    server_settings["run_multiple"] = True

    # Handling when custom socket is not provided.
    if server_settings.get("sock") is None:
        sock = socket()
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((server_settings["host"], server_settings["port"]))
        sock.set_inheritable(True)
        server_settings["sock"] = sock
        server_settings["host"] = None
        server_settings["port"] = None

    processes = []

    def sig_handler(signal, frame):
        logger.info("Received signal %s. Shutting down.", Signals(signal).name)
        for process in processes:
            os.kill(process.pid, SIGTERM)

    signal_func(SIGINT, lambda s, f: sig_handler(s, f))
    signal_func(SIGTERM, lambda s, f: sig_handler(s, f))
    mp = multiprocessing.get_context("fork")

    # 启动多个子进程
    for _ in range(workers):
        process = mp.Process(target=serve, kwargs=server_settings)
        process.daemon = True
        process.start()
        processes.append(process)

    # 等待所有子进程结束
    for process in processes:
        process.join()

    # the above processes will block this until they're stopped
    for process in processes:
        process.terminate()
    server_settings.get("sock").close()
