# -*- coding: utf-8 -*-

import textwrap
from typing import List, Dict, Optional, Union

from unittest import TestCase
from xTool.config.converter import DictConfigConverter
from xTool.codec.yaml_codec import YamlCodec


class TestDictConfigConverter(TestCase):
    def test_unmarshal(self):
        yaml_config = textwrap.dedent("""\
            object1:
              b: 1
              c: 2
              d:
                - d1
                - d2
              e:
                e1: 1
                e2: "2"
              f: [f1, f2]
              object2:
                a: 1
                b: 2
              object3:
                - c: 1
                  d: 2
                - c: 3
                  d: 4
        """)
        dict_config = YamlCodec.decode(yaml_config)
        assert dict_config == {
            'object1': {
                'b': 1,
                'c': 2,
                'd': [
                    'd1',
                    'd2'],
                'e': {
                    'e1': 1,
                    'e2': '2'},
                'f': ['f1', 'f2'],
                'object2': {'a': 1, 'b': 2},
                'object3': [{'c': 1, 'd': 2}, {'c': 3, 'd': 4}]

            }
        }
        converter = DictConfigConverter(dict_config)

        class Object2:
            def __init__(self, a: int = None, b: str = None):
                self.a = a
                self.b = b

            def __eq__(self, other):
                return self.a == other.a and self.b == other.b

        class Object3:
            def __init__(self, c: int = None, d: str = None):
                self.c = c
                self.d = d

            def __eq__(self, other):
                return self.c == other.c and self.d == other.d

        class Object1:
            def __init__(self,
                         a=None,
                         b: str = None,
                         c: int = None,
                         d: Optional[List] = None,
                         e: Union[None, Dict] = None,
                         object2: Object2 = None,
                         object3: List[Object3] = None):
                self.a = a
                self.b = b
                self.c = c
                self.d = d
                self.e = e
                self.object2 = object2 if object2 else {}
                self.object3 = object3 if object3 else []

            def __eq__(self, other):
                return (self.a == other.a and self.b == other.b and self.c == other.c and self.d ==
                        other.d and self.e == other.e and
                        self.object2 == other.object2 and self.object3 == other.object3)

        object1 = converter.unmarshal("object1", Object1())
        assert object1.object2 == Object2(1, '2')
        assert object1.object3 == [Object3(1, '2'), Object3(3, '4')]
        assert object1 == Object1(
            a=None,
            b='1',
            c=2,
            d=['d1', 'd2'],
            e={'e1': 1, 'e2': '2'},
            object2=Object2(1, '2'),
            object3=[Object3(1, '2'), Object3(3, '4')]
        )
