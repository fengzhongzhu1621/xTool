import pickle
from typing import Union

# from .pickle_codec_c import PickleCodec
from xTool.misc import tob
from xTool.plugin import PluginType, register_plugin

from .base import CodecType


@register_plugin(PluginType.CODEC, CodecType.PICKLE)
class PickleCodec:
    @classmethod
    def encode(cls, obj: object) -> bytes:
        return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def decode(cls, data: Union[str, bytes]) -> object:
        if not data:
            return data
        return pickle.loads(tob(data))
