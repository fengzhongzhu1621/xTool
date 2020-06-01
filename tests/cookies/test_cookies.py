# -*- coding: utf-8 -*-

from unittest import TestCase
from xTool.cookies.cookies import CookieJar, Cookie
from xTool.collections.header import Header


class TestCookieJar(TestCase):
    def test___setitem__(self):
        headers = Header()
        headers["X-Served-By"] = "sanic"
        jar = CookieJar(headers)
        assert jar == {}
