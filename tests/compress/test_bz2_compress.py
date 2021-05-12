# -*- coding: utf-8 -*-

from xTool.compress.bz2_compress import BZ2Compress


class TestBZ2Compress:
    def test_compress(self):
        value = b"123456"
        actual = BZ2Compress.compress(value)
        assert actual == b"BZh61AY&SY'\x0f\x93p\x00\x00\x00\x08\x00?\x00 \x00!\x80\x0c\x03'.\xe2\xeeH\xa7\n\x12\x04\xe1\xf2n\x00"

        actual = BZ2Compress.decompress(actual)
        expect = value
        assert actual == expect
