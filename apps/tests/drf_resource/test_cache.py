from apps.core.drf_resource.cache import CacheTypeItem


class TestCacheTypeItem:
    def test_dict(self):
        item = CacheTypeItem(key="test", timeout=60 * 5, user_related=False)
        actual = item.__dict__
        expect = {'key': 'test', 'label': '', 'timeout': 300, 'user_related': False}
        assert actual == expect
