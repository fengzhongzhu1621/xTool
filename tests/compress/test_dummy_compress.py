# -*- coding: utf-8 -*-

from xTool.compress.dummy_compress import DummyCompress


class TestDummyCompress:
    def test_compress(self):
        value = b"123456"
        actual = DummyCompress.compress(value)
        assert actual == value

        actual = DummyCompress.decompress(actual)
        expect = value
        assert actual == expect
