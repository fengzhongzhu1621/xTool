# -*- coding: utf-8 -*

from django.conf import settings
from django.utils.module_loading import import_string


class UserSettings:
    def __init__(self, attr, default_settings=None, import_strings=None):
        # 获得settings.py中的配置
        self.user_settings = getattr(settings, attr, {})
        # 用户定义的默认配置
        self.default_settings = default_settings
        # 如果配置的值是一个模块地址，需要动态导入
        self.import_strings = import_strings

    def __getattr__(self, attr):
        try:
            # 如果全局配置不存在，则以默认配置为准
            value = self.user_settings[attr]
        except KeyError:
            value = self.defaults[attr]

        # 将模块路径转换为模块对象
        if attr in self.import_strings:
            if isinstance(value, str):
                value = import_string(value)
            elif isinstance(value, (list, tuple)):
                value = [import_string(item) for item in value]

        return value
