from xTool.crypto.compress.gzip_compress import GzipCompress


class TestGzipCompress:
    def test_compress(self):
        value = b"123456"
        compress_value = GzipCompress.compress(value)
        print(compress_value)
        actual = GzipCompress.decompress(compress_value)
        expect = value
        assert actual == expect
