import unittest

from xTool import cachetools
from .mixin import CacheTestMixin


class CacheTest(unittest.TestCase, CacheTestMixin):
    Cache = cachetools.Cache

    def test_get_sizeof(self):
        cache = self.Cache(max_size=1)
        assert cache.get_size()
        assert cache.get_sizeof == self.Cache.get_sizeof
