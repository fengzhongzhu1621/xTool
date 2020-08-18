# -*- coding: utf-8 -*-

from enum import IntEnum, unique
# from xTool.plugins.exceptions import PluginTypeNotFound


@unique
class PluginType(IntEnum):
    UNITTEST = 1

    # 默认类型
    CONFIG_NORMAL = 2

    # 配置：范围 [10 - 20]
    CONFIG_DATA_SOURCE = 10
    CONFIG_DECODER = 11


class PluginManager:
    __slots__ = ("_plugins", "_plugin_instances")

    def __init__(self):
        # 线程安全
        self._plugins = {}
        self._plugin_instances = {}

    def add_plugin(self, plugin_type, plugin_name, plugin_class):
        self._plugins.setdefault(plugin_type, {})[plugin_name] = plugin_class

    def get_plugin(self, plugin_type, plugin_name):
        return self._plugins.get(plugin_type, {}).get(plugin_name)

    def add_plugin_instance(self, plugin_type, plugin_name, plugin_instance):
        self._plugin_instances.setdefault(plugin_type, {})[plugin_name] = plugin_instance

    def get_plugin_instance(self, plugin_type, plugin_name):
        return self._plugin_instances.get(plugin_type, {}).get(plugin_name)


DefaultPluginManager = PluginManager()


class Plugin:
    def __init__(self, cls, plugin_type, plugin_name):
        self._cls = cls
        self.name = plugin_name
        self.type = plugin_type

    def create_instance(self):
        return self._cls()


class PluginMeta(type):
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
            plugin = Plugin(new_class, plugin_type, plugin_name)
            DefaultPluginManager.add_plugin(plugin_type, plugin_name, plugin)
        return new_class


def register_plugin(plugin_type, plugin_name=None):
    """将类注册为一个插件 ."""
    def decorator(cls):
        nonlocal plugin_name
        if not plugin_name:
            plugin_name = cls.__name__
        plugin = Plugin(cls, plugin_type, plugin_name)
        DefaultPluginManager.add_plugin(plugin_type, plugin_name, plugin)
        return cls
    return decorator


def get_plugin_instance(plugin_type, plugin_name):
    """懒加载的方式获得插件，如果没有则创建，是一个单例模式 ."""
    # 从缓存中获取插件实例
    plugin_instance = DefaultPluginManager.get_plugin_instance(plugin_type, plugin_name)
    if not plugin_instance:
        # 从缓存中获取插件类
        plugin = DefaultPluginManager.get_plugin(plugin_type, plugin_name)
        if not plugin:
            return None
        # 创建插件实例
        plugin_instance = plugin.create_instance()
        # 缓存插件实例
        DefaultPluginManager.add_plugin_instance(plugin_type, plugin_name, plugin_instance)
    return plugin_instance
