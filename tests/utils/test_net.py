# -*- coding: utf-8 -*-

import socket

from xTool.utils.net import (
    get_hostname,
    int_2_ipv4,
    ipv4_2_int,
    url_concat,
    is_ip_v4,
    is_ip_v6)


def test_get_hostname():
    hostname = get_hostname()
    assert hostname == socket.getfqdn()
    hostname = get_hostname('socket:getfqdn')
    assert hostname == socket.getfqdn()


def test_int2ip():
    ip = "1.2.3.4"
    ip_int = ipv4_2_int(ip)
    actual = int_2_ipv4(ip_int)
    assert actual == ip


def test_url_concat():
    assert url_concat("http://example.com/foo",
                      dict(c="d")) == 'http://example.com/foo?c=d'
    assert url_concat("http://example.com/foo?a=b",
                      dict(c="d")) == 'http://example.com/foo?a=b&c=d'
    assert url_concat("http://example.com/foo?a=b",
                      [("c", "d"), ("c", "d2")]) == 'http://example.com/foo?a=b&c=d&c=d2'


def test_is_ip_v4():
    assert is_ip_v4("1.1.1.1")
    assert not is_ip_v4("1.1.1.1.1")
    assert not is_ip_v4("1.1.1.1/24")


def test_is_ip_v6():
    assert not is_ip_v6("1.1.1.1")
    assert not is_ip_v6("1.1.1.1.1")
    assert not is_ip_v6("1.1.1.1/24")
    assert is_ip_v6("2001:db8::1")
