# -*- coding: utf-8 -*-

import struct
import binascii

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

    def test_append_buffer(self):
        self.demo.reset_buffer()
        self.demo.append_buffer(b'123')
        assert self.demo.get_buffer_data_length() == 3

    def test_read_package(self):
        self.demo.reset_buffer()
        package = struct.pack('>HIIIHI', 1234, 20, 0, 0, 0, 0x12345678)
        self.demo.append_buffer(package)
        assert package.hex() == "04d2000000140000000000000000000012345678"
        assert len(package) == 20
        assert self.demo.get_buffer_data_length() == 20
        # 包体残缺包
        package_1 = struct.pack('>HIIIHI', 1234, 20, 0, 0, 0, 0x123456)
        self.demo.append_buffer(package_1)

        packages = self.demo.read_package()
        assert packages == [package, package_1]
