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

    def test_enqueue(self):
        actual = self.demo.enqueue(300)
        assert actual == 0
        actual = self.demo.dequeue()
        assert actual == 300

    def test_reset_buffer(self):
        self.demo.reset_buffer()
        assert self.demo.get_buffer_data_length() == 0
