#coding: utf-8

from __future__ import unicode_literals

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
        1/0
    except Exception:
        value = misc.exceptionToString()
        assert "ZeroDivisionError" in value


def test_ustr():
    value = "你好"
    value2 = misc.ustr(value)
    assert value == value2
    value3 = misc.ustr(value.encode('utf8'))
    assert value == value3
    value4 = misc.ustr('abc')
    assert 'abc' == value4


def test_get_cur_info():
    actual = misc.get_cur_info()
    value = ('test_get_cur_info', 35)
    assert value[0] == actual[0]


def test_runCommand():
    misc.runCommand("echo 1")


def test_getRunCommandResult():
    actual = misc.getRunCommandResult("echo 1")
    expect = (0, '1\r\n', '')
    assert actual == expect


def test_collect_process_output():
    command = "echo 1"
    process = subprocess.Popen(command,
            shell=True,
            close_fds=False if misc.USE_WINDOWS else False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    actual = misc.collect_process_output(process)
    expect = {'stderr': '', 'stdout': '1\r\n'}
    assert actual == expect


def test_dumpGarbage():
    misc.dumpGarbage()


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


def test_ustr2unicode():
    value = "%u67E5%u8BE2%u5DE5%u4F1A%u4FE1%u606F%u63A5%u53E3"
    actual = misc.ustr2unicode(value, sep='%')
    expect = "查询工会信息接口"
    assert actual == expect
    value = "\\u67E5\\u8BE2\\u5DE5\\u4F1A\\u4FE1\\u606F\\u63A5\\u53E3"
    actual = misc.ustr2unicode(value, sep='\\')
    expect = "查询工会信息接口"
    assert actual == expect


def test_format_time():
    a = timedelta(minutes=10)
    seconds = a.total_seconds()
    actual = misc.format_time(seconds)
    expect = "0:10:00"
    assert actual == expect


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
