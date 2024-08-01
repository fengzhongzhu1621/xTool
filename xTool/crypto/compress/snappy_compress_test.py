from xTool.crypto.compress.snappy_compress import SnappyCompress


class TestSnappyCompress:
    def test_compress(self):
        value = b"123456"
        actual = SnappyCompress.compress(value)
        assert actual == b"\x06\x14123456"

        actual = SnappyCompress.decompress(actual)
        expect = value
        assert actual == expect
