#coding: utf-8

from xTool.func import catch
from math import log10


def test_catch():
    ret = catch(log10)(100)
    assert isinstance(ret, catch.ReturnValue) is True
    assert ret.value == 2.0

    ret = catch(log10)(-100)
    assert isinstance(ret, catch.ReturnValue) is False
    assert isinstance(ret, ValueError) is True
