from .exceptions import PluginTypeNotFound
from .plugin import Plugin
from .store import DefaultPluginStore


class PluginMeta(type):
    """插件元类 ."""

    def __new__(cls, name, bases, attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, PluginMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        new_class = super_new(cls, name, bases, attrs)
        # 给新类设置属性
        for obj_name, obj in attrs.items():
            setattr(new_class, obj_name, obj)
        class_name = new_class.__name__
        # 获得插件类型
        plugin_type = getattr(new_class, "plugin_type", "")
        if not plugin_type:
            raise PluginTypeNotFound("plugin_type not set in class %s" % class_name)
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
            # 将插件添加到仓库
            DefaultPluginStore.add_plugin(plugin_type, plugin_name, plugin)
        return new_class


class PluginRegister(metaclass=PluginMeta):
    def __init__(self): ...
