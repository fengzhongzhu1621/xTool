# -*- coding: utf-8 -*-

"""
对于混入类，有几点需要记住。首先是，混入类不能直接被实例化使用。
其次，混入类没有自己的状态信息，也就是说它们并没有定义 __init__() 方法，并且没有实例属性。
这也是为什么我们在上面明确定义了 __slots__ = ()
"""


class SetOnceMappingMixin:
    """
    Only allow a key to be set once.
    """
    __slots__ = ()

    def __setitem__(self, key, value):
        if key in self:
            raise KeyError(str(key) + ' already set')
        return super().__setitem__(key, value)


class StringKeysMappingMixin:
    """
    Restrict keys to strings only
    """
    __slots__ = ()

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError('keys must be strings')
        return super().__setitem__(key, value)
