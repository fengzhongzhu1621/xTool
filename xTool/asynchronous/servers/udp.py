import asyncio
import socket
from functools import partial

from xTool.asynchronous.aiomisc import awaitable
from xTool.asynchronous.servers.base import SimpleServer
from xTool.servers.helpers import OptionsType, bind_socket


class UDPSimpleProtocol(asyncio.DatagramProtocol):

    def __init__(self, handle_datagram, task_factory):
        super().__init__()
        self.task_factory = task_factory
        # 将数据处理函数转换为协程
        self.handler = awaitable(handle_datagram)
        self.transport = None  # type: asyncio.DatagramTransport
        self.loop = None  # type: asyncio.AbstractEventLoop

    def connection_made(self, transport: asyncio.DatagramTransport):
        self.transport = transport
        self.loop = asyncio.get_event_loop()

    def datagram_received(self, data: bytes, addr: tuple):
        """每次接收到数据都会创建一个协程处理 ."""
        self.task_factory(self.handler(data, addr))


class UDPServer(SimpleServer):

    def __init__(
        self,
        address: str = None,
        port: int = None,
        options: OptionsType = (),
        sock=None,
        protocol_factory=None,
        **kwargs,
    ):
        if not sock:
            if not (address and port):
                raise RuntimeError(
                    "You should pass socket instance or " '"address" and "port" couple',
                )

            self.make_socket = partial(
                bind_socket,
                address,
                port,
                family=socket.AF_INET6 if ":" in address else socket.AF_INET,
                type=socket.SOCK_DGRAM,
                options=options,
                proto_name="udp",
            )
        elif not isinstance(sock, socket.socket):
            raise ValueError("sock must be socket instance")
        else:
            self.make_socket = lambda: sock

        self.server = None
        if not protocol_factory:
            protocol_factory = UDPSimpleProtocol
        self.protocol_factory = protocol_factory
        self._protocol = None
        self.socket = None
        super().__init__(**kwargs)

    def sendto(self, data, addr):
        return self._protocol.transport.sendto(data, addr)

    def handle_datagram(self, data: bytes, addr):
        raise NotImplementedError

    async def start(self):
        # 绑定端口
        self.socket = self.make_socket()
        # 创建UDP Sever
        transport, protocol = await self.loop.create_datagram_endpoint(
            lambda: self.protocol_factory(
                self.handle_datagram,
                self.create_task,
            ),
            sock=self.socket,
        )
        self.server = transport
        self._protocol = protocol
