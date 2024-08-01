from xTool.crypto.codec.json_codec import JsonCodec


class TestJsonCodec:
    def test_encode(self):
        value = {"a": 1, "b": 2}
        value_codec = JsonCodec.encode(value)
        actual = JsonCodec.decode(value_codec)
        assert actual == value
