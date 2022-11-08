# -*- coding: utf-8 -*-

from unittest import TestCase

import pytest

from xTool.algorithms.collections.attrdict import StripDict, DefaultSize


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


class TestDefaultSize:
    def test___getitem__(self):
        assert DefaultSize()[0] == 1
        assert DefaultSize()[1] == 1

    def test___setitem__(self):
        DefaultSize()[0] = 1
        DefaultSize()[1] = 1
        DefaultSize()[2] = 1
        with pytest.raises(AssertionError):
            DefaultSize()[0] = 2

    def test_pop(self):
        obj = DefaultSize()
        assert obj.pop("key1") == 1
        assert obj.pop("key2") == 1
