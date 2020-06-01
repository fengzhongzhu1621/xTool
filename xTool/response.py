# -*- coding: utf-8 -*-

from xTool.cookies.cookies import CookieJar
from xTool.headers import format_http1, format_http1_response
from xTool.header import remove_entity_headers
from xTool.collections.header import Header
from xTool.status import has_message_body


class BaseHTTPResponse:
    def __init__(self, *args, **kwargs):
        self._cookies = None

    def _encode_body(self, data):
        return data.encode() if hasattr(data, "encode") else data

    def _parse_headers(self):
        """Convert a headers iterable into HTTP/1 header format ."""
        return format_http1(self.headers.items())

    @property
    def cookies(self):
        if self._cookies is None:
            self._cookies = CookieJar(self.headers)
        return self._cookies

    def get_headers(
        self,
        version="1.1",
        keep_alive=False,
        keep_alive_timeout=None,
        body=b"",
    ):
        """.. deprecated:: 20.3:
           This function is not public API and will be removed."""

        # self.headers get priority over content_type
        if self.content_type and "Content-Type" not in self.headers:
            self.headers["Content-Type"] = self.content_type

        if keep_alive:
            self.headers["Connection"] = "keep-alive"
            if keep_alive_timeout is not None:
                self.headers["Keep-Alive"] = keep_alive_timeout
        else:
            self.headers["Connection"] = "close"

        if self.status in (304, 412):
            self.headers = remove_entity_headers(self.headers)

        return format_http1_response(self.status, self.headers.items(), body)


class HTTPResponse(BaseHTTPResponse):
    __slots__ = ("body", "status", "content_type", "headers", "_cookies")

    def __init__(
        self,
        body=None,
        status=200,
        headers=None,
        content_type=None,
        body_bytes=b"",
    ):
        self.content_type = content_type
        self.body = body_bytes if body is None else self._encode_body(body)
        self.status = status
        self.headers = Header(headers or {})
        self._cookies = None

    def output(self, version="1.1", keep_alive=False, keep_alive_timeout=None):
        body = b""
        if has_message_body(self.status):
            body = self.body
            self.headers["Content-Length"] = self.headers.get(
                "Content-Length", len(self.body)
            )

        return self.get_headers(version, keep_alive, keep_alive_timeout, body)

    @property
    def cookies(self):
        if self._cookies is None:
            self._cookies = CookieJar(self.headers)
        return self._cookies


def html(body, status=200, headers=None):
    """
    Returns response object with body in html format.

    :param body: str or bytes-ish, or an object with __html__ or _repr_html_.
    :param status: Response code.
    :param headers: Custom Headers.
    """
    if hasattr(body, "__html__"):
        body = body.__html__()
    elif hasattr(body, "_repr_html_"):
        body = body._repr_html_()
    return HTTPResponse(
        body,
        status=status,
        headers=headers,
        content_type="text/html; charset=utf-8",
    )
