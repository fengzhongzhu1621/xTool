# -*- coding: utf-8 -*-

import rapidjson as json
from xTool.plugins.plugin import register_plugin, PluginType
from .base import CodecType


@register_plugin(
    PluginType.CODEC, CodecType.JSON
)
class JsonCodec:
    @classmethod
    def encode(cls, obj: object) -> bytes:
        return json.dumps(obj).encode("utf8")

    @classmethod
    def decode(cls, data: bytes) -> object:
        return json.loads(data)
