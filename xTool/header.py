# -*- coding: utf-8 -*-

# According to https://tools.ietf.org/html/rfc2616#section-7.1
_ENTITY_HEADERS = frozenset(
    [
        "allow",
        "content-encoding",
        "content-language",
        "content-length",
        "content-location",
        "content-md5",
        "content-range",
        "content-type",
        "expires",
        "last-modified",
        "extension-header",
    ]
)

# According to https://tools.ietf.org/html/rfc2616#section-13.5.1
_HOP_BY_HOP_HEADERS = frozenset(
    [
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    ]
)


def is_entity_header(header):
    """Checks if the given header is an Entity Header"""
    return header.lower() in _ENTITY_HEADERS


def is_hop_by_hop_header(header):
    """Checks if the given header is a Hop By Hop header"""
    return header.lower() in _HOP_BY_HOP_HEADERS


def remove_entity_headers(headers, allowed=("content-location", "expires")):
    """去掉实体头部
    Removes all the entity headers present in the headers given.
    According to RFC 2616 Section 10.3.5,
    Content-Location and Expires are allowed as for the
    "strong cache validator".
    https://tools.ietf.org/html/rfc2616#section-10.3.5

    returns the headers without the entity headers
    """
    allowed = set([h.lower() for h in allowed])
    headers = {
        header: value
        for header, value in headers.items()
        if not is_entity_header(header) or header.lower() in allowed
    }
    return headers
