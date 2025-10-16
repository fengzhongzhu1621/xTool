from importlib import import_module
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.utils.module_loading import import_string


class UserSettings:

    # 默认配置
    DEFAULT_SETTINGS = {}

    # 动态导入的默认配置
    LAZY_IMPORT_SETTINGS = []

    def __init__(
        self,
        group_name: str,
        default_settings: Optional[Dict] = None,
        import_strings: Optional[List] = None,
        module_strings: Optional[List] = None,
    ) -> None:
        if not default_settings:
            default_settings = {}
        if not import_strings:
            import_strings = []
        if not module_strings:
            module_strings = []

        self.cache = {}
        self.group_name = group_name
        # 获得settings.py中的自定义配置
        self.group_name_settings = self.get_group_name_settings(group_name)
        # 用户定义的默认配置
        self.default_settings = {**self.DEFAULT_SETTINGS, **default_settings}
        # 对象的加载路径
        self.import_strings = [*self.LAZY_IMPORT_SETTINGS, *import_strings]
        # 模块的加载路径
        self.module_strings = module_strings

    def validate_key(self, key: str) -> None:
        """
        validate key
        """

        if key not in self.DEFAULT_SETTINGS.keys():
            raise KeyError("[%s] is not a valid key for %s" % key, self.group_name)

    @staticmethod
    def get_group_name_settings(group_name: str) -> Dict:
        """
        Custom settings in django.conf.settings
        """

        return getattr(settings, group_name, {})

    def __getattr__(self, key: str) -> Any:
        # 读取缓存
        if key in self.cache:
            return self.cache[key]

        # 如果全局配置不存在，则以默认配置为准
        try:
            value = self.group_name_settings[key]
        except KeyError:
            # 获取配置的默认值
            value = self.default_settings[key]

        # 返回加载的模块中的对象
        if key in self.import_strings:
            if isinstance(value, str):
                value = import_string(value)
                self.cache[key] = value
            elif isinstance(value, (list, tuple)):
                value = [import_string(item) for item in value]
                self.cache[key] = value

        # 将模块路径转换为模块对象
        if key in self.module_strings:
            if isinstance(value, str):
                value = import_module(value)
                self.cache[key] = value
            elif isinstance(value, (list, tuple)):
                value = [import_module(item) for item in value]
                self.cache[key] = value

        return value
