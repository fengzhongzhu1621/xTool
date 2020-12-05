# -*- coding: utf-8 -*-

import unittest
from xTool.decorators.utils import CallableContextManager


class A(CallableContextManager):
    def __enter__(self):
        self.value = 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.value = 2


class TestCallableContextManager(unittest.TestCase):
    def test_context(self):
        a = A()
        with a:
            assert a.value == 1
        assert a.value == 2

    def test_decorator(self):
        decorator = A()

        @decorator
        def _func():
            return 3
        actual = _func()
        assert actual == 3
        assert decorator.value == 2
