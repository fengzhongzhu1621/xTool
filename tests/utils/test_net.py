#coding: utf-8

import socket

from xTool.utils.net import get_hostname


def test_get_hostname():
    hostname = get_hostname()
    assert hostname == socket.getfqdn()
    hostname = get_hostname('socket:getfqdn')
    assert hostname == socket.getfqdn()
