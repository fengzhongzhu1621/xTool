# -*- coding: utf-8 -*-

from typing import Callable
from asyncio import AbstractEventLoop
from xTool.plugins.plugin import register_plugin, PluginType
from xTool.plugins.exceptions import PluginDataSourceException
from xTool.plugins.provider import IBaseDataProvider


@register_plugin(PluginType.CONFIG_DATA_SOURCE)
class FileDataProvider(IBaseDataProvider):
    def __init__(self):
        super().__init__()
        self.options = None

    def load(self, file_path: str, options: dict = None) -> bytes:
        # 获取配置文件路径
        if not file_path:
            file_path = options.get('file_path')
        if not file_path:
            raise PluginDataSourceException('FileDataProvider: options should contain file_path')
        # 根据配置文件路径读取配置文件
        with open(file_path, 'rb') as f:
            return f.read()

    def watch(self, callback: Callable, interval: int, event_loop: AbstractEventLoop):
        pass

    def set_options(self, options: dict):
        self.options = options

