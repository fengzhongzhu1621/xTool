# -*- coding: utf-8 -*-

from xTool.codec.pb_json_codec import PbJsonCodec
from .codec_pb2 import Request


class TestPbJsonCodec:
    def test_encode(self):
        request = Request()
        request.message = "hello world"
        value_codec = PbJsonCodec.encode(request)
        assert value_codec == b'{"message": "hello world"}'

        request2 = Request()
        PbJsonCodec.decode(request2, value_codec)
        assert request2.message == request.message
