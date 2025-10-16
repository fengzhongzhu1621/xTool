import socket

from xTool.net.http.host import get_hostname, url_concat


def test_get_hostname():
    hostname = get_hostname()
    assert hostname == socket.getfqdn()
    hostname = get_hostname("socket:getfqdn")
    assert hostname == socket.getfqdn()


def test_url_concat():
    assert url_concat("http://example.com/foo", dict(c="d")) == "http://example.com/foo?c=d"
    assert url_concat("http://example.com/foo?a=b", dict(c="d")) == "http://example.com/foo?a=b&c=d"
    assert url_concat("http://example.com/foo?a=b", [("c", "d"), ("c", "d2")]) == "http://example.com/foo?a=b&c=d&c=d2"
