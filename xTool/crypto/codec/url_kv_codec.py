from typing import Dict
from urllib.parse import quote, unquote

from xTool.plugin import PluginType, register_plugin

from .base import CodecType


@register_plugin(PluginType.CODEC, CodecType.URL_KV)
class UrlKvCodec:
    @classmethod
    def encode(cls, data: Dict) -> str:
        return "&".join(
            [
                "{}={}".format(key, quote(str(value).encode("utf8")) if value is not None else "")
                for key, value in data.items()
            ]
        )

    @classmethod
    def decode(cls, data: str) -> Dict:
        items = data.split("&")
        new_data = [item.split("=", 1) for item in items]
        new_data_with_unquote = [(item[0], unquote(item[1]) if item[1] else item[1]) for item in new_data]
        return dict(new_data_with_unquote)
