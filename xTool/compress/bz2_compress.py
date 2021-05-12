# -*- coding: utf-8 -*-

import bz2

from xTool.plugins.plugin import register_plugin, PluginType
from .compress_type import CompressType


@register_plugin(
    PluginType.COMPRESS, CompressType.BZ2
)
class BZ2Compress:
    @classmethod
    def compress(cls, data: bytes, compression_level: int = 6) -> bytes:
        if data is None:
            return data
        return bz2.compress(data, compression_level)

    @classmethod
    def decompress(cls, data: bytes) -> bytes:
        if data is None:
            return data
        return bz2.decompress(data)
