# -*- coding: utf-8 -*-

import socket

from xTool.utils.net import get_hostname, int2ip, ip2int, url_concat


def test_get_hostname():
    hostname = get_hostname()
    assert hostname == socket.getfqdn()
    hostname = get_hostname('socket:getfqdn')
    assert hostname == socket.getfqdn()


def test_int2ip():
    ip = "1.2.3.4"
    ip_int = ip2int(ip)
    actual = int2ip(ip_int)
    assert actual == ip


def test_url_concat():
    assert url_concat("http://example.com/foo", dict(c="d")) == 'http://example.com/foo?c=d'
    assert url_concat("http://example.com/foo?a=b", dict(c="d")) == 'http://example.com/foo?a=b&c=d'
    assert url_concat("http://example.com/foo?a=b", [("c", "d"), ("c", "d2")]) == 'http://example.com/foo?a=b&c=d&c=d2'
