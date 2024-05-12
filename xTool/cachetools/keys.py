class HashedTuple(tuple):
    """A tuple that ensures that hash() will be called no more than once
    per element, since cache decorators will hash the key multiple
    times on a cache miss.  See also _HashedSeq in the standard
    library functools implementation.

    """

    __hash_value = None

    def __hash__(self, hash=tuple.__hash__):
        """计算元组的hash值 ."""
        hash_value = self.__hash_value
        if hash_value is None:
            self.__hash_value = hash_value = hash(self)
        return hash_value

    def __add__(self, other, add=tuple.__add__):
        """两个元组相加 ."""
        return HashedTuple(add(self, other))

    def __radd__(self, other, add=tuple.__add__):
        return HashedTuple(add(other, self))

    def __getstate__(self):
        """pickle.dumps时调用，如果 __getstate__ 与 __setstate__ 都省略,
        那么就是默认情况, 自动保存和加载对象的属性字典 __dict__，
        必须返回一个字典, 字典的内容被加载到当前的对象"""
        return {}


# used for separating keyword arguments; we do not use an object
# instance here so identity is preserved when pickling/unpickling
# 分割符，用于分割args和kwargs
_kw_mark = (HashedTuple,)


def hash_key(*args, **kwargs):
    """Return a cache key for the specified hashable arguments."""

    if kwargs:
        return HashedTuple(args + sum(sorted(kwargs.items()), _kw_mark))
    else:
        return HashedTuple(args)


def method_key(self, *args, **kwargs):
    """Return a cache key for use with cached methods."""
    return hash_key(*args, **kwargs)


def typed_key(*args, **kwargs):
    """Return a typed cache key for the specified hashable arguments."""
    # 计算参数的hash值
    key = hash_key(*args, **kwargs)
    # 添加参数的类型
    key += tuple(type(v) for v in args)
    key += tuple(type(v) for _, v in sorted(kwargs.items()))
    return key
