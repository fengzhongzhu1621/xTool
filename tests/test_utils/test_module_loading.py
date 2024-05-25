#coding: utf-8

import os
import sys
from inspect import isfunction

from xTool.utils import module_loading
from xTool.exceptions import XToolException

import pytest


def test_prepare_classpath():
    dir_path = "."
    module_loading.prepare_classpath(dir_path)
    dir_path = os.path.abspath(os.path.expanduser(dir_path))
    assert dir_path in sys.path


def test_make_module():
    name = 'my_module.sub_module'
    class Object1:
        def __init__(self):
            pass
        
    class Object2:
        def __init__(self):
            pass

    objects = [Object1, Object2]
    module_obj = module_loading.make_module(name, objects)
    assert module_obj.Object1().__class__.__name__ == 'Object1'
    assert module_obj._name == name.split('.')[-1]
    assert module_obj.__name__ == name
    assert module_obj._objects == objects


def test_load_backend_module_from_conf():
    section = 'section'
    key = 'key'
    default_backend = 'xTool.utils.module_loading.make_module'
    conf = None
    with pytest.raises(XToolException) as exeinfo:
        module = module_loading.load_backend_module_from_conf(section,
                                                 key,
                                                 default_backend,
                                                 conf)

    default_backend = 'xTool.utils.module_loading'
    module = module_loading.load_backend_module_from_conf(section,
                                                 key,
                                                 default_backend,
                                                 conf)
    assert module.load_backend_module_from_conf


def test_import_string():
    backend = 'xTool.utils.module_loading'
    module = module_loading.import_string(backend)
    assert module.__name__ == 'xTool.utils.module_loading'

    backend = 'xTool.utils.module_loading.make_module'
    function = module_loading.import_string(backend)
    assert isfunction(function)
    assert function.__name__ == 'make_module'
