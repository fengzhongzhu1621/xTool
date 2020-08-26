# -*- coding: utf-8 -*-

import asyncio
import socket
from xTool.servers.udp import UDPServer


def test_udp_server(aiomisc_unused_port):
    loop = asyncio.get_event_loop()

    class TestService(UDPServer):
        DATA = []

        async def handle_datagram(self, data: bytes, addr: tuple):
            self.DATA.append(data)

    service = TestService("127.0.0.1", aiomisc_unused_port, **{"loop": loop})

    async def writer():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        with sock:
            sock.sendto(b"hello server\n", ("127.0.0.1", aiomisc_unused_port))

    loop.run_until_complete(service.start())
    loop.run_until_complete(
        asyncio.wait_for(writer(), timeout=10),
    )
    loop.close()

    assert TestService.DATA
    assert TestService.DATA == [b"hello server\n"]
