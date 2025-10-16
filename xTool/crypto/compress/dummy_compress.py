from typing import Optional

from xTool.plugin import PluginType, register_plugin

from .base import CompressType


@register_plugin(PluginType.COMPRESS, CompressType.DUMMY)
class DummyCompress:
    @classmethod
    def compress(cls, data: bytes, _: int = 6) -> Optional[bytes]:
        return data

    @classmethod
    def decompress(cls, data: bytes) -> Optional[bytes]:
        return data
