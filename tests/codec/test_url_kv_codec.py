# -*- coding: utf-8 -*-

from xTool.codec.url_kv_codec import UrlKvCodec


class TestUrlKvCodec:
    def test_encode(self):
        data = {"a": 1, "b": "你好", "c": None, "d": "", "e": 0}
        actual = UrlKvCodec.encode(data)
        expect = "a=1&b=%E4%BD%A0%E5%A5%BD&c=&d=&e=0"
        assert actual == expect

    def test_decode(self):
        data = "a=1&b=%E4%BD%A0%E5%A5%BD&c=&d=&e=0"
        actual = UrlKvCodec.decode(data)
        expect = {'a': '1', 'b': '你好', 'c': '', 'd': '', 'e': '0'}
        assert actual == expect
