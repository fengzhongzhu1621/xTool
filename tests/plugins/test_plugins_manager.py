#coding: utf-8

import os
import sys

from xTool.plugins.plugins_manager import *


plugins_folder = os.path.dirname(__file__)


class OperatorA(object):
    pass


class XToolTestPlugin(XToolBasePlugin):
    name = 'my_module'
    OPERATORS_MODULES = [OperatorA]


def test_load_plugins():
    operators_modules = load_plugins(plugins_folder, followlinks=True)
    from xTool.operators.my_module import OperatorA
    a = OperatorA()
