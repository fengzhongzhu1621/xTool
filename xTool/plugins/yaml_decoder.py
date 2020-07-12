# -*- coding: utf-8 -*-
import yaml
from xTool.plugins.decoder import BaseDecoder
from xTool.plugins.plugin import PluginType, register_plugin
from xTool.misc import tou


@register_plugin(PluginType.CONFIG_DECODER)
class YamlDecoder(BaseDecoder):

    def __init__(self):
        super().__init__()
        self.options = None

    def decode(self, config_data: bytes, options: dict = None) -> dict:
        config = yaml.load(tou(config_data, Loader=yaml.FullLoader))
        return config

    def set_options(self, options: dict) -> None:
        self.options=options
