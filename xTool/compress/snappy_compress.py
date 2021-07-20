# -*- coding: utf-8 -*-

import snappy

from xTool.plugins.plugin import register_plugin, PluginType
from .base import CompressType


@register_plugin(
    PluginType.COMPRESS, CompressType.SNAPPY
)
class SnappyCompress:
    @classmethod
    def compress(cls, data: bytes, compression_level: int = 6) -> bytes:
        if data is None:
            return data
        return snappy.compress(data, compression_level)

    @classmethod
    def decompress(cls, data: bytes) -> bytes:
        if data is None:
            return data
        return snappy.decompress(data)
