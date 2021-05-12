# -*- coding: utf-8 -*-

from xTool.codec.pb_codec import ProtocCodec
from .codec_pb2 import Request


class TestProtocCodec:
    def test_encode(self):
        request = Request()
        request.message = "hello world"
        value_codec = ProtocCodec.encode(request)
        assert value_codec == b'\n\x0bhello world'

        request2 = Request()
        ProtocCodec.decode(request2, value_codec)
        assert request2.message == request.message
