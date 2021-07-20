# -*- coding: utf-8 -*-

from typing import Union
from enum import Enum, IntEnum, unique


@unique
class PluginType(IntEnum):
    # 单元测试
    UNITTEST = 1

    # 默认类型
    CONFIG_NORMAL = 2

    # 过滤器
    BEFORE_FILTER = 3
    AFTER_FILTER = 4

    # metrics
    STATS_LOGGER = 10
    STATS_NAME_HANDLER = 11             # stats名称验证器
    STATS_NAME_ALLOW_VALIDATOR = 12     # 只允许指定的metrics name

    # 编解码
    CODEC = 20
    # 解压缩
    COMPRESS = 21

    # 配置加载
    CONFIG_LOADER = 30


class PluginStore:
    __slots__ = ("plugins", "plugin_instances")

    def __init__(self):
        self.plugins = {}              # 存放所有的插件
        self.plugin_instances = {}     # 存放所有的插件实例化对象，一个插件只有一个实例化对象

    def add_plugin(self, plugin_type, plugin_name, plugin_class):
        self.plugins.setdefault(plugin_type, {})[plugin_name] = plugin_class

    def get_plugin(self, plugin_type, plugin_name):
        return self.plugins.get(plugin_type, {}).get(plugin_name)

    def add_plugin_instance(self, plugin_type, plugin_name, plugin_instance):
        self.plugin_instances.setdefault(
            plugin_type, {})[plugin_name] = plugin_instance

    def get_plugin_instance(self, plugin_type, plugin_name):
        return self.plugin_instances.get(plugin_type, {}).get(plugin_name)

    def clear_plugin_instances(self):
        self.plugin_instances = {}

    def destroy_plugins(self):
        self.plugins = {}
        self.plugin_instances = {}


DefaultPluginStore = PluginStore()


class Plugin:
    def __init__(self,
                 cls,
                 plugin_type,
                 plugin_name,
                 version: str = "",
                 can_init_instance: bool = True, *args, **kwargs):
        self._cls = cls
        self.name = plugin_name
        self.type = plugin_type
        self.version = version
        self.can_init_instance = can_init_instance
        self.args = args
        self.kwargs = kwargs

    def create_instance(self):
        return self._cls(*self.args, **self.kwargs)


class PluginMeta(type):
    """插件元类 ."""
    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, PluginMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        new_class = super_new(cls, name, bases, attrs)

        for obj_name, obj in attrs.items():
            setattr(new_class, obj_name, obj)
        class_name = new_class.__name__
        # 获得插件类型
        plugin_type = getattr(new_class, "plugin_type", "")
        if not plugin_type:
            plugin_type = PluginType.CONFIG_NORMAL
            # raise PluginTypeNotFound("plugin_type not set in class %s" % class_name)
        # 获得插件名称，默认为类名
        plugin_name = getattr(new_class, "plugin_name", "")
        if not plugin_name:
            plugin_name = class_name
        # 是否忽略此插件
        register_ignore = getattr(new_class, "register_ignore", False)
        # 创建插件类
        if not register_ignore:
            # 将类包装为一个插件
            plugin = Plugin(new_class, plugin_type, plugin_name)
            DefaultPluginStore.add_plugin(plugin_type, plugin_name, plugin)
        return new_class


def register_plugin(plugin_type: PluginType,
                    plugin_name: Union[str, Enum],
                    version: str = "",
                    can_init_instance: bool = True, *args, **kwargs):
    """将类/函数注册为一个插件 ."""
    def decorator(cls):
        nonlocal plugin_name
        if not plugin_name:
            plugin_name = cls.__name__
        # 将类包装为一个插件
        plugin = Plugin(
            cls,
            plugin_type,
            plugin_name,
            version,
            can_init_instance,
            *args,
            **kwargs)
        DefaultPluginStore.add_plugin(plugin_type, plugin_name, plugin)
        return cls
    return decorator


def get_plugin(plugin_type: int, plugin_name: str):
    return DefaultPluginStore.get_plugin(plugin_type, plugin_name)


def get_plugin_instance(plugin_type: int, plugin_name: str):
    """懒加载的方式获得插件，如果没有则创建，是一个单例模式 ."""
    # 从缓存中获取插件实例
    plugin_instance = DefaultPluginStore.get_plugin_instance(
        plugin_type, plugin_name)
    if not plugin_instance:
        # 从缓存中获取插件类
        plugin = DefaultPluginStore.get_plugin(plugin_type, plugin_name)
        if not plugin:
            return None
        # 创建插件实例
        plugin_instance = plugin.create_instance()
        # 缓存插件实例
        DefaultPluginStore.add_plugin_instance(
            plugin_type, plugin_name, plugin_instance)
    return plugin_instance


def reload_global_plugin_store():
    global DefaultPluginStore
    DefaultPluginStore.clear_plugin_instances()


class PluginRegister(metaclass=PluginMeta):
    def __init__(self):
        pass


def load_default_plugins():
    reload_global_plugin_store()
    for plugin_type, plugins in DefaultPluginStore.plugins.items():
        for plugin_name, plugin_cls in plugins.items():
            if plugin_cls.can_init_instance:
                plugin_instance = plugin_cls.cls()
                DefaultPluginStore.set_instance(
                    plugin_type, plugin_name, plugin_instance)
