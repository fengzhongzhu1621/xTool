# -*- coding: utf-8 -*-

from xTool.plugins.plugin import register_plugin, PluginType
from .codec_type import CodecType


@register_plugin(
    PluginType.CODEC, CodecType.PB
)
class ProtocCodec:
    @classmethod
    def serialize(cls, obj: object) -> bytes:
        return obj.SerializeToString()

    @classmethod
    def deserialize(cls, obj, data: bytes) -> None:
        obj.ParseFromString(data)
