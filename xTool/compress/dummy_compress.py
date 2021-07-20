# -*- coding: utf-8 -*-

from xTool.plugins.plugin import register_plugin, PluginType
from .base import CompressType


@register_plugin(
    PluginType.COMPRESS, CompressType.DUMMY
)
class DummyCompress:
    @classmethod
    def compress(cls, data: bytes, compression_level: int = 6) -> bytes:
        return data

    @classmethod
    def decompress(cls, data: bytes) -> bytes:
        return data
