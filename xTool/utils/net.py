# -*- coding: utf-8 -*-

import importlib
import socket
from xTool.configuration import (conf, XToolConfigException)


def get_hostname():
    """
    Fetch the hostname using the callable from the config or using
    `socket.getfqdn` as a fallback.
    """
    # First we attempt to fetch the callable path from the config.
    try:
        callable_path = conf.get('core', 'hostname_callable')
    except XToolConfigException:
        callable_path = None

    # Then we handle the case when the config is missing or empty. This is the
    # default behavior.
    if not callable_path:
        return socket.getfqdn()

    # Since we have a callable path, we try to import and run it next.
    # 根据配置文件中的设置的回调函数 module_path:attr_name 获取主机名
    # 加载指定模块，获得模块定义的主机属性名
    module_path, attr_name = callable_path.split(':')
    module = importlib.import_module(module_path)
    callable = getattr(module, attr_name)
    return callable()
