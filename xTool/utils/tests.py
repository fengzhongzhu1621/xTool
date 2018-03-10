# -*- coding: utf-8 -*-

import unittest

def skipUnlessImported(module, obj):
    """如果对象不在导入的模块中，跳过被装饰的测试 .
    
    @skipUnlessImported('airflow.operators.mysql_operator', 'MySqlOperator')
    """
    import importlib
    try:
        m = importlib.import_module(module)
    except ImportError:
        m = None
    return unittest.skipUnless(
        obj in dir(m),
        "Skipping test because {} could not be imported from {}".format(
            obj, module))
