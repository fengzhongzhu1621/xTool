# -*- coding: utf-8 -*-

from xTool.codec.yaml_codec import YamlCodec


class TestYamlCodec:
    def test_encode(self):
        value = """
none: [~, null]
bool: [true, false, on, off]
int: 42
float: 3.14159
list: [LITE, RES_ACID, SUS_DEXT]
dict: {hp: 13, sp: 5}
"""
        actual = YamlCodec.decode(value)
        expect = {
            'none': [None, None],
            'bool': [True, False, True, False],
            'int': 42,
            'float': 3.14159,
            'list': ['LITE', 'RES_ACID', 'SUS_DEXT'],
            'dict': {'hp': 13, 'sp': 5}}
        assert actual == expect

        actual = YamlCodec.encode(expect)
        expect = """bool:
- true
- false
- true
- false
dict:
  hp: 13
  sp: 5
float: 3.14159
int: 42
list:
- LITE
- RES_ACID
- SUS_DEXT
none:
- null
- null
"""
        assert actual == expect
