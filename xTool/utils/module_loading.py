# -*- coding: utf-8 -*-

from __future__ import print_function

from xTool.exceptions import XToolException
from xTool.utils.log.logging_mixin import LoggingMixin
from importlib import import_module
import imp


log = LoggingMixin().log


def make_module(name, objects):
    """动态创建模块 .

    - name: 模块名称
    - objects: 模块中需要包含的对象列表
    """
    name = name.lower()
    module = imp.new_module(name)
    module._name = name.split('.')[-1]
    module._objects = objects
    module.__dict__.update((o.__name__, o) for o in objects)
    return module


def load_backend_module_from_conf(section, key, default_backend, conf=None):
    """从配置文件中加载模块 .
    
    Args:
        section: 配置文件中的section
        key: section中的key
        default_backend: 默认后端模块配置
        conf: 配置对象

    Returns:
        返回加载的模块
    """
    module = None
    # 从配置文件中获取配置的后端模块
    if conf is None:
        backend = default_backend
    else:
        try:
            backend = conf.get(section, key)
        except conf.XToolConfigException:
            # 没有配置
            backend = default_backend

    # 加载模块，加载失败抛出异常
    try:
        module = import_module(backend)
    except ImportError as err:
        log.critical(
            "Cannot import %s for %s %s due to: %s",
            backend, section, key, err
        )
        raise XToolException(err)

    return module


def import_string(dotted_path):
    """根据点分割的字符串，加载类
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.

    Args:
        dotted_path: 字符串表示的模块类，module.class
    Returns:
        返回加载的模块中的对象
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        raise ImportError("{} doesn't look like a module path".format(dotted_path))

    module = import_module(module_path)

    try:
        # 返回模块中的类
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError('Module "{}" does not define a "{}" attribute/class'.format(
            module_path, class_name)
        )
