import abc
from typing import Any, Union

import orjson as json
from django.core.cache import cache

from core.constants import TimeEnum
from xTool.codec import count_md5


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
            actual_key = count_md5(actual_key)

        return actual_key

    def get(self) -> Any:
        value = cache.get(self.key)
        if value is not None:
            cache_value = json.loads(value)
            return cache_value

        return

    def set(self, value: Any, timeout: Union[int, TimeEnum]) -> None:
        timeout = timeout.value if isinstance(timeout, TimeEnum) else timeout
        cache.set(self.key, json.dumps(value), timeout)


class CacheKeyTemplate(CacheKey):
    def __init__(self, key_template: str, need_md5=False, *args, **kwargs):
        self.key_template = key_template
        super().__init__(need_md5, *args, **kwargs)

    def key_template(self) -> str:
        return self.key_template
