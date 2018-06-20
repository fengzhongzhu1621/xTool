# coding: utf-8

import subprocess
import logging
import sys

import pytest

from xTool.utils.helpers import *
from xTool.exceptions import XToolException


def test_validate_key():
    with pytest.raises(XToolException) as excinfo:
        validate_key('*')

    with pytest.raises(TypeError) as excinfo:
        validate_key({})
        
def test_alchemy_to_dict():
    pass
        
        
def test_is_in():
    class A(object):
        pass
    a = A()
    b = A()
    flag = is_in(a, [a, b])
    assert flag is True
    flag = is_in((1, 2), [(1, 2), (3, 4)])
    assert flag is False    
    

def test_is_container():
    assert is_container([1,2]) is True
    assert is_container((1,2)) is True
    assert is_container('123') is False
    
    
def test_as_tuple():
    assert as_tuple([1, 2]) == (1, 2)
    assert as_tuple(1) == (1, )
    assert as_tuple('abc') == ('abc', )
    

def test_chunks():
    items = chunks([1,2,3], 2)
    assert list(items) == [[1, 2], [3]]
    with pytest.raises(ValueError) as excinfo:
        a = chunks([1,2,3], 0)
        list(a)
    
    
def test_reduce_in_chunks():
    initializer = [0]
    iterable = [1, 2, 3]
    chunk_size = 2
    def fn(x, y):
        return x + y
    res = reduce_in_chunks(fn, iterable, initializer, chunk_size)
    assert res == [0, 1, 2, 3]
    

def test_as_flattened_list():
    iterable = (('blue', 'red'), ('green', 'yellow', 'pink'))
    actual = as_flattened_list(iterable)
    expected = ['blue', 'red', 'green', 'yellow', 'pink']
    assert actual == expected


@pytest.mark.skipif(sys.platform == 'win32', reason="requires windows")
def test_reap_process_group():
    process = subprocess.Popen("echo 1")
    pid = process.pid
    reap_process_group(pid, logging)


def test_parse_template_string():
    (template_string, template) = parse_template_string("{{1+2}}")
    assert template_string is None
    (template_string, template) = parse_template_string("1+2")
    assert template is None
    assert template_string == "1+2"


def test_tob():
    actual = tob('123')
    expected = b'123'
    assert actual == expected
    actual = tob('你好')
    expected = '你好'.encode('utf8')
    assert actual == expected


def test_tou():
    actual = tou(b'123')
    expected = '123'
    assert actual == expected
    actual = tou('你好'.encode('utf8'))
    expected = '你好'
    assert actual == expected


def test_expand_env_var():
    actual = expand_env_var("$var 123")
    expected = "$var 123"
    assert actual == expected
    os.environ['var'] =  "I'm"
    actual = expand_env_var("$var 123")
    expected = "I'm 123"
    assert actual == expected


def test_run_command():
    actual = run_command("echo 1")
    assert actual == '1' + os.linesep
    with pytest.raises(FileNotFoundError):
        actual = run_command("runerr example")
