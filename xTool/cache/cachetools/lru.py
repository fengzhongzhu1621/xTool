import collections

from .cache import Cache


class LRUCache(Cache):
    """Least Recently Used (LRU) cache implementation."""

    def __init__(self, maxsize, get_sizeof=None):
        Cache.__init__(self, maxsize, get_sizeof)
        self.__order = collections.OrderedDict()

    def __getitem__(self, key, cache_getitem=Cache.__getitem__):
        # 将使用过的数据放到队尾
        value = cache_getitem(self, key)
        if key in self:  # __missing__ may not store item
            self.__update(key)
        return value

    def __setitem__(self, key, value, cache_setitem=Cache.__setitem__):
        # 将需要缓冲的数据放到队尾
        cache_setitem(self, key, value)
        self.__update(key)

    def __delitem__(self, key, cache_delitem=Cache.__delitem__):
        cache_delitem(self, key)
        # 缓冲区满时，删除最先缓冲和最少使用的数据
        del self.__order[key]

    def popitem(self):
        """Remove and return the `(key, value)` pair least recently used."""
        try:
            # 从队列头取key
            key = next(iter(self.__order))
        except StopIteration:
            raise KeyError("%s is empty" % type(self).__name__) from None
        else:
            return key, self.pop(key)

    def __update(self, key):
        try:
            # 将key移到队列的尾部，会在缓冲区满时有限被替换
            self.__order.move_to_end(key)
        except KeyError:
            self.__order[key] = None
