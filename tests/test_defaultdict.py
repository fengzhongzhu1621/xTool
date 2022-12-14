# -*- coding: utf-8 -*-

from collections import defaultdict


def test_default_dict():
    dict1 = defaultdict(int)
    dict2 = defaultdict(set)
    dict3 = defaultdict(str)
    dict4 = defaultdict(list)
    dict1[2] = '2'
    assert dict1[1] == 0
    assert dict2[1] == set()
    assert dict3[1] == ""
    assert dict4[1] == []
    assert dict(dict1) == {1: 0, 2: '2'}

    # 自定义函数
    def zero():
        return 1

    dict5 = defaultdict(zero)
    assert dict5["a"] == 1

    # lambda函数
    def constant_factory(value):
        return lambda: value

    dict6 = defaultdict(constant_factory('<missing>'))
    assert dict6["a"] == '<missing>'
    
    # 多个参数
    dict7 = defaultdict(lambda: "{title}{content}", {"email": "email content"})
    assert dict7[1] == '{title}{content}'
    assert dict7["email"] == "email content"
