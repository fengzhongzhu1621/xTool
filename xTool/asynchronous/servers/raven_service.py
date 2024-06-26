import inspect
import logging
import socket
from types import MappingProxyType
from typing import Iterable, Mapping  # NOQA

import yarl
from aiohttp import ClientSession, TCPConnector
from raven import Client
from raven.handlers.logging import SentryHandler
from raven.transport import Transport
from raven_aiohttp import QueuedAioHttpTransport

from xTool.asynchronous.servers.base import Service

log = logging.getLogger(__name__)


class DummyTransport(Transport):
    def send(self, url, data, headers):
        pass


class QueuedKeepaliveAioHttpTransport(QueuedAioHttpTransport):
    DNS_CACHE_TTL = 600
    DNS_CACHE = True
    TCP_CONNECTION_LIMIT = 32
    TCP_CONNECTION_LIMIT_HOST = 8
    WORKERS = 1
    QUEUE_SIZE = 1000

    def __init__(
        self,
        *args,
        family=socket.AF_UNSPEC,
        loop=None,
        dns_cache: bool = DNS_CACHE,
        dns_cache_ttl: int = DNS_CACHE_TTL,
        connection_limit: int = TCP_CONNECTION_LIMIT,
        connection_limit_host: int = TCP_CONNECTION_LIMIT_HOST,
        workers: int = WORKERS,
        qsize: int = QUEUE_SIZE,
        **kwargs
    ):
        self.connection_limit = connection_limit
        self.connection_limit_host = connection_limit_host
        self.dns_cache = dns_cache
        self.dns_cache_ttl = dns_cache_ttl

        super().__init__(*args, family=family, loop=loop, keepalive=True, workers=workers, qsize=qsize, **kwargs)

    def _client_session_factory(self):
        self.connector = TCPConnector(
            family=self.family,
            limit=self.connection_limit,
            limit_per_host=self.connection_limit_host,
            ttl_dns_cache=self.dns_cache_ttl,
            use_dns_cache=self.dns_cache,
            verify_ssl=self.verify_ssl,
        )

        return ClientSession(
            connector=self.connector,
            connector_owner=False,
        )

    async def _close(self):
        transport = await super()._close()
        if inspect.iscoroutinefunction(self.connector.close()):
            await self.connection.close()
        else:
            self.connector.close()
        return transport


class RavenSender(Service):
    __required__ = ("sentry_dsn",)

    sentry_dsn = None  # type: yarl.URL
    min_level = logging.WARNING  # type: int
    client_options = MappingProxyType({})  # type: Mapping

    client = None  # type: Client

    filters = ()  # type: Iterable[logging.Filter]

    async def start(self):
        self.client = Client(str(self.sentry_dsn), transport=QueuedKeepaliveAioHttpTransport, **self.client_options)

        # Initialize Transport object
        self.client.remote.get_transport()

        self.sentry_dsn = (
            yarl.URL(
                self.sentry_dsn,
            )
            .with_password("")
            .with_user("")
        )

        log.info("Starting Raven for %r", self.sentry_dsn)

        handler = SentryHandler(
            client=self.client,
            level=self.min_level,
        )

        # Add filters
        for fltr in self.filters:
            handler.addFilter(fltr)

        logging.getLogger().handlers.append(
            handler,
        )

    async def stop(self, *_):
        transport = self.client.remote.get_transport()
        self.client.set_dsn("", transport=DummyTransport)

        await transport.close()

        log.info("Stopping Raven client for %r", self.sentry_dsn)


__all__ = ("RavenSender",)
