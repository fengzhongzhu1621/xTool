from typing import Union

import orjson as json

from xTool.misc import tob
from xTool.plugin import PluginType, register_plugin

from .base import CodecType


@register_plugin(PluginType.CODEC, CodecType.JSON)
class JsonCodec:
    @classmethod
    def encode(cls, obj: object) -> bytes:
        return tob(json.dumps(obj))

    @classmethod
    def decode(cls, data: Union[str, bytes]) -> object:
        return json.loads(tob(data))
