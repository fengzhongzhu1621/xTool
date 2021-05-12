# -*- coding: utf-8 -*-

from xTool.plugins.plugin import register_plugin, PluginType
from .compress_type import CompressType


@register_plugin(
    PluginType.COMPRESS, CompressType.DUMMY
)
class DummyCompress:
    @classmethod
    def compress(cls, data: bytes) -> bytes:
        return data

    @classmethod
    def decompress(cls, data: bytes) -> bytes:
        return data
