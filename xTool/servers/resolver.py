import asyncio
import socket
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from xTool.aiomisc import get_running_loop

__all__ = ('ThreadedResolver', 'AsyncResolver', 'DefaultResolver')

try:
    import aiodns
    # aiodns_default = hasattr(aiodns.DNSResolver, 'gethostbyname')
except ImportError:  # pragma: no cover
    aiodns = None

aiodns_default = False


class AbstractResolver(ABC):
    """Abstract DNS resolver."""

    @abstractmethod
    async def resolve(self, host: str,
                      port: int, family: int) -> List[Dict[str, Any]]:
        """Return IP address for given hostname"""

    @abstractmethod
    async def close(self) -> None:
        """Release resolver"""


class ThreadedResolver(AbstractResolver):
    """Use Executor for synchronous getaddrinfo() calls, which defaults to
    concurrent.futures.ThreadPoolExecutor.
    """

    def __init__(self,
                 loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self._loop = get_running_loop(loop)

    async def resolve(self, host: str, port: int = 0,
                      family: int = socket.AF_INET) -> List[Dict[str, Any]]:
        """解析host ."""
        # 翻译 host / port 参数转换成5个元组的序列，其中包含创建连接到该服务的套接字所需的所有参数。
        # (family, type, proto, canonname, sockaddr)
        # socket.getaddrinfo("example.org", 80, proto=socket.IPPROTO_TCP)
        # [
        #     (<AddressFamily.AF_INET6: 10>, <SocketType.SOCK_STREAM: 1>, 6, '', ('2606:2800:220:1:248:1893:25c8:1946', 80, 0, 0)),
        #     (<AddressFamily.AF_INET: 2>,<SocketType.SOCK_STREAM: 1>, 6, '', ('93.184.216.34', 80))
        # ]
        # AF_INET（又称 PF_INET）是 IPv4 网络协议的套接字类型，AF_INET6 则是 IPv6 的；而 AF_UNIX 则是
        # Unix 系统本地通信。
        infos = await self._loop.getaddrinfo(
            host, port, type=socket.SOCK_STREAM, family=family)

        hosts = []
        for family, _, proto, _, address in infos:
            hosts.append({'hostname': host,
                          'host': address[0],
                          'port': address[1],
                          'family': family,
                          'proto': proto,
                          'flags': socket.AI_NUMERICHOST})

        return hosts

    async def close(self) -> None:
        pass


class AsyncResolver(AbstractResolver):
    """Use the `aiodns` package to make asynchronous DNS lookups"""

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None,
                 *args: Any, **kwargs: Any) -> None:
        if aiodns is None:
            raise RuntimeError("Resolver requires aiodns library")

        self._loop = get_running_loop(loop)
        self._resolver = aiodns.DNSResolver(*args, loop=loop, **kwargs)

        if not hasattr(self._resolver, 'gethostbyname'):
            # aiodns 1.1 is not available, fallback to DNSResolver.query
            self.resolve = self._resolve_with_query  # type: ignore

    async def resolve(self, host: str, port: int = 0,
                      family: int = socket.AF_INET) -> List[Dict[str, Any]]:
        try:
            resp = await self._resolver.gethostbyname(host, family)
        except aiodns.error.DNSError as exc:
            msg = exc.args[1] if len(exc.args) >= 1 else "DNS lookup failed"
            raise OSError(msg) from exc
        hosts = []
        for address in resp.addresses:
            hosts.append(
                {'hostname': host,
                 'host': address, 'port': port,
                 'family': family, 'proto': 0,
                 'flags': socket.AI_NUMERICHOST})

        if not hosts:
            raise OSError("DNS lookup failed")

        return hosts

    async def _resolve_with_query(
            self, host: str, port: int = 0,
            family: int = socket.AF_INET) -> List[Dict[str, Any]]:
        if family == socket.AF_INET6:
            qtype = 'AAAA'
        else:
            qtype = 'A'

        try:
            resp = await self._resolver.query(host, qtype)
        except aiodns.error.DNSError as exc:
            msg = exc.args[1] if len(exc.args) >= 1 else "DNS lookup failed"
            raise OSError(msg) from exc

        hosts = []
        for rr in resp:
            hosts.append(
                {'hostname': host,
                 'host': rr.host, 'port': port,
                 'family': family, 'proto': 0,
                 'flags': socket.AI_NUMERICHOST})

        if not hosts:
            raise OSError("DNS lookup failed")

        return hosts

    async def close(self) -> None:
        return self._resolver.cancel()


# 默认使用aiohttp.ThreadResolver, 异步版本在某些情况下会解析失败
DefaultResolver = AsyncResolver if aiodns_default else ThreadedResolver
