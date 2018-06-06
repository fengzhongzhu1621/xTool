#coding: utf-8


from xTool.patterns.singleton import Singleton
from six import with_metaclass


class C(with_metaclass(Singleton)):
    pass

def test_singleton():
    c1 = C()
    c2 = C()
    assert c1 is c2
