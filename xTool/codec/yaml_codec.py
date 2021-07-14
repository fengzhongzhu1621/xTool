# -*- coding: utf-8 -*-

from typing import Union, Dict, Hashable, Any, List

import yaml
from xTool.plugins.plugin import register_plugin, PluginType
from .codec_type import CodecType


@register_plugin(
    PluginType.CODEC, CodecType.YAML
)
class YamlCodec:
    @classmethod
    def encode(
            cls,
            obj: object,
            stream=None,
            dumper=yaml.Dumper,
            default_style=None,
            default_flow_style=False,
            canonical=None,
            indent=None,
            width=None,
            allow_unicode=None,
            line_break=None,
            encoding=None,
            explicit_start=None,
            explicit_end=None,
            version=None,
            tags=None,
            sort_keys=True) -> bytes:
        """python对象转化为yaml ."""
        return yaml.dump(
            obj,
            stream=stream,
            Dumper=dumper,
            default_style=default_style,
            default_flow_style=default_flow_style,
            canonical=canonical,
            indent=indent,
            width=width,
            allow_unicode=allow_unicode,
            line_break=line_break,
            encoding=encoding,
            explicit_start=explicit_start,
            explicit_end=explicit_end,
            version=version,
            tags=tags,
            sort_keys=sort_keys)

    @classmethod
    def decode(cls, data: str, loader=yaml.FullLoader) -> Union[Dict[Hashable, Any], List, None]:
        """yaml字符串转化为python对象 ."""
        return yaml.load(data, Loader=loader)
