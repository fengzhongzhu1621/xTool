# -*- coding: utf-8 -*-

from typing import Optional

from xTool.plugins.plugin import register_plugin, PluginType
from .base import CompressType


@register_plugin(
    PluginType.COMPRESS, CompressType.DUMMY
)
class DummyCompress:
    @classmethod
    def compress(cls, data: bytes, _: int = 6) -> Optional[bytes]:
        return data

    @classmethod
    def decompress(cls, data: bytes) -> Optional[bytes]:
        return data
