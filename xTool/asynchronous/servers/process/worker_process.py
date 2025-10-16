import asyncio
import multiprocessing
from functools import partial
from signal import SIGTERM

from xTool.asynchronous.servers.protocols.http_protocol import HttpProtocol
from xTool.servers.pipeline import IPipelineConnector
from xTool.servers.signal import Signal


class WorkerProcess(multiprocessing.Process):
    def __init__(
        self,
        host,
        port,
        app,
        loop,
        ssl=None,
        reuse_port=None,
        sock=None,
        pineline_connector: IPipelineConnector = None,
        read_queue=None,
        write_queue=None,
        protocol_factory=HttpProtocol,
        backlog=100,
        connections=None,
        signal=Signal(),
        state=None,
        server_kwargs=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.app = app
        if not loop:
            # 子进程使用自己的事件处理流
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        else:
            self.loop = None
        # 数据管道，用于进程间通信
        self.pipeline_connector = pineline_connector
        # 队列，用于进程间通信
        self.read_queue = read_queue
        self.write_queue = write_queue
        self.protocol_factory = protocol_factory
        self.host = host
        self.port = port
        self.server_kwargs = server_kwargs if server_kwargs else {}
        self.connections = connections
        self.signal = signal
        self.state = state
        self.backlog = backlog
        self.sock = sock
        self.reuse_port = reuse_port
        self.ssl = ssl

    def get_data(self):
        """获取数据 ."""
        pass

    def decode_input_data(self):
        pass

    def encode_output_data(self):
        pass

    def register_signal(self):
        def signal_handler():
            exit()

        self.loop.add_signal_handler(SIGTERM, signal_handler)

    def create_server(self):
        if self.pipeline_connector:
            # 创建自定义Server
            self.pipeline_connector.close_other_side()
            sock = self.worker_pipe_conn.get_socket()
            server_coroutine = self.loop.create_connection(self.protocol_factory, sock=sock)
        else:
            # 创建HTTP Server
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
            )
        return self.loop.run_until_complete(server_coroutine)

    def run(self):
        self.create_server()
        try:
            self.register_signal()
            self.loop.run_forever()
        except (SystemExit, KeyboardInterrupt):
            self.loop.stop()
