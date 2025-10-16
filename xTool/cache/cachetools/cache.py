from collections.abc import MutableMapping
from typing import Callable, Optional

from xTool.collections import DefaultSize


class Cache(MutableMapping):
    """Mutable mapping to serve as a simple cache or cache base class."""

    __marker = object()

    __size = DefaultSize()

    def __init__(self, maxsize: int, get_sizeof: Optional[Callable] = None) -> None:
        """
        :param maxsize: 缓冲value的字符数
        :param get_sizeof: 计算value的字符数的函数
        """
        if get_sizeof:
            self.get_sizeof = get_sizeof
        if self.get_sizeof is not Cache.get_sizeof:
            # 记录每个key的value的字符数
            self.__size = dict()
        # 需要缓冲的数据
        self.__data = dict()
        # 所有缓冲的value的字符数总和
        self.__curr_size = 0
        # 所有缓冲value的最大字符数
        self.__maxsize = maxsize

    def __repr__(self):
        return "{}({}, maxsize={!r}, curr_size={!r})".format(
            self.__class__.__name__,
            repr(self.__data),
            self.__maxsize,
            self.__curr_size,
        )

    def __getitem__(self, key):
        try:
            return self.__data[key]
        except KeyError:
            # __missing__()的主要作用就是由__getitem__在缺失 key 时调用，从而避免出现 KeyError
            return self.__missing__(key)

    def __setitem__(self, key, value):
        maxsize = self.__maxsize
        # 计算cache value的字符数
        size = self.get_sizeof(value)
        if size > maxsize:
            raise ValueError("value too large")
        if key not in self.__data or self.__size[key] < size:
            # 如果是新增的数据 或 需要更新的数据比原来要大
            while self.__curr_size + size > maxsize:
                # 如果缓冲区满，则删除字典中的最后一对键和值，预留足够的空间给需要缓冲的最新数据
                self.popitem()
        # 计算新增的value的字符数
        if key in self.__data:
            diff_size = size - self.__size[key]
        else:
            diff_size = size
        # 保存需要缓存的数据
        self.__data[key] = value
        # 记录key的value的字符数
        self.__size[key] = size
        # 记录缓冲的总字符数
        self.__curr_size += diff_size

    def __delitem__(self, key):
        size = self.__size.pop(key)
        del self.__data[key]
        self.__curr_size -= size

    def __contains__(self, key):
        return key in self.__data

    def __missing__(self, key):
        raise KeyError(key)

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def pop(self, key, default=__marker):
        if key in self:
            value = self[key]
            del self[key]
        elif default is self.__marker:
            raise KeyError(key)
        else:
            value = default
        return value

    def setdefault(self, key, default=None):
        if key in self:
            value = self[key]
        else:
            self[key] = value = default
        return value

    @property
    def maxsize(self):
        """The maximum size of the cache."""
        return self.__maxsize

    @property
    def curr_size(self):
        """The current size of the cache."""
        return self.__curr_size

    @staticmethod
    def get_sizeof(_):
        """Return the size of a cache element's value."""
        return 1

    def get_size(self):
        return self.__size
