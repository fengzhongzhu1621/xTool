# -*- coding: utf-8 -*-

from unittest import TestCase
from xTool.cython.example import CythonDemo


class TestCythonDemo(TestCase):
    def setUp(self) -> None:
        self.demo = CythonDemo()

    def test_strcpy(self):
        actual = self.demo.strcpy()
        assert actual == "abc"

    def test_get_queue_size(self):
        actual = self.demo.get_queue_size()
        assert actual == 2
