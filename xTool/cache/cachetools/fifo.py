import collections

from .cache import Cache


class FIFOCache(Cache):
    """First In First Out (FIFO) cache implementation."""

    def __init__(self, maxsize, get_sizeof=None):
        super().__init__(maxsize, get_sizeof)
        self.__order = collections.OrderedDict()

    def __setitem__(self, key, value, cache_setitem=Cache.__setitem__):
        cache_setitem(self, key, value)
        self.__update(key)

    def __delitem__(self, key, cache_delitem=Cache.__delitem__):
        cache_delitem(self, key)
        # 缓冲区满时，删除最先缓冲的数据
        del self.__order[key]

    def popitem(self):
        """Remove and return the `(key, value)` pair first inserted."""
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
