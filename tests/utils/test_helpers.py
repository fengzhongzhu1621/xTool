# coding: utf-8

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
	
	