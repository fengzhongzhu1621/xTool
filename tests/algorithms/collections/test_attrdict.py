# -*- coding: utf-8 -*-

from unittest import TestCase
from xTool.algorithms.collections.attrdict import StripDict


class TestStripDict(TestCase):
    def setUp(self) -> None:
        self.dict = StripDict({"a": 1, "b": "2 ", "c": "\t3 \n"})

    def test_dict(self):
        assert self.dict['a'] == 1
        assert self.dict['b'] == "2"
        assert self.dict['c'] == "3"
        assert self.dict.get("a") == 1
        assert self.dict.get("b") == "2"
        assert self.dict.get("c") == "3"
        assert self.dict.get("c", "default") == "3"
        assert self.dict.get("d", "default") == "default"
