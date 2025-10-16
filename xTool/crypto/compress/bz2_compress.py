import bz2
from typing import Optional

from xTool.plugin import PluginType, register_plugin

from .base import CompressType


@register_plugin(PluginType.COMPRESS, CompressType.BZ2)
class Bz2Compress:
    @classmethod
    def compress(cls, data: bytes, compression_level: int = 6) -> Optional[bytes]:
        if data is None:
            return data
        return bz2.compress(data, compression_level)

    @classmethod
    def decompress(cls, data: bytes) -> Optional[bytes]:
        if data is None:
            return data
        return bz2.decompress(data)
