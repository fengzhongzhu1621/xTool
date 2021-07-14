# -*- coding: utf-8 -*-

"""
实现PB和JSON的相互转化
"""

from google.protobuf.json_format import MessageToJson, Parse

from xTool.plugins.plugin import register_plugin, PluginType
from .base import CodecType


@register_plugin(
    PluginType.CODEC, CodecType.PB_JSON
)
class PbJsonCodec:
    @classmethod
    def encode(cls, message: bytes, including_default_value_fields=False,
               preserving_proto_field_name=False,
               indent=None,
               sort_keys=False,
               use_integers_for_enums=False,
               descriptor_pool=None,
               float_precision=None) -> bytes:
        """PB转化为json字符串 ."""
        # preserveing_proto_field_name: 设置为 True 可以保留 protobuf
        # 的原有字段名，不然会自动转驼峰，如 request_id 会被自动转化为 requestId
        json_str = MessageToJson(
            message,
            including_default_value_fields=including_default_value_fields,
            preserving_proto_field_name=preserving_proto_field_name,
            indent=indent,
            sort_keys=sort_keys,
            use_integers_for_enums=use_integers_for_enums,
            descriptor_pool=descriptor_pool,
            float_precision=float_precision)
        return json_str.encode("utf8")

    @classmethod
    def decode(
            cls,
            message: object,
            text: bytes,
            ignore_unknown_fields=False,
            descriptor_pool=None) -> None:
        """JSON字符串转化为PB对象 ."""
        Parse(
            text,
            message,
            ignore_unknown_fields=ignore_unknown_fields,
            descriptor_pool=descriptor_pool)
