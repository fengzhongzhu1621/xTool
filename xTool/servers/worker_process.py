# -*- coding: utf-8 -*-

import asyncio
import multiprocessing
from functools import partial
from signal import SIGTERM

from xTool.servers.protocols.http_protocol import HttpProtocol
from xTool.servers.signal import Signal
from xTool.servers.pipeline import IPipelineConnector


class WorkerProcess(multiprocessing.Process):
    def __init__(self,
                 host,
                 port,
                 app,
                 loop,
                 pineline_connector: IPipelineConnector,
                 protocol_factory=HttpProtocol,
                 connections=None,
                 signal=Signal(),
                 state=None,
                 server_kwargs=None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        if not loop:
            # 子进程使用自己的事件处理流
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        else:
            self.loop = None
        # 数据管道
        self.pipeline_connector = pineline_connector
        self.protocol_factory = protocol_factory
        self.host = host
        self.port = port
        self.server_kwargs = server_kwargs if server_kwargs else {}
        self.connections = connections
        self.signal = signal
        self.state = state

    def create_connection(self):
        self.pipeline_connector.close_other_side()
        protocol = partial(
            self.protocol_factory,
            loop=self.loop,
            connections=self.connections,
            signal=self.signal,
            app=self.app,
            state=self.state,
        )
        server_coroutine = self.loop.create_server(
            protocol,
            self.host,
            self.port,
            ssl=self.ssl,
            reuse_port=self.reuse_port,
            sock=self.sock,
            backlog=self.backlog,
            **self.server_kwargs,
        )
        return self.loop.run_until_complete(server_coroutine)

    def run(self):
        # 创建与分配器的TCP连接，接受请求数据
        self.create_connection()

        def signal_handler():
            exit()

        try:
            self.loop.add_signal_handler(SIGTERM, signal_handler)
            self.loop.run_forever()
        except (SystemExit, KeyboardInterrupt):
            self.loop.stop()
