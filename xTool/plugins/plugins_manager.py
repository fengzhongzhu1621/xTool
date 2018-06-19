# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import object
import imp
import inspect
import os
import re
import sys

from xTool.utils.log.logging_mixin import LoggingMixin
from xTool.utils.module_loading import make_module
from xTool.utils.module_loading import prepare_classpath


log = LoggingMixin().log


norm_pattern = re.compile(r'[/|.]')


class XToolPluginException(Exception):
    pass


class XToolBasePlugin(object):
    Name = None

    @classmethod
    def validate(cls):
        """验证插件必须定义name静态变量 ."""
        if not cls.Name:
            raise XToolPluginException("Your plugin needs a name.")


def find_plugins(plugins_folder, followlinks=True):
    """在插件目录下查询插件 ."""
    plugins = []
    for root, dirs, files in os.walk(plugins_folder, followlinks=True):
        for f in files:
            try:
                # 获得插件目录下的所有文件路径
                filepath = os.path.join(root, f)
                if not os.path.isfile(filepath):
                    continue
                # 判断文件的后缀是否是.py
                mod_name, file_ext = os.path.splitext(
                    os.path.split(filepath)[-1])
                if file_ext != '.py':
                    continue

                log.debug('Importing plugin module %s', filepath)
                # 将路径转换为命名空间
                # normalize root path as namespace
                # e.g.:
                # __data__home__user00__application__airflow__plugins_rest_api_plugin
                # mod_name 为文件名（去掉后缀）
                namespace = '_'.join([re.sub(norm_pattern, '__', root), mod_name])

                # 根据文件名加载模块
                m = imp.load_source(namespace, filepath)

                # 将所加载模块中的 XToolBasePlugin 子类添加到 plugins 列表中
                # 遍历模块的属性值
                for obj in list(m.__dict__.values()):
                    # 判断模块中的类是否为 XToolBasePlugin 的子类
                    if (
                            inspect.isclass(obj) and
                            issubclass(obj, XToolBasePlugin) and
                            obj is not XToolBasePlugin):
                        # 验证子类中是否定义了name静态变量
                        obj.validate()
                        # 将类加入到插件列表中
                        if obj not in plugins:
                            plugins.append(obj)
            except Exception as e:
                log.exception('Failed to import plugin %s' % filepath)

    return plugins


def load_plugin(plugin):
    """加载插件 ."""
    modules_list = [
        (attr, getattr(plugin, attr))
        for attr in dir(plugin)
            if attr.endswith("_MODULES") and isinstance(getattr(plugin, attr), (tuple, list))
    ]

    modules = []
    for attr, objects in modules_list:
        prefix = "xTool.%s" % attr.split('_MODULES')[0].lower()
        module_name = "%s.%s" % (prefix, plugin.Name)
        module = make_module(module_name, objects)
        sys.modules[module.__name__] = module
        modules.append(module)
    return modules

def load_plugins(plugins_folder, followlinks=True):
    prepare_classpath(plugins_folder)
    plugins = find_plugins(plugins_folder, followlinks=True)
    res = [] 
    for plugin in plugins:
        modules = load_plugin(plugin)
        res.extend(modules)
    return res