# -*- coding: utf-8 -*-

import pytest
from xTool import compat


def test_flatten_list_bytes():
    list_of_data = ['a', 'b', 'c']
    with pytest.raises(TypeError):
        compat.flatten_list_bytes(list_of_data)

    list_of_data = [b'a', b'b', b'c']
    actual = compat.flatten_list_bytes(list_of_data)
    assert actual == b'abc'

    list_of_data = [bytearray('abc', encoding='utf-8'), bytearray('def', encoding='utf-8')]
    actual = compat.flatten_list_bytes(list_of_data)
    assert actual == b'abcdef'
