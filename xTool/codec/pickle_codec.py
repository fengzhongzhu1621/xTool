# -*- coding: utf-8 -*-

import pickle
from xTool.plugins.plugin import register_plugin, PluginType
# from .pickle_codec_c import PickleCodec
from .base import CodecType


@register_plugin(
    PluginType.CODEC, CodecType.PICKLE
)
class PickleCodec:
    @classmethod
    def encode(cls, obj: object) -> bytes:
        return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def decode(cls, data: bytes) -> object:
        return pickle.loads(data)
