# -*- coding: utf-8 -*-

from typing import Callable
from .plugin import Plugin
from .store import DefaultPluginStore


def register_plugin(
    plugin_type: str,
    plugin_name: str,
    version: str = "",
    can_init_instance: bool = True,
    *args,
    **kwargs
):
    """将类/函数注册为一个插件 ."""

    def wrapper(obj: Callable) -> Callable:
        nonlocal plugin_name
        if not plugin_name:
            plugin_name = obj.__name__
        # 将类/函数包装为一个插件
        plugin = Plugin(
            obj, plugin_type, plugin_name, version, can_init_instance, *args, **kwargs
        )
        # 将插件添加到仓库
        DefaultPluginStore.add_plugin(plugin_type, plugin_name, plugin)
        return obj

    return wrapper


def get_plugin(plugin_type: str, plugin_name: str):
    """从仓库中获取插件 ."""
    return DefaultPluginStore.get_plugin(plugin_type, plugin_name)


def register_plugin_instance(plugin_type: str, plugin_name: str, plugin_instance: Plugin):
    DefaultPluginStore.add_plugin_instance(plugin_type, plugin_name, plugin_instance)


def get_plugin_instance(plugin_type: str, plugin_name: str):
    """懒加载的方式获得插件，如果没有则创建，是一个单例模式 ."""
    # 从缓存中获取插件实例
    plugin_instance = DefaultPluginStore.get_plugin_instance(plugin_type, plugin_name)
    if not plugin_instance:
        # 从缓存中获取插件类
        plugin = get_plugin(plugin_type, plugin_name)
        if not plugin:
            return None
        # 创建插件实例
        plugin_instance = plugin.create_instance()
        # 缓存插件实例
        DefaultPluginStore.add_plugin_instance(
            plugin_type, plugin_name, plugin_instance
        )
    return plugin_instance


def load_plugins():
    # 遍历所有插件类型
    for plugin_type, plugins in DefaultPluginStore.get_all_plugin().items():
        # 遍历所有的插件类
        for plugin_name, plugin_cls in plugins.items():
            # 判断插件类是否可以实例化
            if plugin_cls.can_init_instance:
                # 创建插件实例
                plugin_instance = plugin_cls.cls()
                # 缓冲插件实例
                register_plugin_instance(plugin_type, plugin_name, plugin_instance)
