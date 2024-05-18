import socket
from asyncio import events

from xTool.net.utils import is_ipv6


async def create_datagram_endpoint(protocol, host, port, loop=None, *kwargs):
    """创建udp异步客户端 ."""
    if loop is None:
        loop = events.get_event_loop()
    if is_ipv6(host):
        transport, _ = await loop.create_datagram_endpoint(
            lambda: protocol, remote_addr=(host, port), family=socket.AF_INET6, **kwargs
        )
    else:
        transport, _ = await loop.create_datagram_endpoint(lambda: protocol, remote_addr=(host, port), **kwargs)
    return transport
