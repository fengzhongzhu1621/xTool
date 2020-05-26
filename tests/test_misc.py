#coding: utf-8

from __future__ import unicode_literals

import os
from datetime import timedelta
import subprocess

import pytest

from xTool import misc


def test_get_encodings():
    items = misc.get_encodings()
    items = list(items)
    assert 'utf8' in items


def test_exceptionToString():
    try:
        1 / 0
    except Exception:
        value = misc.exceptionToString()
        assert "ZeroDivisionError" in value


def test_get_cur_info():
    actual = misc.get_cur_info()
    value = ('test_get_cur_info', 35)
    assert value[0] == actual[0]


def test_runCommand():
    misc.runCommand("echo 1")


def test_getRunCommandResult():
    actual = misc.getRunCommandResult("echo 1")
    expect = (0, b'1' + misc.tob(os.linesep), b'')
    assert actual == expect


def test_listData():
    rows = [{
        'key': 'abc',
        'value': 'def',
    }]
    key = 'key'
    value = 'value'
    actual = misc.listData(rows, key, value)
    expect = {u'abc': u'def'}
    assert expect == actual


def test_isMemoryAvailable():
    actual = misc.isMemoryAvailable(limit=1)
    assert actual is False
    actual = misc.isMemoryAvailable(limit=100)
    assert actual is True


def test_isDiskAvailable():
    actual = misc.isDiskAvailable(".", limit=1)
    assert actual is False
    actual = misc.isDiskAvailable(".", limit=100)
    assert actual is True


def test_format_row():
    row = " a  b \t c "
    actual = misc.format_row(row)
    expect = ['a', 'b', 'c']
    assert actual == expect
    row = ""
    actual = misc.format_row(row)
    assert actual == []


def test_get_col_count():
    row = " a  b \t c "
    actual = misc.get_col_count(row)
    assert actual == 3
    row = ""
    actual = misc.get_col_count(row)
    assert actual == 0


def test_get_file_rowcol_count():
    dirname = os.path.dirname(__name__)
    filePath = os.path.abspath(os.path.join(dirname, "tests/data/a.txt"))
    (row, col) = misc.get_file_rowcol_count(filePath)
    assert row == 2
    assert col == 3


def test_get_file_row():
    dirname = os.path.dirname(__name__)
    filePath = os.path.abspath(os.path.join(dirname, "tests/data/a.txt"))
    row = misc.get_file_row(filePath)
    assert row == 2


def test_grouper():
    n = 3
    iterable = 'abcdefg'
    actual = misc.grouper(n, iterable, padvalue=None)
    expect = [('a', 'b', 'c'), ('d', 'e', 'f'), ('g', None, None)]
    assert list(actual) == expect
    actual = misc.grouper(n, iterable, padvalue='x')
    expect = [('a', 'b', 'c'), ('d', 'e', 'f'), ('g', 'x', 'x')]
    assert list(actual) == expect


def test_chunks():
    n = 3
    iterable = 'abcdefg'
    actual = misc.chunks(iterable, n)
    assert list(actual) == [u'abc', u'def', u'g']


def test_chunked():
    n = 3
    iterable = 'abcdefg'
    actual = misc.chunked(iterable, n)
    assert list(actual) == [['a', 'b', 'c'], ['d', 'e', 'f'], ['g']]


def test_get_random_string():
    actual = misc.get_random_string(length=13)
    assert len(actual) == 13
    actual = misc.get_random_string(length=0)
    assert actual == ''


def test_strict_bool():
    with pytest.raises(ValueError):
        misc.strict_bool(True)
    with pytest.raises(ValueError):
        misc.strict_bool(False)
    with pytest.raises(ValueError):
        misc.strict_bool(None)
    with pytest.raises(ValueError):
        misc.strict_bool("None")
    assert misc.strict_bool("True") is True
    assert misc.strict_bool("False") is False
    with pytest.raises(ValueError):
        misc.strict_bool("true") is True
    with pytest.raises(ValueError):
        misc.strict_bool("false") is True


def test_less_strict_bool():
    with pytest.raises(ValueError):
        misc.less_strict_bool('abc')
    with pytest.raises(ValueError):
        misc.less_strict_bool("true") is True
    with pytest.raises(ValueError):
        misc.less_strict_bool("false") is True
    with pytest.raises(ValueError):
        misc.less_strict_bool("None")
    assert misc.less_strict_bool("True") is True
    assert misc.less_strict_bool("False") is False
    assert misc.less_strict_bool(True) is True
    assert misc.less_strict_bool(False) is False
    assert misc.less_strict_bool(None) is False


def test_properties():
    class Foo():
        def __init__(self):
            self.var = 1

        @property
        def prop(self):
            return self.var + 1

        def meth(self):
            return self.var + 2
    foo = Foo()
    actual = misc.properties(foo)
    expect = {'var': 1, 'prop': 2, 'meth': foo.meth}
    assert actual == expect


def test_get_first_duplicate():
    expect = 2
    actual = misc.get_first_duplicate([1, 2, 2, 3])
    assert actual == expect


def test_many_to_one():
    expect = {'a': 1, 'b': 1, 'c': 2, 'd': 2}
    actual = misc.many_to_one({'ab': 1, ('c', 'd'): 2})
    assert actual == expect


def test_quote():
    actual = misc.quote(",", ["a", "b"])
    assert actual == "a,b"
    actual = misc.quote([",", ";"], ["a", "b"])
    assert actual == "a,b.a;b"


def test_make_snake_case():
    actual = misc.make_snake_case("API_Response")
    assert actual == "api_response"
    actual = misc.make_snake_case("APIResponse")
    assert actual == "api_response"
    actual = misc.make_snake_case("APIResponseFactory")
    assert actual == "api_response_factory"
