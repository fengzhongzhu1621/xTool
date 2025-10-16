import asyncio
import socket

import pytest

from xTool.asynchronous.servers.tcp import TCPServer


@pytest.mark.skip
def test_tcp_server(aiomisc_unused_port):
    loop = asyncio.get_event_loop()

    class TestTcpService(TCPServer):
        DATA = []

        async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
            while True:
                data = await reader.readline()
                writer.write(data)
                self.DATA.append(data)

    service = TestTcpService("127.0.0.1", aiomisc_unused_port, **{"loop": loop})

    async def writer():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with sock:
            sock.connect(("127.0.0.1", aiomisc_unused_port))
            sock.sendall(b"hello server\n")
        await asyncio.sleep(1)

    loop.run_until_complete(service.start())
    loop.run_until_complete(writer())
    loop.close()

    assert TestTcpService.DATA == [b"hello server\n"]
