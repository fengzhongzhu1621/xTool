import abc
from typing import Any

import orjson as json
from django.core.cache import cache

from apps.core.constants import TimeEnum
from xTool.misc import md5 as md5_sum


class CacheKey(abc.ABC):
    def __init__(self, need_md5=False, *args, **kwargs):
        self.need_md5 = need_md5
        self.key = self.rend_template(*args, **kwargs)

    @property
    @abc.abstractmethod
    def key_template(self) -> str:
        raise NotImplementedError

    def rend_template(self, *args, **kwargs) -> str:
        try:
            actual_key = self.key_template.format(*args, **kwargs)
        except (IndexError, KeyError):
            actual_key = self.key_template
        if self.need_md5:
            actual_key = md5_sum(actual_key)

        return actual_key

    def get(self) -> Any:
        value = cache.get(self.key)
        if value is not None:
            cache_value = json.loads(value)
            return cache_value

        return

    def set(self, value: Any, timeout: TimeEnum) -> None:
        cache.set(self.key, json.dumps(value), timeout.value)


class CacheKeyTemplate(CacheKey):
    def __init__(self, key_template: str, need_md5=False, *args, **kwargs):
        super().__init__(need_md5, *args, **kwargs)
        self.key_template = key_template

    def key_template(self) -> str:
        return self.key_template
