# -*- coding: utf-8 -*-

from xTool.compress.gzip_compress import GzipCompress


class TestGzipCompress:
    def test_compress(self):
        value = b"123456"
        compress_value = GzipCompress.compress(value)
        actual = GzipCompress.decompress(compress_value)
        expect = value
        assert actual == expect
