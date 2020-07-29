# -*- coding: utf-8 -*-

import asyncio


class WorkerProtocol(asyncio.Protocol):
    __slots__ = ("transport", )

    def __init__(self, *args, **kargs):
        self.transport = None
        self.parser = None

    def connection_made(self, transport):
        """创建连接时执行 ."""
        self.transport = transport

    def data_received(self, data: bytes):
        """接受到数据时调用 ."""
        self.parser.feed_data(data)
        self.parser.read()
        self.parser.write()

    def connection_lost(self, exc):
        """连接丢失时执行 ."""

    def close(self):
        """
        Force close the connection.
        """
        if self.transport is not None:
            self.transport.close()
            self.transport = None

    def read_request_data(self):
        pass

    def write_response_data(self):
        pass

    def on_message_complete(self):
        pass

    def execute_request_handler(self):
        pass
