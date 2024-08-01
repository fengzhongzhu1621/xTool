import pytest


@pytest.mark.skip
class TestProtocCodec:
    def test_encode(self):
        from xTool.crypto.codec.pb_codec import ProtocCodec

        from .codec_pb2 import Request

        request = Request()
        request.message = "hello world"
        value_codec = ProtocCodec.encode(request)
        assert value_codec == b"\n\x0bhello world"

        request2 = Request()
        ProtocCodec.decode(request2, value_codec)
        assert request2.message == request.message
