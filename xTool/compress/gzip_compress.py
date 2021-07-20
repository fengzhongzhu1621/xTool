# -*- coding: utf-8 -*-

import gzip
from typing import Optional

from xTool.plugins.plugin import register_plugin, PluginType
from .base import CompressType


@register_plugin(
    PluginType.COMPRESS, CompressType.GZIP
)
class GzipCompress:
    @classmethod
    def compress(cls, data: bytes, compression_level: int = 6) -> Optional[bytes]:
        if data is None:
            return data
        return gzip.compress(data, compression_level)

    @classmethod
    def decompress(cls, data: bytes) -> Optional[bytes]:
        if data is None:
            return data
        return gzip.decompress(data)
