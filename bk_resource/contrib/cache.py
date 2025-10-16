import abc

from bk_resource.base import Resource
from bk_resource.utils.cache import CacheTypeItem, using_cache


class CacheResource(Resource, metaclass=abc.ABCMeta):
    """
    支持缓存的resource
    """

    # 缓存类型
    cache_type = None
    # 后台缓存时间
    backend_cache_type = None
    # 缓存是否与用户关联，默认关联
    cache_user_related: bool = None
    # 是否使用压缩
    cache_compress = True

    def __init__(self, *args, **kwargs):
        # 若cache_type为None则视为关闭缓存功能
        if self._need_cache_wrap():
            self._wrap_request()
        super().__init__(*args, **kwargs)

    def _need_cache_wrap(self):
        need_cache = False
        if self.cache_type is not None:
            if not isinstance(self.cache_type, CacheTypeItem):
                raise TypeError("param 'cache_type' must be an" "instance of <utils.cache.CacheTypeItem>")
            need_cache = True
        if self.backend_cache_type is not None:
            if not isinstance(self.backend_cache_type, CacheTypeItem):
                raise TypeError("param 'cache_type' must be an" "instance of <utils.cache.CacheTypeItem>")
            need_cache = True
        return need_cache

    def _wrap_request(self):
        """
        将原有的request方法替换为支持缓存的request方法
        """

        def func_key_generator(resource):
            key = "{}.{}".format(
                resource.__self__.__class__.__module__,
                resource.__self__.__class__.__name__,
            )
            return key

        self.request = using_cache(
            cache_type=self.cache_type,
            backend_cache_type=self.backend_cache_type,
            user_related=self.cache_user_related,
            compress=self.cache_compress,
            is_cache_func=self.cache_write_trigger,
            func_key_generator=func_key_generator,
        )(self.request)

    def cache_write_trigger(self, res):
        """
        缓存写入触发条件
        """
        return True
