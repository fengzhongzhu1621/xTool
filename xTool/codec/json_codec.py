# -*- coding: utf-8 -*-

from typing import Union

import rapidjson as json

from xTool.plugin import register_plugin, PluginType
from xTool.misc import tob
from .base import CodecType


@register_plugin(
    PluginType.CODEC, CodecType.JSON
)
class JsonCodec:
    @classmethod
    def encode(cls, obj: object) -> bytes:
        return json.dumps(obj).encode("utf8")

    @classmethod
    def decode(cls, data: Union[str, bytes]) -> object:
        return json.loads(tob(data))
