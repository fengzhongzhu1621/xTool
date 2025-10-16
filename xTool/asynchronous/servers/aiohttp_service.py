import socket

from aiohttp.web import Application, AppRunner, SockSite

from xTool.asynchronous.servers.base import Service
from xTool.asynchronous.servers.tls import PathOrStr, get_ssl_context
from xTool.net.servers.helpers import bind_socket

try:
    from aiohttp.web_log import AccessLogger
except ImportError:  # pragma: nocover
    from aiohttp.helpers import AccessLogger


class AIOHTTPService(Service):
    __async_required__ = "start", "create_application"

    def __init__(
        self,
        address: str = "localhost",
        port: int = None,
        sock: socket.socket = None,
        shutdown_timeout: int = 5,
        **kwds,
    ):

        if not sock:
            if not (address and port):
                raise RuntimeError(
                    "You should pass socket instance or " '"address" and "port" couple',
                )

            self.socket = bind_socket(
                address=address,
                port=port,
                proto_name="http",
            )

        elif not isinstance(sock, socket.socket):
            raise ValueError("sock must be socket instance")
        else:
            self.socket = sock

        self.runner = None
        self.site = None
        self.shutdown_timeout = shutdown_timeout

        super().__init__(**kwds)

    async def create_application(self) -> Application:
        raise NotImplementedError(
            "You should implement " '"create_application" method',
        )

    async def create_site(self):
        return SockSite(
            self.runner,
            self.socket,
            shutdown_timeout=self.shutdown_timeout,
        )

    async def start(self):
        self.runner = AppRunner(
            await self.create_application(),
            access_log_class=AccessLogger,
            access_log_format=AccessLogger.LOG_FORMAT,
        )

        await self.runner.setup()

        self.site = await self.create_site()

        await self.site.start()

    async def stop(self, exception: Exception = None):
        try:
            await self.site.stop()
        finally:
            await self.runner.cleanup()


class AIOHTTPSSLService(AIOHTTPService):
    def __init__(
        self,
        cert: PathOrStr,
        key: PathOrStr,
        ca: PathOrStr = None,
        address: str = None,
        port: int = None,
        verify: bool = True,
        sock: socket.socket = None,
        shutdown_timeout: int = 5,
        require_client_cert: bool = False,
        **kwds,
    ):

        super().__init__(address=address, port=port, sock=sock, shutdown_timeout=shutdown_timeout, **kwds)

        self.__ssl_options = cert, key, ca, verify, require_client_cert

    async def create_site(self):
        return SockSite(
            self.runner,
            self.socket,
            shutdown_timeout=self.shutdown_timeout,
            ssl_context=await self.loop.run_in_executor(None, get_ssl_context, *self.__ssl_options),
        )
