# -*- coding: utf-8 -*-

from unittest import TestCase
from xTool.cython.example import CythonDemo


class TestCythonDemo(TestCase):
    def test_action_strcpy(self):
        demo = CythonDemo()
        actual = demo.action_strcpy()
        assert actual == "abc"
