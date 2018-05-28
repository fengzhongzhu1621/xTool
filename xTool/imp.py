#coding: utf-8

from __future__ import print_function

from xTool.exceptions import XToolException
from xTool import configuration as conf
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


def load_backend_module_from_conf(backend, section, key):
    """从配置文件中加载模块 ."""
    module = None
    # 从配置文件中获取配置的后端模块
    try:
        backend = conf.get(section, key)
    except conf.XToolConfigException:
        # 没有配置
        pass

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
