# -*- coding: utf-8 -*-

from xTool.compress.zlib_compress import ZlibCompress


class TestZlibCompress:
    def test_compress(self):
        value = b"123456"
        actual = ZlibCompress.compress(value)
        assert actual == b'x\x9c342615\x03\x00\x04.\x016'

        actual = ZlibCompress.decompress(actual)
        expect = value
        assert actual == expect
