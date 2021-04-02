# -*- coding: utf-8 -*-

import socket

from xTool.utils.net import (
    get_hostname,
    int_to_ipv4,
    ipv4_to_int,
    url_concat,
    is_ipv4,
    is_ipv6)


def test_get_hostname():
    hostname = get_hostname()
    assert hostname == socket.getfqdn()
    hostname = get_hostname('socket:getfqdn')
    assert hostname == socket.getfqdn()


def test_int2ip():
    ip = "1.2.3.4"
    ip_int = ipv4_to_int(ip)
    actual = int_to_ipv4(ip_int)
    assert actual == ip


def test_url_concat():
    assert url_concat("http://example.com/foo",
                      dict(c="d")) == 'http://example.com/foo?c=d'
    assert url_concat("http://example.com/foo?a=b",
                      dict(c="d")) == 'http://example.com/foo?a=b&c=d'
    assert url_concat("http://example.com/foo?a=b",
                      [("c", "d"), ("c", "d2")]) == 'http://example.com/foo?a=b&c=d&c=d2'


def test_is_ipv4():
    assert is_ipv4("1.1.1.1")
    assert not is_ipv4("1.1.1.1.1")
    assert not is_ipv4("1.1.1.1/24")


def test_is_ipv6():
    assert not is_ipv6("1.1.1.1")
    assert not is_ipv6("1.1.1.1.1")
    assert not is_ipv6("1.1.1.1/24")
    assert is_ipv6("2001:db8::1")
