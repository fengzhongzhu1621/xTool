# -*- coding: utf-8 -*-
import ujson as json
from xTool.plugins.decoder import BaseDecoder
from xTool.plugins.plugin import PluginType, register_plugin
from xTool.misc import tou


@register_plugin(PluginType.CONFIG_DECODER)
class JSONDecoder(BaseDecoder):

    def __init__(self):
        super().__init__()
        self.options = None

    def decode(self, config_data: bytes, options: dict = None) -> dict:
        config = json.loads(tou(config_data))
        return config

    def set_options(self, options: dict) -> None:
        self.options = options
