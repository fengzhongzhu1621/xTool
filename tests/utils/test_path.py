# -*- coding: utf-8 -*-

from xTool.utils.path import path_to_dotted


def test_path_to_dotted():
    actual = path_to_dotted("/usr/local/", "/")
    expect = "usr.local"
    assert actual == expect
